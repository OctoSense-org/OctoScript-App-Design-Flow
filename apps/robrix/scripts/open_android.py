#!/usr/bin/env python3
"""Open the separately packaged Robrix preview on an authorized Android device."""
import argparse
import json
from pathlib import Path
import shlex
import shutil
import subprocess

PACKAGE = 'dev.makepad.octosense.robrixpreview'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--adb', default=shutil.which('adb'))
    parser.add_argument('--serial')
    parser.add_argument('--apk', type=Path)
    parser.add_argument('--card-preview', action='store_true', help='Fictional L0 card; no Matrix client')
    parser.add_argument('--capture', action='store_true', help='Enable app-owned GPU readback; allow at least 12 seconds after input')
    args = parser.parse_args()
    if not args.adb:
        parser.error('pass --adb /path/to/existing/platform-tools/adb')
    rows = subprocess.check_output([args.adb, 'devices'], text=True).splitlines()[1:]
    devices = [row.split()[0] for row in rows if len(row.split()) >= 2 and row.split()[1] == 'device']
    if not args.serial and len(devices) == 1:
        args.serial = devices[0]
    if args.serial not in devices:
        parser.error('connect one authorized device or specify --serial')
    adb = [args.adb, '-s', args.serial]
    running = subprocess.run(adb + ['shell', 'pidof', PACKAGE], capture_output=True, text=True)
    if running.stdout.strip():
        parser.error('close the existing Robrix preview before starting another session')
    if args.apk:
        subprocess.run(adb + ['install', '--no-incremental', '-r', str(args.apk.resolve())], check=True)
    config = {'test_actions': ['launch-robrix']}
    if args.card_preview:
        config['module_open'] = {'robrix': {'card_preview': True}}
    if args.capture:
        folder = '/sdcard/Android/data/' + PACKAGE + '/files'
        subprocess.run(adb + ['shell', 'mkdir', '-p', folder], check=True)
        subprocess.run(adb + ['shell', 'rm', '-f', folder + '/robrix-capture.png'], check=True)
        config['test_actions'].append('capture:' + folder + '/robrix-capture.png')
    command = ['am', 'start', '-n', PACKAGE + '/.MakepadApp', '--es', 'makepad.APP_CONFIG', json.dumps(config)]
    subprocess.run(adb + ['shell', shlex.join(command)], check=True)
    print('Opened Robrix AppCard fixture.' if args.card_preview else 'Opened Robrix Matrix login.')
    if args.capture:
        print('GPU capture uses two 5-second timer stages and requests a redraw. Wait at least 12 seconds after input; this is not a repaint-latency test.')


if __name__ == '__main__':
    main()
