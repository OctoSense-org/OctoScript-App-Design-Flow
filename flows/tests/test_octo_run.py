"""tools/octo run: port checks and bridge detection (#119), without card-host."""
import importlib.machinery
import importlib.util
import json
import socket
import subprocess
import sys
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

OCTO = Path(__file__).resolve().parents[2] / 'tools' / 'octo'
loader = importlib.machinery.SourceFileLoader('octo', str(OCTO))
spec = importlib.util.spec_from_loader('octo', loader)
octo = importlib.util.module_from_spec(spec)
loader.exec_module(octo)


def free_port():
    with socket.socket() as s:
        s.bind(('127.0.0.1', 0))
        return s.getsockname()[1]


class FakeBridge(BaseHTTPRequestHandler):
    def do_GET(self):
        body = json.dumps({'app': 'card-host', 'pid': 4242, 'w': []}).encode()
        self.send_response(200)
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass


class PortOwnerTests(unittest.TestCase):
    def test_free_port(self):
        self.assertIsNone(octo.port_owner(free_port()))

    def test_bridge_on_port_is_named(self):
        server = HTTPServer(('127.0.0.1', 0), FakeBridge)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        try:
            owner = octo.port_owner(server.server_address[1])
        finally:
            server.shutdown()
            server.server_close()
        self.assertIn('card-host pid 4242', owner)

    def test_other_listener(self):
        with socket.socket() as s:
            s.bind(('127.0.0.1', 0))
            s.listen()
            owner = octo.port_owner(s.getsockname()[1])
        self.assertIn('not a makepad remote bridge', owner)


class WaitForTests(unittest.TestCase):
    def run_fake(self, lines, port=8171):
        with tempfile.TemporaryDirectory() as d:
            log = Path(d) / 'card-host.log'
            proc = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(30)'])
            try:
                log.write_text('\n'.join(line.replace('{pid}', str(proc.pid)) for line in lines) + '\n')
                return octo.wait_for(log, proc, port, timeout=2)
            finally:
                proc.kill()
                proc.wait()

    def test_bind_failure_is_an_error(self):
        _, admitted, error = self.run_fake([
            '[E] makepad/platform/src/remote.rs:518:17 - [makepad-remote] bind 127.0.0.1:8171 failed: Address already in use (os error 48)',
            '[I] card-host: tip-split 0.1.0 admitted — capabilities {}',
        ])
        self.assertIn('bind 127.0.0.1:8171 failed', error)

    def test_listening_line_must_match_port_and_pid(self):
        _, admitted, error = self.run_fake([
            '[makepad-remote] listening on 127.0.0.1:8172 pid={pid} app=card-host',
            '[makepad-remote] listening on 127.0.0.1:8171 pid=1 app=card-host',
            '[I] card-host: tip-split 0.1.0 admitted — capabilities {}',
        ])
        self.assertTrue(admitted)
        self.assertIn('never reported its remote bridge', error)

    def test_success(self):
        listening, admitted, error = self.run_fake([
            '[makepad-remote] listening on 127.0.0.1:8171 pid={pid} app=card-host',
            '[I] card-host: tip-split 0.1.0 admitted — capabilities {}',
        ])
        self.assertIsNone(error)
        self.assertIn('8171', listening)


if __name__ == '__main__':
    unittest.main()
