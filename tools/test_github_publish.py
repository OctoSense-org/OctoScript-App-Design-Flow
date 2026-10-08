"""Publishing setup preserves developer files and sealed release bytes."""
import argparse
import contextlib
import importlib.machinery
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
loader = importlib.machinery.SourceFileLoader('publisher_octo', str(HERE / 'octo'))
spec = importlib.util.spec_from_loader(loader.name, loader)
octo = importlib.util.module_from_spec(spec)
loader.exec_module(octo)


class PublishingSetup(unittest.TestCase):
    def app(self, root, integrity=None):
        app = Path(root) / 'app'
        (app / 'bundle').mkdir(parents=True)
        (app / 'bundle/manifest.json').write_text(json.dumps({
            'id': 'dev.example.quicknotes', 'version': '0.1.0',
            'integrity': integrity or {'bundle_blake3': 'development'},
        }))
        return app

    def test_installer_is_idempotent_and_does_not_publish(self):
        with tempfile.TemporaryDirectory() as temp:
            app = self.app(temp)
            args = argparse.Namespace(dir=str(app), replace=False)
            with patch.object(octo, 'publisher_workflow', return_value='name: fixture\n'), \
                    patch.object(octo.subprocess, 'run') as external, \
                    contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(octo.cmd_publish_github(args), 0)
                workflow = app / '.github/workflows/publish-app.yml'
                before = workflow.stat().st_mtime_ns
                self.assertEqual(octo.cmd_publish_github(args), 0)
                self.assertEqual(workflow.stat().st_mtime_ns, before)
                external.assert_not_called()

    def test_custom_workflow_needs_explicit_replacement(self):
        with tempfile.TemporaryDirectory() as temp:
            app = self.app(temp)
            octo.install_publisher_workflow(app, 'name: custom\n')
            with self.assertRaises(ValueError):
                octo.install_publisher_workflow(app, 'name: new\n')
            workflow = app / '.github/workflows/publish-app.yml'
            self.assertEqual(workflow.read_text(), 'name: custom\n')
            self.assertTrue(octo.install_publisher_workflow(app, 'name: new\n', True))
            self.assertEqual(workflow.read_text(), 'name: new\n')

    def test_symlinks_cannot_redirect_workflow_writes(self):
        for component in ('.github', '.github/workflows', '.github/workflows/publish-app.yml'):
            with self.subTest(component=component), tempfile.TemporaryDirectory() as temp:
                app = self.app(temp)
                outside = Path(temp) / 'outside'
                outside.mkdir()
                target = app / component
                target.parent.mkdir(parents=True, exist_ok=True)
                try:
                    target.symlink_to(outside, target_is_directory=True)
                except OSError as error:
                    self.skipTest('Symlink creation unavailable: ' + str(error))
                with self.assertRaises(ValueError):
                    octo.install_publisher_workflow(app, 'name: fixture\n', True)
                self.assertEqual(list(outside.iterdir()), [])

    def test_sealed_bundle_is_not_used_as_editable_repository(self):
        with tempfile.TemporaryDirectory() as temp:
            app = self.app(temp, {'github': {'attestation': {'fixture': True}}})
            with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                octo.cmd_publish_github(argparse.Namespace(dir=str(app), replace=False))
            self.assertFalse((app / '.github').exists())

    def test_github_metadata_never_gets_restamped_or_unsigned_escape(self):
        for github in ({'attestation': {'fixture': True}}, {}, None):
            with self.subTest(github=github), tempfile.TemporaryDirectory() as temp:
                app = self.app(temp, {'github': github})
                bundle = app / 'bundle'
                original = (bundle / 'manifest.json').read_bytes()
                args = argparse.Namespace(bundle=str(bundle), catalog=None, publisher_key=[])
                with patch.object(octo, 'need', return_value=Path('/fixture/hub')), \
                        patch.object(octo.subprocess, 'run') as run, \
                        contextlib.redirect_stdout(io.StringIO()):
                    run.return_value.returncode = 1
                    self.assertEqual(octo.cmd_check(args, []), 1)
                    self.assertEqual(run.call_count, 1)
                    self.assertEqual(run.call_args.args[0], ['/fixture/hub', 'check', str(bundle.resolve())])
                self.assertEqual((bundle / 'manifest.json').read_bytes(), original)

    def test_run_refuses_sealed_releases_before_startup_or_file_writes(self):
        for integrity in ({'github': {}}, {'github': None}, {'signature': 'legacy-signed'}, {'signature': {}}):
            with self.subTest(integrity=integrity), tempfile.TemporaryDirectory() as temp:
                app = self.app(temp, integrity)
                bundle = app / 'bundle'
                original = (bundle / 'manifest.json').read_bytes()
                args = argparse.Namespace(bundle=str(bundle))
                with patch.object(octo, 'need') as binary, \
                        patch.object(octo.subprocess, 'Popen') as start, \
                        patch.object(octo, 'port_owner') as port, \
                        contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                    octo.cmd_run(args)
                binary.assert_not_called()
                start.assert_not_called()
                port.assert_not_called()
                self.assertFalse((app / '.local-state').exists())
                self.assertEqual((bundle / 'manifest.json').read_bytes(), original)

    def test_typed_unsigned_null_signature_remains_authorable(self):
        with tempfile.TemporaryDirectory() as temp:
            app = self.app(temp, {'signature': None})
            args = argparse.Namespace(bundle=str(app / 'bundle'))
            with patch.object(octo, 'need', side_effect=RuntimeError('authoring path reached')) as binary:
                with self.assertRaisesRegex(RuntimeError, 'authoring path reached'):
                    octo.cmd_run(args)
                binary.assert_called_once_with('card-host', 'OCTO_CARD_HOST')
            args.catalog, args.publisher_key = None, []
            with patch.object(octo, 'need', return_value=Path('/fixture/hub')), \
                    patch.object(octo.subprocess, 'run') as run, \
                    contextlib.redirect_stdout(io.StringIO()):
                run.return_value.returncode = 0
                self.assertEqual(octo.cmd_check(args, []), 0)
                self.assertEqual(run.call_count, 2)
                self.assertEqual(run.call_args_list[0].args[0][1], 'stamp')
                self.assertIn('--allow-unsigned', run.call_args_list[1].args[0])

    def test_toolchain_ref_cannot_be_mutable_or_inject_workflow(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / 'tools').mkdir()
            (root / 'tools/publish-app.template.yml').write_text('ref: __HUB_REVISION__\n')
            config = root / 'tools/publisher-toolchain.json'
            with patch.object(octo, 'REPO', root):
                for ref in (None, 'main', 'v1.8.0', 'a' * 40 + '\nrun: bad'):
                    config.write_text(json.dumps({'schema': 1, 'repository': 'OctoSense-org/OctoSense-App-Hub', 'revision': ref}))
                    with self.assertRaises(ValueError):
                        octo.publisher_workflow()
                config.write_text(json.dumps({'schema': 1, 'repository': 'OctoSense-org/OctoSense-App-Hub', 'revision': 'a' * 40}))
                self.assertEqual(octo.publisher_workflow(), 'ref: ' + 'a' * 40 + '\n')


if __name__ == '__main__':
    unittest.main()
