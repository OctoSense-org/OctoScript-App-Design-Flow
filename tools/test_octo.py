"""Onboarding regressions; no model, native window or external credentials."""
import argparse
import contextlib
import importlib.machinery
import importlib.util
import io
import json
import os
from pathlib import Path
import re
import tempfile
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
loader = importlib.machinery.SourceFileLoader('octo_cli', str(HERE / 'octo'))
spec = importlib.util.spec_from_loader(loader.name, loader)
octo = importlib.util.module_from_spec(spec)
loader.exec_module(octo)


class Onboarding(unittest.TestCase):
    def create(self, dest, app_id='com.example.quicknotes', platforms=('macos',), system=False):
        args = argparse.Namespace(dir=str(dest), id=app_id, name='Test Notes', platform=platforms, system=system)
        with patch.object(octo, 'find_binary', return_value=(None, None, [])), contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            return octo.cmd_new(args)

    def test_platform_must_be_explicit_and_known(self):
        for args in (['new', '/unused'], ['new', '/unused', '--platform', 'madeup']):
            with patch('sys.argv', ['octo'] + args), contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as error:
                octo.main()
            self.assertEqual(error.exception.code, 2)

    def test_platforms_replace_template_and_deduplicate(self):
        with tempfile.TemporaryDirectory() as temp:
            dest = Path(temp) / 'new-app'
            self.create(dest, platforms=('windows', 'linux', 'windows'))
            listing = json.loads((dest / 'bundle/listing.json').read_text())
            self.assertEqual(listing['platforms'], ['windows', 'linux'])
            self.assertNotIn('android', listing['platforms'])
            self.assertEqual((dest/'.gitattributes').read_text(),'bundle/** -text\n')
            self.assertEqual(json.loads((dest / 'bundle/manifest.json').read_text())['id'], 'com.example.quicknotes')

    def test_check_exposes_and_forwards_catalog_and_publisher_keys(self):
        with tempfile.TemporaryDirectory() as temp:
            bundle=Path(temp)
            (bundle/'manifest.json').write_text(json.dumps({'integrity':{'signature':'signed fixture'}}))
            argv=['octo','check',str(bundle),'--catalog','catalog.json','--publisher-key','one=key','--publisher-key','two=key','--offline']
            with patch('sys.argv',argv), patch.object(octo,'need',return_value=Path('/fixture/hub')), patch.object(octo.subprocess,'run') as run, contextlib.redirect_stdout(io.StringIO()), self.assertRaises(SystemExit) as done:
                run.return_value.returncode=0
                octo.main()
            self.assertEqual(done.exception.code,0)
            self.assertEqual(run.call_args.args[0],['/fixture/hub','check',str(bundle.resolve()),'--catalog','catalog.json','--publisher-key','one=key','--publisher-key','two=key','--offline'])

    def test_reserved_ids_and_namespaces_leave_no_partial_project(self):
        names = ('agents apphub appcard browser calculator card clock dev notes octos octoscode os '
                 'reference reminders rinx sheets shell system task terminal toolbox weather workflow').split()
        with tempfile.TemporaryDirectory() as temp:
            for name in names:
                for app_id in (name, 'com.example.' + name):
                    for system in (False, True):
                        dest = Path(temp) / app_id
                        with self.subTest(app_id=app_id, system=system), self.assertRaises(SystemExit):
                            self.create(dest, app_id, system=system)
                        self.assertFalse(dest.exists())

    def test_system_prefix_needs_explicit_escape(self):
        with tempfile.TemporaryDirectory() as temp:
            dest = Path(temp) / 'new-app'
            with self.assertRaises(SystemExit): self.create(dest, 'os.example')
            self.assertFalse(dest.exists())
            self.create(dest, 'os.example', system=True)
            self.assertTrue((dest / 'bundle/main.splash').is_file())

    def test_windows_executables_found_in_candidate_directory_before_path(self):
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp)
            for name in ('hub', 'card-host'):
                exe = target / (name + '.exe')
                exe.touch(); exe.chmod(0o700)
                with patch.dict(os.environ, {}, clear=True), patch.object(octo.sys, 'platform', 'win32'), patch.object(octo, 'candidate_dirs', return_value=[target]), patch.object(octo, 'is_octosense_hub', return_value=True), patch.object(octo.shutil, 'which') as which:
                    found, where, searched = octo.find_binary(name, 'OCTO_' + name)
                    self.assertEqual(found, exe)
                    self.assertEqual(where, str(target))
                    which.assert_not_called()

    def test_windows_rejects_wrong_hub_before_path_fallback(self):
        with tempfile.TemporaryDirectory() as temp:
            exe = Path(temp) / 'hub.exe'; exe.touch(); exe.chmod(0o700)
            fallback = Path(temp) / 'known' / 'hub.exe'
            with patch.dict(os.environ, {}, clear=True), patch.object(octo.sys, 'platform', 'win32'), patch.object(octo, 'candidate_dirs', return_value=[Path(temp)]), patch.object(octo, 'is_octosense_hub', side_effect=lambda p: Path(p) == fallback), patch.object(octo.shutil, 'which', return_value=str(fallback)):
                found, where, searched = octo.find_binary('hub', 'OCTO_HUB')
                self.assertEqual(found, fallback)
                self.assertEqual(where, 'PATH')

    def test_reserved_names_match_available_hub_contract(self):
        repo = octo.hub_repo()
        if repo is None: self.skipTest('Set OCTOSENSE_APP_HUB to check contract parity')
        source = repo / 'crates/app-contract/src/manifest.rs'
        if not source.is_file(): self.skipTest('Hub contract source unavailable')
        declaration = re.search(r'pub const RESERVED_NAMES:.*?= &\[(.*?)\];', source.read_text(), re.S).group(1)
        self.assertEqual(octo.RESERVED_NAMES, set(re.findall(r'"([a-z]+)"', declaration)))


if __name__ == '__main__':
    unittest.main()
