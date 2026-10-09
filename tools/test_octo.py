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
import shutil
import subprocess
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
            hub=bundle/'fixture-tools'/'hub'
            (bundle/'manifest.json').write_text(json.dumps({'integrity':{'signature':'signed fixture'}}))
            argv=['octo','check',str(bundle),'--catalog','catalog.json','--publisher-key','one=key','--publisher-key','two=key','--offline']
            with patch('sys.argv',argv), patch.object(octo,'need',return_value=hub), patch.object(octo.subprocess,'run') as run, contextlib.redirect_stdout(io.StringIO()), self.assertRaises(SystemExit) as done:
                run.return_value.returncode=0
                octo.main()
            self.assertEqual(done.exception.code,0)
            self.assertEqual(run.call_args.args[0],[str(hub),'check',str(bundle.resolve()),'--catalog','catalog.json','--publisher-key','one=key','--publisher-key','two=key','--offline'])

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


# ---------------------------------------------------------------------- wasm
wasm_component = octo.wasm_component
SDK_WASM = [HERE.parent / 'sdk/rust/target' / d / 'wasm32-wasip2/release' for d in ('e2e-wasm', '.')]


def leb(n):
    out = bytearray()
    while True:
        byte, n = n & 0x7f, n >> 7
        out.append(byte | (0x80 if n else 0))
        if not n:
            return bytes(out)


def text(value):
    raw = value.encode()
    return leb(len(raw)) + raw


def section(sid, *entries):
    body = leb(len(entries)) + b''.join(entries)
    return bytes([sid]) + leb(len(body)) + body


def component(*imports):
    """A component's skeleton, laid out the way wit-component lays one out
    (it is not valid: no core code backs its functions). It imports each
    interface as an instance, and a record type as `(type (eq …))`, which
    reaches nothing; it exports `count-words: func(text: string) -> stats`
    and `ping: func()`, the latter with an ascribed type."""
    instance, record = b'\x42\x00', b'\x72\x01' + text('words') + b'\x79'
    count_words = b'\x40\x01' + text('text') + b'\x73' + b'\x00\x02'   # -> type 2, the import of type 1
    ping = b'\x40\x00\x01\x00'
    return (wasm_component.COMPONENT_PREAMBLE
            + section(7, instance, record)
            + section(10, *[b'\x00' + text(name) + b'\x05\x00' for name in imports], b'\x00' + text('stats') + b'\x03\x00\x01')
            + section(7, count_words, ping)
            + section(8, b'\x00\x00\x00\x00\x03', b'\x00\x00\x01\x00\x04')     # lift: functions 0 and 1
            + section(11, b'\x00' + text('count-words') + b'\x01\x00\x00')
            + section(11, b'\x00' + text('ping') + b'\x01\x01\x01\x01\x04'))


# (module (import "octo" "log" (func (param i32 i32)))
#   (func (export "add") (param i32 i32) (result i32) local.get 0 local.get 1 i32.add))
CORE_MODULE = (b'\0asm\x01\0\0\0\x01\x0c\x02\x60\x02\x7f\x7f\x01\x7f\x60\x02\x7f\x7f\x00'
               b'\x02\x0c\x01\x04octo\x03log\x00\x01\x03\x02\x01\x00\x07\x07\x01\x03add\x00\x01'
               b'\x0a\x09\x01\x07\x00\x20\x00\x20\x01\x6a\x0b')

ENV, FILES, TCP = 'wasi:cli/environment@0.2.9', 'wasi:filesystem/types@0.2.9', 'wasi:sockets/tcp@0.2.9'
CLOCK, RANDOM = 'wasi:clocks/wall-clock@0.2.9', 'wasi:random/random@0.2.9'
HTTP, HTTP_TYPES = 'wasi:http/outgoing-handler@0.2.9', 'wasi:http/types@0.2.9'
HOST_SERVICES = 'octosense:host/services@0.1.0'


def toolchain():
    """cargo, when it and the wasm32-wasip2 target are installed."""
    cargo = octo.cargo_path()
    found = octo.rust_toolchain(cargo) if cargo else None
    return cargo if found and found['target'] and (found['release'] or (0, 0)) >= octo.MIN_RUST else None


def git(repo, *args):
    subprocess.run(['git', '-C', str(repo), '-c', 'user.name=Test', '-c', 'user.email=test@example.com',
                    '-c', 'commit.gpgsign=false', *args], check=True, capture_output=True)


class WasmReader(unittest.TestCase):
    def test_a_component_s_imports_and_typed_exports(self):
        info = wasm_component.describe(component(ENV, TCP))
        self.assertEqual(info, {
            'kind': 'component',
            'imports': [ENV, TCP],
            'exports': [
                {'name': 'count-words', 'params': [['text', 'string']], 'result': 'record { words: u32 }'},
                {'name': 'ping', 'params': [], 'result': None},
            ],
        })
        self.assertEqual(wasm_component.refused_imports(info['imports']), [TCP])
        # A package name is matched whole, as App Hub's gate matches it.
        self.assertEqual(wasm_component.refused_imports(['wasi:clocksmith/x', 'my:pkg/host']), ['wasi:clocksmith/x', 'my:pkg/host'])

    def test_phase_3_admits_http_and_host_services_and_nothing_else(self):
        imports = ['wasi:io/poll@0.2.9', 'wasi:sockets/network@0.2.9', HTTP_TYPES, 'my:pkg/host',
                   HOST_SERVICES, 'octosense:hostile/x']
        self.assertEqual(wasm_component.refused_imports(imports),
                         ['wasi:sockets/network@0.2.9', 'my:pkg/host', 'octosense:hostile/x'])
        self.assertTrue(wasm_component.uses_http(imports))
        self.assertTrue(wasm_component.uses_host_services(imports))
        self.assertFalse(wasm_component.uses_http([ENV, FILES, 'wasi:httpx/x']))
        self.assertFalse(wasm_component.uses_host_services([ENV, 'octosense:hostile/x']))

    def test_the_reach_line_is_app_hub_s(self):
        # App Hub's `ComponentInfo::reach` tests, word for word.
        reach = wasm_component.reach
        hosts = ['api.example.com', 'cdn.example.com']
        self.assertEqual(reach([ENV]), 'nothing but its input')
        self.assertEqual(reach([CLOCK, RANDOM]), 'the clock and random numbers, but no files, network or other app')
        self.assertEqual(reach([FILES]), 'files in its app folder, but no network or other app')
        self.assertEqual(reach([CLOCK, FILES]), 'the clock and files in its app folder, but no network or other app')
        self.assertEqual(reach([HTTP, CLOCK], hosts),
                         'the clock and HTTPS to api.example.com, cdn.example.com, but no files or other app')
        self.assertEqual(reach([HTTP, FILES], hosts[:1]),
                         'files in its app folder and HTTPS to api.example.com, but no other app')
        self.assertEqual(reach([HOST_SERVICES]), "its app's host services, but no files, network or other app")
        self.assertEqual(reach([CLOCK, HOST_SERVICES]), "the clock and its app's host services, but no files, network or other app")
        self.assertEqual(reach([CLOCK, RANDOM, FILES, HTTP, HOST_SERVICES], hosts[:1]),
                         "the clock, random numbers, files in its app folder, HTTPS to api.example.com and "
                         "its app's host services, but no other app")
        # Hosts reach nothing without the import, and the import nothing without hosts.
        self.assertEqual(reach([CLOCK], hosts), 'the clock, but no files, network or other app')
        self.assertEqual(reach([HTTP_TYPES]), 'nothing but its input')

    def test_a_core_module_s_imports_and_exports(self):
        self.assertEqual(wasm_component.describe(CORE_MODULE), {
            'kind': 'module',
            'imports': ['octo.log'],
            'exports': [{'name': 'add', 'params': [['p0', 'i32'], ['p1', 'i32']], 'result': 'i32'}],
        })

    def test_anything_else_is_refused_by_name(self):
        for data in (b'#!/bin/sh\n', component(ENV)[:-3], wasm_component.COMPONENT_PREAMBLE + b'\x0a\x05\x01\x07'):
            with self.subTest(data=data[:12]), self.assertRaises(wasm_component.ReadError):
                wasm_component.describe(data)

    def test_built_components_read_as_hub_component_info_reads_them(self):
        # The SDK's examples, once `cargo test` in sdk/rust has built them.
        found = [d / 'markdown_tools.wasm' for d in SDK_WASM if (d / 'markdown_tools.wasm').is_file()]
        if not found: self.skipTest('build sdk/rust first: cargo test --locked --workspace')
        info = wasm_component.describe(found[0].read_bytes())
        self.assertEqual([(e['name'], e['params'], e['result']) for e in info['exports']], [
            ('analyze', [['markdown', 'string']], 'record { words: u32, lines: u32, headings: list<string> }'),
            ('measure', [['markdown', 'string']], 'enum { short, medium, long }'),
            ('now-ms', [], 'u64'),
            ('save-html', [['markdown', 'string'], ['path', 'string']], 'result<u64, string>'),
            ('to-html', [['markdown', 'string']], 'string'),
        ])
        self.assertTrue(wasm_component.uses_files(info['imports']))
        self.assertEqual(wasm_component.refused_imports(info['imports']), [])

    def test_built_phase_3_examples_import_only_what_they_call(self):
        found = {name: [d / name for d in SDK_WASM if (d / name).is_file()]
                 for name in ('http_client.wasm', 'host_services.wasm')}
        if not all(found.values()): self.skipTest('build sdk/rust first: cargo test --locked --workspace')
        client = wasm_component.describe(found['http_client.wasm'][0].read_bytes())
        services = wasm_component.describe(found['host_services.wasm'][0].read_bytes())
        for info in (client, services):
            self.assertEqual(wasm_component.refused_imports(info['imports']), [])
        self.assertTrue(wasm_component.uses_http(client['imports']))
        self.assertFalse(wasm_component.uses_host_services(client['imports']))
        self.assertIn(HOST_SERVICES, services['imports'])
        self.assertFalse(wasm_component.uses_http(services['imports']))
        self.assertEqual(wasm_component.reach(client['imports'], ['api.example.com']),
                         'the clock and HTTPS to api.example.com, but no files or other app')
        self.assertEqual(wasm_component.reach(services['imports']),
                         "the clock and its app's host services, but no files, network or other app")
        self.assertEqual([(e['name'], e['params'], e['result']) for e in services['exports']], [
            ('call', [['service', 'string'], ['args', 'string']], 'result<string, string>'),
            ('host-apis', [], 'result<string, string>'),
        ])


class WasmCommands(unittest.TestCase):
    def app(self, temp, capabilities=('storage',), hosts=None):
        app = Path(temp) / 'texttools'
        Onboarding.create(self, app, 'dev.example.texttools')
        manifest = app / 'bundle/manifest.json'
        fields = dict(json.loads(manifest.read_text()), capabilities=list(capabilities))
        if hosts is not None:
            fields['network'] = {'hosts': list(hosts)}
        manifest.write_text(json.dumps(fields, indent=2) + '\n')
        return app

    def octo(self, *argv):
        out, err = io.StringIO(), io.StringIO()
        with patch('sys.argv', ['octo', *argv]), patch.object(octo, 'find_binary', return_value=(None, None, [])), \
                contextlib.redirect_stdout(out), contextlib.redirect_stderr(err), self.assertRaises(SystemExit) as done:
            octo.main()
        return done.exception.code, out.getvalue(), err.getvalue()

    def fake_cargo(self, crate, wasm, name='text-tools'):
        """subprocess.run as cargo answers for a crate whose build makes `wasm`."""
        package = {'name': name, 'id': f'path+file://{crate}#0.1.0', 'manifest_path': str(crate / 'Cargo.toml')}

        def run(cmd, **kwargs):
            if 'metadata' in cmd:
                return subprocess.CompletedProcess(cmd, 0, stdout=json.dumps({'packages': [package]}), stderr='')
            if 'build' in cmd:
                artifact = {'reason': 'compiler-artifact', 'package_id': package['id'], 'filenames': [str(wasm)]}
                return subprocess.CompletedProcess(cmd, 0, stdout='\n'.join([json.dumps(artifact), '{"reason":"build-finished","success":true}']))
            raise AssertionError(cmd)
        return run

    def build(self, app, data):
        crate = app / 'components/text-tools'
        (crate / 'src').mkdir(parents=True)
        (crate / 'Cargo.toml').write_text('[package]\nname = "text-tools"\n')
        wasm = Path(app) / 'built.wasm'
        wasm.write_bytes(data)
        with patch.object(octo, 'cargo_path', return_value='cargo'), \
                patch.object(octo, 'rust_toolchain', return_value={'version': 'rustc 1.97.1', 'release': (1, 97), 'target': True}), \
                patch.object(octo.subprocess, 'run', side_effect=self.fake_cargo(crate, wasm)):
            return self.octo('wasm', 'build', '--app', str(app))

    def test_new_writes_the_template_with_the_sdk_by_path_or_commit(self):
        with tempfile.TemporaryDirectory() as temp:
            app = self.app(temp)
            code, out, _ = self.octo('wasm', 'new', 'text-tools', '--app', str(app), '--sdk', 'path')
            self.assertEqual(code, 0, out)
            crate = app / 'components/text-tools'
            cargo = (crate / 'Cargo.toml').read_text()
            self.assertIn('name = "text-tools"', cargo)
            self.assertIn('crate-type = ["cdylib", "rlib"]', cargo)
            self.assertIn('because you chose --sdk path', cargo)
            path = re.search(r'^octosense-component = \{ path = "(.+)" \}$', cargo, re.M).group(1)
            self.assertEqual((crate / path).resolve(), (HERE.parent / 'sdk/rust/octosense-component').resolve())
            self.assertEqual((crate / 'src/lib.rs').read_text(), (HERE.parent / 'templates/rust-component/src/lib.rs').read_text())
            self.assertEqual((crate / '.gitignore').read_text(), '/target/\n')
            # Pinned to a commit on App Flow's main when there is one.
            with patch.object(octo, 'sdk_revision', return_value=('a' * 40, None)):
                code, out, _ = self.octo('wasm', 'new', 'other', '--app', str(app))
            self.assertEqual(code, 0, out)
            self.assertIn('octosense-component = { git = "https://github.com/OctoSense-org/OctoSense-App-Flow", rev = "' + 'a' * 40 + '" }',
                          (app / 'components/other/Cargo.toml').read_text())
            with patch.object(octo, 'sdk_revision', return_value=(None, 'no reason')):
                code, _, err = self.octo('wasm', 'new', 'third', '--app', str(app), '--sdk', 'git')
            self.assertEqual(code, 1)
            self.assertIn('no App Flow commit to pin the SDK to: no reason', err)
            self.assertFalse((app / 'components/third').exists())

    def test_new_refuses_names_that_cannot_be_a_crate_and_a_file(self):
        with tempfile.TemporaryDirectory() as temp:
            app = self.app(temp)
            (app / 'bundle/fns').mkdir()
            (app / 'bundle/fns/taken.wasm').write_bytes(CORE_MODULE)
            for name in ('Text', '2d', 'fn', 'test', 'a' * 65, 'my.tools', 'taken'):
                with self.subTest(name=name):
                    code, _, err = self.octo('wasm', 'new', name, '--app', str(app), '--sdk', 'path')
                    self.assertEqual(code, 1, err)
                    self.assertFalse((app / 'components' / name).exists())
            self.assertEqual(self.octo('wasm', 'new', 'x', '--app', temp)[0], 1)  # no bundle/ there

    def test_sdk_commit_is_on_app_flow_s_main_and_has_the_sdk(self):
        if not shutil.which('git'): self.skipTest('needs git')
        with tempfile.TemporaryDirectory() as temp:
            repo = Path(temp)
            git(repo, 'init', '-q')
            git(repo, 'remote', 'add', 'origin', 'https://github.com/OctoSense-org/OctoScript-App-Design-Flow.git')
            (repo / 'README.md').write_text('App Flow\n')
            git(repo, 'add', '.')
            git(repo, 'commit', '-qm', 'before the SDK')
            git(repo, 'update-ref', 'refs/remotes/origin/main', 'HEAD')
            with patch.object(octo, 'REPO', repo):
                rev, why = octo.sdk_revision()
                self.assertIsNone(rev)
                self.assertIn('does not have the SDK yet', why)
                (repo / 'sdk/rust/octosense-component').mkdir(parents=True)
                (repo / 'sdk/rust/octosense-component/Cargo.toml').write_text('[package]\n')
                git(repo, 'add', '.')
                git(repo, 'commit', '-qm', 'the SDK')
                git(repo, 'update-ref', 'refs/remotes/origin/main', 'HEAD')
                main = subprocess.run(['git', '-C', str(repo), 'rev-parse', 'HEAD'], capture_output=True, text=True).stdout.strip()
                git(repo, 'commit', '-q', '--allow-empty', '-m', 'local work, not on main')
                self.assertEqual(octo.sdk_revision(), (main, None))
                git(repo, 'remote', 'set-url', 'origin', 'https://github.com/someone/fork.git')
                self.assertIsNone(octo.sdk_revision()[0])

    def test_build_copies_the_component_and_declares_what_it_needs(self):
        with tempfile.TemporaryDirectory() as temp:
            app = self.app(temp, capabilities=())
            code, out, err = self.build(app, component(ENV, FILES))
            self.assertEqual(code, 0, out + err)
            self.assertEqual((app / 'bundle/fns/text-tools.wasm').read_bytes(), component(ENV, FILES))
            manifest = json.loads((app / 'bundle/manifest.json').read_text())
            self.assertEqual(manifest['capabilities'], ['wasm', 'storage'])
            self.assertEqual(manifest['requires'], ['wasm-components-v1'])
            self.assertIn('wasm.count_words(text: string) -> record { words: u32 }', out)
            self.assertIn('imports wasi:filesystem', out)
            # Building again changes nothing.
            code, out, _ = self.build_again(app, component(ENV, FILES))
            self.assertEqual(code, 0)
            self.assertIn('unchanged bundle/fns/text-tools.wasm', out)
            self.assertNotIn('bundle/manifest.json:', out)

    def build_again(self, app, data):
        crate = app / 'components/text-tools'
        wasm = Path(app) / 'built.wasm'
        wasm.write_bytes(data)
        with patch.object(octo, 'cargo_path', return_value='cargo'), \
                patch.object(octo, 'rust_toolchain', return_value={'version': 'rustc 1.97.1', 'release': (1, 97), 'target': True}), \
                patch.object(octo.subprocess, 'run', side_effect=self.fake_cargo(crate, wasm)):
            return self.octo('wasm', 'build', '--app', str(app))

    def test_build_refuses_imports_no_host_gives_and_leaves_the_bundle_alone(self):
        with tempfile.TemporaryDirectory() as temp:
            app = self.app(temp)
            before = (app / 'bundle/manifest.json').read_text()
            code, _, err = self.build(app, component(ENV, TCP))
            self.assertEqual(code, 1)
            self.assertIn(TCP, err)
            self.assertIn('a component has none. It reaches the app\'s own hosts over HTTP through wasi:http, '
                          'with octosense_component::http', err)
            self.assertFalse((app / 'bundle/fns').exists())
            self.assertEqual((app / 'bundle/manifest.json').read_text(), before)
        with tempfile.TemporaryDirectory() as temp:
            app = self.app(temp)
            code, _, err = self.build(app, component(ENV, 'octosense:hostile/x'))
            self.assertEqual(code, 1)
            self.assertIn('octosense:hostile/x:\n    not an interface any host gives a component', err)

    def test_build_adds_net_for_http_when_the_manifest_lists_its_hosts(self):
        with tempfile.TemporaryDirectory() as temp:
            app = self.app(temp, capabilities=(), hosts=['api.example.com'])
            code, out, err = self.build(app, component(CLOCK, HTTP, HTTP_TYPES))
            self.assertEqual(code, 0, out + err)
            manifest = json.loads((app / 'bundle/manifest.json').read_text())
            self.assertEqual(manifest['capabilities'], ['wasm', 'net'])
            self.assertEqual(manifest['network'], {'hosts': ['api.example.com']})
            self.assertIn('a component that reaches the clock and HTTPS to api.example.com, but no files or other app', out)
            self.assertIn('added "net" to capabilities: text-tools imports wasi:http, and its requests reach only '
                          "the hosts in network.hosts (api.example.com), as the app's script does", out)
            self.assertNotIn('warning', out + err)

    def test_build_never_adds_a_host_and_says_the_gate_refuses_http_without_one(self):
        for capabilities in ((), ('net',)):
            with self.subTest(capabilities=capabilities), tempfile.TemporaryDirectory() as temp:
                app = self.app(temp, capabilities=capabilities)
                code, out, err = self.build(app, component(CLOCK, HTTP))
                self.assertEqual(code, 0, out + err)
                manifest = json.loads((app / 'bundle/manifest.json').read_text())
                self.assertEqual(manifest['capabilities'], [*capabilities, 'wasm'])
                self.assertNotIn('network', manifest)
                self.assertIn('a component that reaches the clock, but no files, network or other app', out)
                self.assertIn("octo: warning: text-tools imports wasi:http, but the manifest's network.hosts lists no "
                              "host, so App Hub's gate refuses the bundle", out)

    def test_build_takes_host_services_with_no_grant_of_their_own(self):
        with tempfile.TemporaryDirectory() as temp:
            app = self.app(temp, capabilities=())
            code, out, err = self.build(app, component(CLOCK, HOST_SERVICES))
            self.assertEqual(code, 0, out + err)
            manifest = json.loads((app / 'bundle/manifest.json').read_text())
            self.assertEqual((manifest['capabilities'], manifest['requires']), (['wasm'], ['wasm-components-v1']))
            self.assertIn("a component that reaches the clock and its app's host services, but no files, network or other app", out)

    def test_build_refuses_a_core_module(self):
        with tempfile.TemporaryDirectory() as temp:
            app = self.app(temp)
            code, _, err = self.build(app, CORE_MODULE)
            self.assertEqual(code, 1)
            self.assertIn('is not a WebAssembly component', err)

    def test_doctor_names_dependencies_that_do_not_build_or_run(self):
        crate = Path('/apps/texttools/components/text-tools')
        package = lambda id, name, **extra: dict({'id': id, 'name': name, 'version': '1.0.0', 'dependencies': []}, **extra)
        build_cc = [{'name': 'cc', 'pkg': 'cc', 'dep_kinds': [{'kind': 'build', 'target': None}]}]
        uses = lambda *ids, kind=None: [{'name': i, 'pkg': i, 'dep_kinds': [{'kind': kind, 'target': None}]} for i in ids]
        metadata = {
            'packages': [
                package('root', 'text-tools', manifest_path=str(crate / 'Cargo.toml'),
                        targets=[{'kind': ['cdylib', 'rlib'], 'crate_types': ['cdylib', 'rlib']}],
                        dependencies=[{'name': 'octosense-component'}]),
                package('ssl', 'openssl-sys'), package('ray', 'rayon'), package('tok', 'tokio'),
                package('zstd', 'zstd-sys'), package('cc', 'cc'), package('md', 'pulldown-cmark'),
                package('wt', 'wasmtime'), package('rq', 'reqwest'),
            ],
            # The component links md, ssl, ray, tok and, through md, zstd; a
            # test (wt) and a build script (rq) need the others, on this machine.
            'resolve': {'root': 'root', 'nodes': [
                {'id': 'root', 'deps': uses('md', 'ssl', 'ray', 'tok') + uses('wt', kind='dev') + uses('rq', kind='build')},
                {'id': 'ssl', 'deps': build_cc}, {'id': 'ray', 'deps': []},
                {'id': 'tok', 'deps': [], 'features': ['rt', 'net', 'macros']}, {'id': 'zstd', 'deps': build_cc},
                {'id': 'cc', 'deps': []}, {'id': 'md', 'deps': uses('zstd')}, {'id': 'wt', 'deps': uses('tok')},
                {'id': 'rq', 'deps': []},
            ]},
        }
        done = subprocess.CompletedProcess([], 0, stdout=json.dumps(metadata), stderr='')
        with patch.object(octo.subprocess, 'run', return_value=done) as run:
            findings = octo.dependency_findings('cargo', crate)
        self.assertIn('--filter-platform', run.call_args.args[0])
        self.assertEqual([level for level, _ in findings], ['ok', 'ok', 'fail', 'warn', 'warn', 'warn'])
        self.assertTrue(findings[2][1].startswith('openssl-sys 1.0.0 links OpenSSL'))
        text = '\n'.join(t for _, t in findings)
        for expected in ('rayon 1.0.0 starts threads', 'tokio 1.0.0 with net', 'zstd-sys 1.0.0 compiles C code'):
            self.assertIn(expected, text)
        self.assertNotIn('openssl-sys 1.0.0 compiles C code', text)
        self.assertNotIn('wasmtime', text)
        self.assertNotIn('reqwest', text)

    def test_info_reads_a_file_without_a_hub(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'tools.wasm'
            path.write_bytes(component(ENV, TCP))
            with patch.object(octo, 'component_info_hub', return_value=None):
                code, out, _ = self.octo('wasm', 'info', str(path))
                self.assertEqual(code, 0)
                self.assertIn("read by octo's own reader", out)
                self.assertIn('wasm.count_words(text: string) -> record { words: u32 }', out)
                self.assertIn(f'{TCP}   (refused)', out)
                code, out, _ = self.octo('wasm', 'info', str(path), '--json')
                self.assertEqual(json.loads(out), wasm_component.describe(component(ENV, TCP)))
                # What a phase 3 component needs, without the app's manifest.
                path.write_bytes(component(CLOCK, FILES, HTTP, HOST_SERVICES))
                code, out, _ = self.octo('wasm', 'info', str(path))
                self.assertEqual(code, 0)
                self.assertIn("reaches: the clock, files in its app folder, HTTPS to the hosts in the app's "
                              "network.hosts and its app's host services, but no other app", out)
                self.assertIn('"storage" in capabilities (it imports wasi:filesystem), "net" in capabilities and '
                              'the hosts it reaches in network.hosts (it imports wasi:http), the capability of each '
                              'host service it calls (it imports octosense:host', out)

    @unittest.skipUnless(toolchain(), 'needs cargo and the wasm32-wasip2 target (rustup target add wasm32-wasip2)')
    def test_new_then_build_with_cargo_makes_a_working_bundle(self):
        with tempfile.TemporaryDirectory() as temp:
            app = self.app(temp, capabilities=())
            self.assertEqual(self.octo('wasm', 'new', 'text-tools', '--app', str(app), '--sdk', 'path')[0], 0)
            code, out, err = self.octo('wasm', 'build', '--app', str(app))
            self.assertEqual(code, 0, out + err)
            info = wasm_component.describe((app / 'bundle/fns/text-tools.wasm').read_bytes())
            self.assertEqual([(e['name'], e['params'], e['result']) for e in info['exports']], [
                ('count', [['text', 'string']], 'record { words: u32, lines: u32 }'),
                ('greet', [['name', 'string']], 'string'),
                ('parse-number', [['text', 'string']], 'result<f64, string>'),
            ])
            self.assertEqual(wasm_component.refused_imports(info['imports']), [])
            manifest = json.loads((app / 'bundle/manifest.json').read_text())
            self.assertEqual((manifest['capabilities'], manifest['requires']), (['wasm'], ['wasm-components-v1']))


if __name__ == '__main__':
    unittest.main()
