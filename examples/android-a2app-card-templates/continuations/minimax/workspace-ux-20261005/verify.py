"""Replay the recorded Android model edits against the preserved original files."""
import hashlib
import json
from pathlib import Path
root = Path(__file__).resolve().parent
record = json.loads((root / "provenance.json").read_text())
for item in record["files"]:
    before = (root / item["base"]).read_bytes()
    after = (root / item["output"]).read_bytes()
    edit = item["mutation"]
    assert hashlib.sha256(before).hexdigest() == item["base_sha256"]
    assert before.count(edit["old_string"].encode()) == 1
    assert before.replace(edit["old_string"].encode(), edit["new_string"].encode(), 1) == after
    assert hashlib.sha256(after).hexdigest() == item["output_sha256"]
    print(item["output"], "model edit replay: PASS")
