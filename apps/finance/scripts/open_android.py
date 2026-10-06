#!/usr/bin/env python3
"""Open Finance in the separately packaged OctoSense-mobile preview."""
import argparse
import json
from pathlib import Path
import shlex
import shutil
import subprocess

PACKAGE = "dev.makepad.octosense.financepreview"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--adb", default=shutil.which("adb"))
    parser.add_argument("--serial", required=True, help="Explicit authorized device serial")
    parser.add_argument("--apk", type=Path, help="Install this preview APK before opening")
    parser.add_argument("--capture", action="store_true", help="Enable app-owned GPU capture")
    parser.add_argument("--symbol", help="Open a canonical listing, for example XNAS:AAPL")
    args = parser.parse_args()
    if not args.adb:
        parser.error("pass --adb /path/to/existing/platform-tools/adb")
    rows = subprocess.check_output([args.adb, "devices"], text=True).splitlines()[1:]
    devices = [r.split()[0] for r in rows if len(r.split()) >= 2 and r.split()[1] == "device"]
    if args.serial not in devices:
        parser.error("the selected device is not connected and authorized")
    adb = [args.adb, "-s", args.serial]
    running = subprocess.run(adb + ["shell", "pidof", PACKAGE], capture_output=True, text=True)
    if running.stdout.strip():
        parser.error("close the existing Finance preview before starting another session")
    if args.apk:
        if not args.apk.is_file():
            parser.error("APK does not exist")
        subprocess.run(adb + ["install", "--no-incremental", "-r", str(args.apk.resolve())], check=True)
    config = {"test_actions": ["launch-finance"]}
    if args.symbol:
        config["module_open"] = {"finance": {"symbol": args.symbol}}
    capture_path = f"/data/user/0/{PACKAGE}/files/finance-capture.png"
    if args.capture:
        subprocess.run(adb + ["shell", "run-as", PACKAGE, "mkdir", "-p", "files"], check=True)
        subprocess.run(adb + ["shell", "run-as", PACKAGE, "rm", "-f", "files/finance-capture.png"], check=True)
        config["test_actions"].append("capture:" + capture_path)
    command = ["am", "start", "-n", PACKAGE + "/.MakepadApp", "--es", "makepad.APP_CONFIG", json.dumps(config)]
    subprocess.run(adb + ["shell", shlex.join(command)], check=True)
    print("Opened Finance in OctoSense-mobile with fictional preview data.")
    if args.capture:
        print("Allow at least 12 seconds for app-owned GPU capture; this is not a repaint-latency check.")
        print("Read capture using adb exec-out run-as " + PACKAGE + " cat files/finance-capture.png")


if __name__ == "__main__":
    main()
