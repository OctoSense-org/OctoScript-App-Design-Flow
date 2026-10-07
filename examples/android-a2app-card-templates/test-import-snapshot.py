#!/usr/bin/env python3
"""Local provenance regressions; fixtures are plain test bytes, never app designs."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('snapshot', Path(__file__).with_name('import-snapshot.py'))
snapshot = importlib.util.module_from_spec(spec)
spec.loader.exec_module(snapshot)


class SnapshotTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.archive = self.root / 'archive'
        self.base = self.archive / 'collection'
        self.source = self.root / 'frozen'
        self.turn = self.root / 'deepseek-11-continuation'
        self.turn.mkdir()
        calls = []
        for index, name in enumerate(sorted(snapshot.EXPECTED)):
            content = json.dumps({'integrity': {'bundle_blake3': '0' * 64}}) if name.endswith('manifest.json') else f'fixture {index}: before\n'
            for folder in (self.base, self.source):
                path = folder / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content)
            calls.append(dict(turn='base', tool_call_id=str(index), name='write_file',
                              arguments={'path': name, 'content': content}, input_complete=True, success=True))
        snapshot.write_json(self.base / 'model-mutations.json', {'calls': calls})
        self.receipt(self.base)
        self.changed = 'card-templates/mail/glance.card'
        path = self.source / self.changed
        path.write_text(path.read_text().replace('before', 'after'))
        self.receipt(self.source)
        self.call = dict(tool_call_id='next', name='edit_file', input_complete=True, success=True,
                         arguments={'path': self.changed, 'old_string': 'before', 'new_string': 'after'},
                         output='unrelated output must never be copied')
        self.transcript()

    def receipt(self, folder):
        snapshot.write_json(folder / 'source-receipt.json', [
            dict(path=name, bytes=(folder / name).stat().st_size, sha256=snapshot.sha(folder / name))
            for name in sorted(snapshot.EXPECTED) if (folder / name).exists()])

    def transcript(self):
        snapshot.write_json(self.turn / 'transcript.json', {'tool_calls': [self.call],
                            'assistant_finals': ['not archived'], 'turn_errors': [], 'reasoning': 'not archived'})

    def run_import(self, dry_run=True):
        return snapshot.import_snapshot(self.source, Path('collection'), [self.turn],
                                        'deepseek', 11, self.archive, dry_run)

    def test_continued_edit_preserves_bytes_and_excludes_outputs(self):
        self.assertEqual(self.run_import()['mode'], 'validated_only')
        destination = self.archive / 'continuations/deepseek/turn-11'
        self.assertFalse(destination.exists())
        self.run_import(False)
        for name in snapshot.EXPECTED:
            self.assertEqual((self.source / name).read_bytes(), (destination / name).read_bytes())
        self.assertNotIn('unrelated output', (destination / 'model-mutations.json').read_text())
        self.assertEqual(snapshot.read_json(destination / 'generation-record.json')['status'],
                         'source_replayed_native_and_visual_review_pending')
        with self.assertRaises(FileExistsError):
            self.run_import(False)

    def test_interruption_is_preserved_without_claiming_completed_turn(self):
        transcript = snapshot.read_json(self.turn / 'transcript.json')
        transcript['assistant_finals'] = []
        snapshot.write_json(self.turn / 'transcript.json', transcript)
        receipt = self.turn / 'operator-interruption.json'
        snapshot.write_json(receipt, {'operator_interrupted': True, 'timestamp_utc': '2026-10-03T00:00:00Z',
                            'reason': 'Operator ends fixture run', 'method': 'Stop isolated test package',
                            'recorded_tool_calls': 1, 'assistant_finals': 0})
        self.run_import(False)
        destination = self.archive / 'continuations/deepseek/turn-11'
        record = snapshot.read_json(destination / 'generation-record.json')['new_turns'][0]
        self.assertEqual(record['completion'], 'operator_interrupted')
        self.assertEqual(record['assistant_finals'], 0)
        self.assertEqual((destination / record['operator_interruption']).read_bytes(), receipt.read_bytes())

    def test_interruption_count_mismatch_is_rejected(self):
        snapshot.write_json(self.turn / 'operator-interruption.json',
                            {'operator_interrupted': True, 'recorded_tool_calls': 42, 'assistant_finals': 0})
        with self.assertRaisesRegex(ValueError, 'counts must match'):
            self.run_import()

    def test_cross_model_base_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'same model'):
            snapshot.import_snapshot(self.source, Path('collection'), [self.turn],
                                     'minimax', 11, self.archive)

    def test_failed_edit_cannot_explain_new_source(self):
        self.call['success'] = False
        self.transcript()
        with self.assertRaisesRegex(ValueError, 'does not exactly reproduce'):
            self.run_import()

    def test_failed_patch_cannot_explain_new_source(self):
        original = (self.base / self.changed).read_text().rstrip('\n')
        self.call.update(name='apply_patch', success=False, arguments={'patch':
            '*** Begin Patch\n*** Update File: ' + self.changed + '\n@@\n-' + original
            + '\n+' + original.replace('before', 'after') + '\n*** End Patch'})
        self.transcript()
        with self.assertRaisesRegex(ValueError, 'does not exactly reproduce'):
            self.run_import()

    def test_incomplete_recorded_arguments_are_rejected(self):
        self.call['input_complete'] = False
        self.transcript()
        with self.assertRaisesRegex(ValueError, 'arguments must be complete'):
            self.run_import()

    def test_ambiguous_edit_is_not_guessed(self):
        self.call['arguments']['old_string'] = 'e'
        self.transcript()
        with self.assertRaisesRegex(ValueError, 'does not exactly reproduce'):
            self.run_import()

    def test_incomplete_collection_is_not_imported(self):
        (self.source / self.changed).unlink()
        self.receipt(self.source)
        with self.assertRaisesRegex(ValueError, '25 expected'):
            self.run_import()

    def test_receipt_tampering_is_rejected(self):
        (self.source / self.changed).write_text('different bytes')
        with self.assertRaisesRegex(ValueError, 'differ from source receipt'):
            self.run_import()

    def test_symlink_and_traversal_are_rejected(self):
        path = self.source / self.changed
        path.unlink()
        path.symlink_to(self.base / self.changed)
        with self.assertRaisesRegex(ValueError, 'symlinks'):
            self.run_import()
        with self.assertRaisesRegex(ValueError, 'inside the archive root'):
            snapshot.authorship.validate(self.archive, [Path('../frozen')])

    def test_same_leaf_cases_do_not_overwrite_results(self):
        self.run_import(False)
        other = self.archive / 'continuations/minimax/turn-11'
        snapshot.shutil.copytree(self.archive / 'continuations/deepseek/turn-11', other)
        cases = [Path(f'continuations/{model}/turn-11') for model in ('deepseek', 'minimax')]
        result = snapshot.authorship.validate(self.archive, cases)
        self.assertEqual(set(result['cases']), {str(case) for case in cases})
        self.assertEqual(sum(len(rows) for rows in result['cases'].values()), 50)


class ExactPatchTests(unittest.TestCase):
    path = 'card-templates/calendar/bundle/main.splash'

    def patch(self, body, path=None):
        return '*** Begin Patch\n*** Update File: ' + (path or self.path) + '\n' + body + '\n*** End Patch'

    def apply(self, content, body):
        return snapshot.authorship.apply_exact_patch(content, self.patch(body), self.path)

    def test_multiple_hunks_preserve_unicode_whitespace_and_newline(self):
        original = 'let name = "旧"\n  keep\nlast\n'
        body = '@@\n-let name = "旧"\n+let name = "新"\n   keep\n@@\n last\n+tail'
        self.assertEqual(self.apply(original, body), 'let name = "新"\n  keep\nlast\ntail\n')

    def test_repeated_context_uses_pinned_first_forward_match(self):
        self.assertEqual(self.apply('same\nsame\n', '@@\n-same\n+new'), 'new\nsame\n')

    def test_hunks_continue_forward_after_first_match(self):
        original = 'same\nanchor\nsame\n'
        body = '@@\n-same\n+changed\n@@\n-anchor\n+anchored'
        self.assertEqual(self.apply(original, body), 'changed\nanchored\nsame\n')

    def test_multiple_possible_sequences_do_not_override_first_choice(self):
        original = 'same\nanchor\nsame\nanchor\n'
        self.assertEqual(self.apply(original, '@@\n-same\n+changed\n@@\n-anchor\n+anchored'),
                         'changed\nanchored\nsame\nanchor\n')

    def test_earlier_runtime_trim_match_blocks_later_exact_solution(self):
        with self.assertRaisesRegex(ValueError, 'pinned first-forward'):
            self.apply('old  \nold\n', '@@\n-old\n+new')

    def test_context_only_hunk_advances_cursor(self):
        self.assertEqual(self.apply('}\nfn target(){\nbody\n}\n}\n',
                         '@@\n fn target(){\n@@\n }\n+added'),
                         '}\nfn target(){\nbody\n}\nadded\n}\n')

    def test_hunk_limit_refuses_unbounded_replay(self):
        patch = self.patch('\n'.join(['@@\n-old\n+new'] * 129))
        with self.assertRaisesRegex(ValueError, 'hunk limit'):
            snapshot.authorship.apply_exact_patch('old\n', patch, self.path)

    def test_later_validation_failure_returns_no_partial_result(self):
        source = 'old\n'
        with self.assertRaisesRegex(ValueError, 'missing'):
            self.apply(source, '@@\n-old\n+new\n@@\n-missing\n+added')
        self.assertEqual(source, 'old\n')

    def test_remove_only_line_preserves_kernel_final_newline(self):
        self.assertEqual(self.apply('old\n', '@@\n-old'), '\n')

    def test_whitespace_mismatch_is_not_fuzzy(self):
        with self.assertRaisesRegex(ValueError, 'missing'):
            self.apply('  old\n', '@@\n-old\n+new')

    def test_unanchored_insert_and_extended_headers_rejected(self):
        for body in ('@@\n+new', '@@ context\n-old\n+new', '@@\n-old\n+new\n*** End of File'):
            with self.subTest(body=body), self.assertRaises(ValueError):
                self.apply('old\n', body)

    def test_no_crlf_or_missing_final_newline_normalization(self):
        for content in ('old', 'old\r\n'):
            with self.subTest(content=content), self.assertRaises(ValueError):
                self.apply(content, '@@\n-old\n+new')

    def test_unsafe_paths_and_unsupported_operations_rejected(self):
        for path in ('../outside', '/absolute', 'card-templates/../outside', 'card-templates//bad'):
            with self.subTest(path=path), self.assertRaises(ValueError):
                snapshot.authorship.parse_exact_patch(self.patch('@@\n-old\n+new', path))
        for command in ('Add File', 'Delete File', 'Move to'):
            patch = '*** Begin Patch\n*** ' + command + ': ' + self.path + '\n+new\n*** End Patch'
            with self.subTest(command=command), self.assertRaises(ValueError):
                snapshot.authorship.parse_exact_patch(patch)

    def test_out_of_order_hunks_rejected(self):
        with self.assertRaisesRegex(ValueError, 'out-of-order'):
            self.apply('first\nsecond\n', '@@\n-second\n+changed\n@@\n-first\n+changed-first')

    def test_import_replays_patch_without_synthetic_write(self):
        fixture = SnapshotTests()
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        original = (fixture.base / fixture.changed).read_text().rstrip('\n')
        patch = self.patch('@@\n-' + original + '\n+' + original.replace('before', 'after'), fixture.changed)
        fixture.call.update(name='apply_patch', arguments={'patch': patch})
        fixture.transcript()
        fixture.run_import(False)
        archived = snapshot.read_json(fixture.archive / 'continuations/deepseek/turn-11/model-mutations.json')['calls'][-1]
        self.assertEqual(archived['name'], 'apply_patch')
        self.assertEqual(archived['arguments']['patch'], patch)


if __name__ == '__main__':
    unittest.main()
