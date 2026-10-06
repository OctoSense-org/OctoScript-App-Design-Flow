#!/usr/bin/env python3
"""Reuse image semantic/compiler/Studio gates on external service-card projects."""
import argparse
import fcntl
import json
from pathlib import Path
import sys
from contextlib import contextmanager
from flow import read_manifest, local

IMAGE = Path(__file__).resolve().parents[1] / 'image-to-appcard'
sys.path.insert(0, str(IMAGE))


@contextmanager
def alias(design_id, directory):
    target = IMAGE / design_id
    created = False
    if target.exists() or target.is_symlink():
        if target.resolve() != directory.resolve():
            raise ValueError('Studio design ID already belongs to another source: ' + design_id)
    else:
        target.symlink_to(directory, target_is_directory=True)
        created = True
    try:
        yield
    finally:
        if created and target.is_symlink() and target.resolve() == directory.resolve():
            target.unlink()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project', required=True, type=Path)
    parser.add_argument('--manifest', required=True, type=Path)
    parser.add_argument('--stage', choices=('observe', 'measure', 'map', 'semantic', 'compile', 'capture', 'gate'), required=True)
    parser.add_argument('--launch', action='store_true')
    args = parser.parse_args()
    project = args.project.resolve()
    doc = read_manifest(args.manifest.resolve(), project)
    from semantics import preflight
    from compile import compile_page
    # The existing image adapter serializes one request per Studio host.
    # This lock coordinates flow runner capture jobs; external watchers must be stopped.
    with (IMAGE / '.service-capture.lock').open('a') as lock:
        if args.stage == 'capture':
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        build = None
        for scene in doc['scenes']:
            directory = local(project, scene['directory'])
            required = ('reference.png', 'contract.json') if args.stage in ('observe', 'measure', 'map') else ('reference.png', 'contract.json', 'mapped.json', 'semantic-map.json', 'service-actions.json')
            missing = [name for name in required if not (directory / name).is_file()]
            if missing:
                raise ValueError(f'{scene["design_id"]}: review and author measured native mapping first; missing {missing}')
            if json.loads((directory / 'contract.json').read_text())['id'] != scene['design_id']:
                raise ValueError('Scene design_id must match native contract id')
            if args.stage == 'observe':
                from observe import observe
                result = observe(directory)
            elif args.stage == 'measure':
                from measure_surfaces import measure
                if (directory / 'annotations.json').exists():
                    result = {'retained': 'annotations.json; existing source measurements preserved'}
                else:
                    result = measure(directory)
            elif args.stage == 'map':
                from observe import map_observations
                from semantics import propose
                if (directory / 'mapped.json').exists():
                    raise ValueError('Existing mapped.json retained; use a new design version for a fresh mapping')
                result = map_observations(directory)
                propose(directory)
            elif args.stage == 'semantic':
                # Authoring preflight checks the current mapping. Historical
                # capture inspection belongs to the later gate stage; an old
                # screenshot must not prevent compiling a reviewed repair.
                result = preflight(directory)
                if not result['pass']:
                    raise ValueError('Semantic mapping failed: ' + scene['design_id'])
            elif args.stage == 'compile':
                font_root = project / 'native' if (project / 'native').is_dir() else None
                result = compile_page(directory, font_root=font_root)
            elif args.stage == 'capture':
                from studio import launch, capture, click_controls
                compile_page(directory)
                if build is None:
                    build = launch() if args.launch else json.loads((IMAGE / 'studio-run.json').read_text())['build_id']
                with alias(scene['design_id'], directory):
                    capture_path = capture(scene['design_id'], build)
                    click_controls(capture_path, build)
                    result = {'build_id': build, 'capture': str(capture_path)}
            else:
                from gate import evaluate
                latest = json.loads((directory / 'latest.json').read_text())
                result = evaluate(directory, directory / 'rounds' / latest['round'])
                if not result['accepted']:
                    raise ValueError(f'{scene["design_id"]}: current native/image/semantic/visual gate has not accepted this capture')
            print(json.dumps({'scene': scene['id'], 'stage': args.stage, 'result': result}), flush=True)


if __name__ == '__main__':
    main()
