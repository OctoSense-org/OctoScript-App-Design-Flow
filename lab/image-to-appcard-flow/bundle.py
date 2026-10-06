#!/usr/bin/env python3
"""Export manifest-selected native L0 scenes and declared artwork, without approval claims."""
import argparse
import ctypes
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import sys
import tempfile
from urllib.parse import urlsplit
from xml.etree import ElementTree

FILES = {"card": "page.card", "data": "page.data.json", "kit": "kit/native/light/kit.json", "mapping": "mapping.json", "actions": "service-actions.json"}
HASH = re.compile(r"[0-9a-f]{64}\Z")
REFERENCE_KEYS = {"reference_sha256", "image_sha256", "original_image_sha256", "atlas_sha256", "original_atlas_sha256"}
ART_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".svg"}


class BundleError(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise BundleError(message)


def digest(content):
    return hashlib.sha256(content).hexdigest()


def safe_relative(value):
    require(isinstance(value, str) and value and not any(c in value for c in ("\\", "\0", "%", ":")), "Unsafe relative path: " + repr(value))
    path = PurePosixPath(value)
    require(not path.is_absolute() and all(part not in ("", ".", "..") for part in value.split("/")), "Unsafe relative path: " + value)
    return path


def inside(root, relative):
    relative = safe_relative(relative)
    path = root.joinpath(*relative.parts)
    require(path.resolve().is_relative_to(root.resolve()), "Path escapes declared root: " + str(relative))
    return path


def atomic_replace_directory(staged, target):
    """Swap two complete sibling directories atomically; never remove old first."""
    staged, target = Path(staged), Path(target)
    require(staged.parent == target.parent, "Atomic publication requires sibling directories")
    require(not target.is_symlink(), "Output may not be a symlink")
    if not target.exists():
        os.replace(staged, target)
        return
    require(target.is_dir(), "Output must be a directory")
    libc = ctypes.CDLL(None, use_errno=True)
    if sys.platform == "darwin":
        call = libc.renamex_np
        call.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_uint]
        result = call(os.fsencode(staged), os.fsencode(target), 2)  # RENAME_SWAP
    elif sys.platform.startswith("linux") and hasattr(libc, "renameat2"):
        call = libc.renameat2
        call.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_uint]
        result = call(-100, os.fsencode(staged), -100, os.fsencode(target), 2)  # RENAME_EXCHANGE
    else:
        raise BundleError("Atomic directory replacement requires macOS renamex_np or Linux renameat2; previous output retained")
    if result != 0:
        code = ctypes.get_errno()
        raise OSError(code, os.strerror(code), str(target))
    # The old output now occupies staged; cleanup cannot expose a partial output.
    shutil.rmtree(staged, ignore_errors=True)


def reference_hashes(document):
    values = set()
    if isinstance(document, dict):
        for key, value in document.items():
            if key in REFERENCE_KEYS and isinstance(value, str) and HASH.fullmatch(value):
                values.add(value)
            values.update(reference_hashes(value))
    elif isinstance(document, list):
        for value in document:
            values.update(reference_hashes(value))
    return values


def validate_svg(content, name):
    """An icon may not be a wrapper around a reference raster or remote resource."""
    try:
        root = ElementTree.fromstring(content)
    except ElementTree.ParseError as error:
        raise BundleError("Invalid SVG artwork: " + name) from error
    require(root.tag.rsplit("}", 1)[-1] == "svg", "Artwork is not SVG: " + name)
    for node in root.iter():
        require(node.tag.rsplit("}", 1)[-1] not in ("image", "foreignObject", "script"), "SVG contains embedded image or active content: " + name)
        for key, value in node.attrib.items():
            if key.rsplit("}", 1)[-1] == "href":
                require(value.startswith("#"), "SVG references external artwork: " + name)
    for match in re.finditer(rb"url\(([^)]*)\)", content):
        require(match.group(1).strip().strip(b"'\"").startswith(b"#"), "SVG references external CSS resource: " + name)


def validate_image_sources(value, prefix, web_sources=frozenset()):
    if isinstance(value, dict):
        for key, item in value.items():
            if key in ("src", "image_src") and isinstance(item, str):
                require(item.startswith(prefix) or (key == "src" and item in web_sources), "Image source lacks declared artwork provenance: " + item)
            validate_image_sources(item, prefix, web_sources)
    elif isinstance(value, list):
        for item in value:
            validate_image_sources(item, prefix, web_sources)


def export_bundle(project, manifest, output):
    project_input = Path(project)
    require(project_input.is_absolute(), "--project must be an absolute path")
    project = project_input.resolve()
    require(project.is_dir(), "Project directory does not exist")
    manifest_path = Path(manifest)
    if not manifest_path.is_absolute():
        manifest_path = inside(project, str(manifest_path))
    manifest_bytes = manifest_path.read_bytes()
    specification = json.loads(manifest_bytes)
    require(isinstance(specification, dict) and specification.get("schema_version") == 1, "Unsupported flow manifest schema_version")
    require(isinstance(specification.get("id"), str) and specification["id"].strip(), "Flow manifest requires id")
    artboard = specification.get("artboard")
    require(isinstance(artboard, list) and len(artboard) == 2 and all(type(n) is int and n > 0 for n in artboard), "artboard must contain two positive integers")
    scenes = specification.get("scenes")
    require(isinstance(scenes, list) and scenes, "Flow manifest must select at least one scene")
    require(all(isinstance(scene, dict) and isinstance(scene.get("id"), str) and scene["id"] for scene in scenes), "Each scene requires a nonempty string id")
    require(len({scene["id"] for scene in scenes}) == len(scenes), "Duplicate scene id")
    artwork = specification.get("artwork", {})
    require(isinstance(artwork, dict), "artwork must be an object")
    prefix = artwork.get("source_prefix")
    require(isinstance(prefix, str) and prefix.endswith("/"), "artwork.source_prefix must be an absolute URL ending in /")
    parsed = urlsplit(prefix)
    require(parsed.scheme in ("http", "https") and parsed.netloc and not parsed.username and not parsed.password and not parsed.query and not parsed.fragment, "Unsafe artwork source_prefix")
    artwork_root = inside(project, artwork.get("root"))
    require(artwork_root.is_dir(), "Declared artwork root does not exist")
    directories = [inside(project, scene.get("directory")) for scene in scenes]
    output = Path(output).absolute()
    require(not output.is_symlink(), "Output may not be a symlink")
    resolved_output = output.resolve()
    require(not project.is_relative_to(resolved_output), "Output may not replace the project or its ancestor")
    for source in [artwork_root, *directories]:
        require(not source.resolve().is_relative_to(resolved_output) and not resolved_output.is_relative_to(source.resolve()), "Output overlaps scene/artwork input: " + str(source))

    sources, records, assets, asset_proof = {}, {}, {}, {}
    forbidden_hashes = set()
    asset_pattern = re.compile(re.escape(prefix) + r'[^"\s<>]+')

    def read_source(path):
        require(path.is_file(), "Required source file missing: " + str(path))
        require(path.resolve().is_relative_to(project), "Source file escapes project: " + str(path))
        content = path.read_bytes()
        sources[str(path.relative_to(project))] = digest(content)
        return content

    if manifest_path.resolve().is_relative_to(project):
        read_source(manifest_path)
    for scene, directory in zip(scenes, directories):
        require(directory.is_dir(), "Scene directory does not exist: " + str(directory))
        declared, metadata = {}, []
        for name in ("semantic-map.json", "generation.json", "contract.json"):
            path = directory / name
            if path.exists():
                document = json.loads(read_source(path))
                metadata.append(document)
                forbidden_hashes.update(reference_hashes(document))
                if name == "semantic-map.json":
                    for element in document.get("elements", []):
                        data = element.get("data")
                        if isinstance(data, dict) and ("path" in data or "sha256" in data):
                            require(isinstance(data.get("sha256"), str) and HASH.fullmatch(data["sha256"]), "Declared numeric data requires SHA256: " + str(element.get("id")))
                            source = inside(directory, data.get("path"))
                            require(digest(read_source(source)) == data["sha256"], "Declared numeric data hash mismatch: " + str(source))
                        asset = element.get("asset")
                        if not asset:
                            continue
                        require(isinstance(asset, dict) and isinstance(asset.get("sha256"), str) and HASH.fullmatch(asset["sha256"]), "Declared artwork requires SHA256: " + str(element.get("id")))
                        source = inside(directory, asset.get("path"))
                        require(source.suffix.lower() in ART_EXTENSIONS, "Unsupported artwork type: " + str(source))
                        raw = read_source(source)
                        require(digest(raw) == asset["sha256"], "Declared artwork hash mismatch: " + str(source))
                        if source.suffix.lower() == ".svg":
                            validate_svg(raw, str(source))
                        method = asset.get("method")
                        require(method in ("source_crop", "reference_svg", "generated", "generated_artwork", "provided_asset", "original_artwork"), "Unknown artwork provenance method: " + str(method))
                        require(asset.get("contains_ui") is not True, "Artwork declaration includes UI: " + str(source))
                        require(source.suffix.lower() == ".svg" or asset.get("contains_ui") is False, "Raster artwork must explicitly declare contains_ui=false: " + str(source))
                        declared[asset["sha256"]] = {"scene_id": scene["id"], "element_id": element.get("id"), "declared_asset": str(source.relative_to(project)), "declaration": str(path.relative_to(project)), "method": method, "reference_sha256": asset.get("reference_sha256")}
        for name in ("reference.png", "source.png", "atlas.png"):
            reference = directory / name
            if reference.is_file():
                forbidden_hashes.add(digest(reference.read_bytes()))
        # Inline HTML belongs to an explicitly typed native WebView, not artwork.
        # Do not exempt arbitrary data URLs or image placements.
        scene_data = json.loads(read_source(directory / FILES["data"]))
        scene_kit = json.loads(read_source(directory / FILES["kit"]))
        web_sources = set()
        for placement in scene_data.get("$kit", {}).get("placements", {}).values():
            component = scene_kit.get("components", {}).get(placement.get("component"), {})
            src = placement.get("layout", {}).get("src", "")
            if component.get("style", {}).get("t") == "web" and src.startswith("data:text/html;charset=utf-8;base64,"):
                import base64
                try:
                    base64.b64decode(src.split(",", 1)[1], validate=True).decode("utf-8")
                except (ValueError, UnicodeError) as error:
                    raise BundleError("Invalid inline WebView document") from error
                web_sources.add(src)
        record, urls = {}, set()
        for key, name in FILES.items():
            text = read_source(directory / name).decode("utf-8")
            require("data:image/" not in text.lower() and "file://" not in text.lower(), "Embedded or local images are not declared artwork: " + name)
            if key != "card":
                validate_image_sources(json.loads(text), prefix, web_sources)
            urls.update(asset_pattern.findall(text))
            text = text.replace(prefix, "__OCTOSENSE_ASSETS__/")
            record[key] = text if key == "card" else json.loads(text)
        for url in sorted(urls):
            relative = url[len(prefix):]
            source = inside(artwork_root, relative)
            require(source.suffix.lower() in ART_EXTENSIONS, "Unsupported referenced artwork type: " + relative)
            raw = read_source(source)
            asset_hash = digest(raw)
            require(asset_hash in declared, "Referenced artwork has no matching scene provenance: " + relative)
            require(asset_hash not in forbidden_hashes, "Source reference raster may not be shipped: " + relative)
            destination = "card-assets/" + str(safe_relative(relative))
            require(destination not in assets or assets[destination] == raw, "Conflicting artwork destination: " + destination)
            assets[destination] = raw
            asset_proof[destination] = {**declared[asset_hash], "project_path": str(source.relative_to(project)), "sha256": asset_hash}
        records[scene["id"]] = record
    # A later scene can identify an earlier asset as a source reference.
    for name, raw in assets.items():
        require(digest(raw) not in forbidden_hashes, "Known source reference may not be shipped: " + name)
    bundle = {"schemaVersion": 1, "id": specification["id"], "artboard": artboard, "scenes": records,
              "renderer": "native Makepad L0 widgets in WebAssembly", "simulation": True}
    bundle_bytes = json.dumps(bundle, ensure_ascii=False, separators=(",", ":")).encode()
    receipt = {"schema_version": 1, "id": specification["id"], "manifest_sha256": digest(manifest_bytes),
               "source_files": sources, "artwork": {name: digest(raw) for name, raw in sorted(assets.items())},
               "artwork_sources": asset_proof, "bundle_sha256": digest(bundle_bytes), "screen_rasters_included": False,
               "reference_hashes_excluded": sorted(forbidden_hashes), "visual_approval": "not_assessed_by_exporter",
               "asset_policy": "Only referenced assets matching scene declarations; known reference and atlas hashes excluded"}
    output.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix="." + output.name + "-staged-", dir=output.parent))
    try:
        (stage / "cards.bundle.json").write_bytes(bundle_bytes)
        for name, raw in assets.items():
            target = stage / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(raw)
        (stage / "cards.provenance.json").write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n")
        for path, expected in sources.items():
            require(digest(inside(project, path).read_bytes()) == expected, "Source changed during export: " + path)
        atomic_replace_directory(stage, output)
    finally:
        if stage.exists():
            shutil.rmtree(stage, ignore_errors=True)
    return {"passed": True, "id": specification["id"], "scenes": len(records), "artwork_assets": len(assets),
            "output": str(output), "bundle_sha256": receipt["bundle_sha256"], "visual_approval": receipt["visual_approval"]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", required=True, type=Path)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    try:
        print(json.dumps(export_bundle(args.project, args.manifest, args.output), ensure_ascii=False))
    except (BundleError, OSError, ValueError) as error:
        print(json.dumps({"passed": False, "error": str(error), "previous_output_retained": True}, ensure_ascii=False), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
