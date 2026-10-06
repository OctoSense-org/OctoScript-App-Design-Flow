"""Artifact integrity and publication tests; these do not assess visual quality."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location("flow_bundle", Path(__file__).with_name("bundle.py"))
bundle = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bundle)


class BundleTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name) / "project"
        self.root.mkdir()
        self.scene = self.root / "cards/example"
        self.scene.mkdir(parents=True)
        self.output = self.root / "export/bundle"
        self.prefix = "http://127.0.0.1:8170/ux-images/"
        self.asset = b'<svg xmlns="http://www.w3.org/2000/svg"><path d="M1 2L3 4"/></svg>'
        self.put("cards/example/assets/icon.svg", self.asset)
        self.put("art/example/assets/icon-hashed.svg", self.asset)
        self.put("art/unrelated.png", b"never export this")
        self.metadata = {"reference_sha256": bundle.digest(b"original screen"), "elements": [
            {"id": "icon", "asset": {"path": "assets/icon.svg", "sha256": bundle.digest(self.asset), "method": "reference_svg"}}
        ]}
        self.put("cards/example/semantic-map.json", self.metadata)
        self.put("cards/example/reference.png", b"original screen")
        self.data = {"$kit": {"placements": {"icon": {"layout": {"src": self.prefix + "example/assets/icon-hashed.svg"}}}}, "label": "确认预约"}
        self.put("cards/example/page.card", 'native ConfirmButton { text: "确认预约" }')
        self.put("cards/example/page.data.json", self.data)
        self.put("cards/example/kit/native/light/kit.json", {"kind": "native", "enabled": True})
        self.put("cards/example/mapping.json", {"confirm_booking": "button_1"})
        self.put("cards/example/service-actions.json", {"controls": {"confirm_booking": {"action": "installation.confirm_booking"}}})
        self.manifest = {"schema_version": 1, "id": "example", "artboard": [406, 776],
                         "scenes": [{"id": "1", "directory": "cards/example", "title": "标题"}],
                         "artwork": {"source_prefix": self.prefix, "root": "art"}}
        self.save_manifest()

    def put(self, relative, content):
        target = self.root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(content, (dict, list)):
            content = json.dumps(content, ensure_ascii=False).encode()
        elif isinstance(content, str):
            content = content.encode()
        target.write_bytes(content)
        return target

    def save_manifest(self):
        self.put("flow.json", self.manifest)

    def export(self):
        return bundle.export_bundle(self.root, "flow.json", self.output)

    def test_inline_html_requires_native_web_component(self):
        src = "data:text/html;charset=utf-8;base64,PGgxPkhlbGxvPC9oMT4="
        self.data["$kit"]["placements"]["reader"] = {"component": "Reader", "layout": {"src": src}}
        self.put("cards/example/page.data.json", self.data)
        with self.assertRaises(bundle.BundleError):
            self.export()
        self.put("cards/example/kit/native/light/kit.json", {"components": {"Reader": {"style": {"t": "web"}}}})
        self.assertTrue(self.export()["passed"])

    def test_preserves_native_controls_and_exports_only_referenced_art(self):
        report = self.export()
        record = json.loads((self.output / "cards.bundle.json").read_text())["scenes"]["1"]
        self.assertEqual(record["card"], (self.scene / "page.card").read_text())
        self.assertEqual(record["actions"], json.loads((self.scene / "service-actions.json").read_text()))
        self.assertEqual(record["data"]["label"], "确认预约")
        self.assertTrue(record["data"]["$kit"]["placements"]["icon"]["layout"]["src"].startswith("__OCTOSENSE_ASSETS__/"))
        files = {str(p.relative_to(self.output)) for p in self.output.rglob("*") if p.is_file()}
        self.assertEqual(files, {"cards.bundle.json", "cards.provenance.json", "card-assets/example/assets/icon-hashed.svg"})
        receipt = json.loads((self.output / "cards.provenance.json").read_text())
        self.assertEqual(receipt["bundle_sha256"], bundle.digest((self.output / "cards.bundle.json").read_bytes()))
        for name, sha in receipt["source_files"].items():
            self.assertEqual(bundle.digest((self.root / name).read_bytes()), sha)
        self.assertEqual(receipt["artwork_sources"]["card-assets/example/assets/icon-hashed.svg"]["declared_asset"], "cards/example/assets/icon.svg")
        self.assertEqual(report["visual_approval"], "not_assessed_by_exporter")
        self.assertFalse(receipt["screen_rasters_included"])

    def test_atomic_replacement_removes_stale_output_after_success(self):
        self.export()
        (self.output / "stale.txt").write_text("old")
        self.data["label"] = "新的短句"
        self.put("cards/example/page.data.json", self.data)
        self.export()
        self.assertFalse((self.output / "stale.txt").exists())
        self.assertEqual(json.loads((self.output / "cards.bundle.json").read_text())["scenes"]["1"]["data"]["label"], "新的短句")

    def test_bad_input_retains_previous_package(self):
        self.export()
        before = (self.output / "cards.bundle.json").read_bytes()
        self.put("art/example/assets/icon-hashed.svg", b"tampered")
        with self.assertRaisesRegex(bundle.BundleError, "no matching scene provenance"):
            self.export()
        self.assertEqual(before, (self.output / "cards.bundle.json").read_bytes())

    def test_rejects_declared_source_hash_mismatch(self):
        self.put("cards/example/assets/icon.svg", b"modified")
        with self.assertRaisesRegex(bundle.BundleError, "hash mismatch"):
            self.export()

    def test_numeric_data_is_hashed_and_changed_source_retains_previous_bundle(self):
        numeric = self.put("cards/example/data/series.json", {"values": [10, 20, 15]})
        expected = bundle.digest(numeric.read_bytes())
        self.metadata["elements"].append({"id": "chart", "data": {"path": "data/series.json", "sha256": expected}})
        self.put("cards/example/semantic-map.json", self.metadata)
        self.export()
        receipt = json.loads((self.output / "cards.provenance.json").read_text())
        self.assertEqual(receipt["source_files"]["cards/example/data/series.json"], expected)
        self.assertFalse((self.output / "data/series.json").exists())
        before = (self.output / "cards.bundle.json").read_bytes()
        self.put("cards/example/data/series.json", {"values": [10, 200, 15]})
        with self.assertRaisesRegex(bundle.BundleError, "numeric data hash mismatch"):
            self.export()
        self.assertEqual((self.output / "cards.bundle.json").read_bytes(), before)

    def test_rejects_reference_raster_even_if_declared_as_artwork(self):
        self.metadata["reference_sha256"] = bundle.digest(self.asset)
        self.put("cards/example/semantic-map.json", self.metadata)
        with self.assertRaisesRegex(bundle.BundleError, "reference raster"):
            self.export()

    def test_rejects_ui_artwork_and_embedded_raster(self):
        self.metadata["elements"][0]["asset"]["contains_ui"] = True
        self.put("cards/example/semantic-map.json", self.metadata)
        with self.assertRaisesRegex(bundle.BundleError, "includes UI"):
            self.export()
        with self.assertRaisesRegex(bundle.BundleError, "embedded image"):
            bundle.validate_svg(b'<svg><image href="data:image/png;base64,AAAA"/></svg>', "test.svg")

    def test_rejects_undeclared_image_source(self):
        self.data["$kit"]["placements"]["icon"]["layout"]["src"] = "https://example.invalid/reference.png"
        self.put("cards/example/page.data.json", self.data)
        with self.assertRaisesRegex(bundle.BundleError, "lacks declared artwork"):
            self.export()

    def test_rejects_unsafe_paths_and_ids(self):
        for unsafe in ("../outside", "/absolute", "a/../b", "a//b", "a\\b", "a/%2e", "a:stream"):
            with self.subTest(path=unsafe), self.assertRaises(bundle.BundleError):
                bundle.safe_relative(unsafe)
        self.manifest["scenes"].append(dict(self.manifest["scenes"][0]))
        self.save_manifest()
        with self.assertRaisesRegex(bundle.BundleError, "Duplicate scene"):
            self.export()

    def test_rejects_symlink_escape_and_output_overlap(self):
        outside = Path(self.temporary.name) / "outside"
        outside.mkdir()
        (self.root / "escape").symlink_to(outside, target_is_directory=True)
        self.manifest["artwork"]["root"] = "escape"
        self.save_manifest()
        with self.assertRaisesRegex(bundle.BundleError, "escapes declared root"):
            self.export()
        self.manifest["artwork"]["root"] = "art"
        self.save_manifest()
        with self.assertRaisesRegex(bundle.BundleError, "overlaps"):
            bundle.export_bundle(self.root, "flow.json", self.scene / "output")

    def test_rejects_output_symlink_and_relative_project(self):
        self.output.parent.mkdir(parents=True)
        self.output.symlink_to(self.root / "art", target_is_directory=True)
        with self.assertRaisesRegex(bundle.BundleError, "symlink"):
            self.export()
        with self.assertRaisesRegex(bundle.BundleError, "absolute"):
            bundle.export_bundle(Path("."), "flow.json", self.output)


if __name__ == "__main__":
    unittest.main()
