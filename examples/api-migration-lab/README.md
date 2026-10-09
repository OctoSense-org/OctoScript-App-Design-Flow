# API Migration Lab

English | [简体中文](README.zh-CN.md)

A small development app for the request-contract repairs in
[the migration guide](../../docs/SUBMISSION-API-MIGRATIONS.md). Edit a note,
write or request a summary, save it, and publish/withdraw one stable Glance
card. A failed service call leaves the local draft intact.

`model.complete` uses `task`, `input`, a bounded JSON Schema and
`r.data.output`. Glance uses an admitted `brief.splash` template, `initial`
and `card_id` in both publication and withdrawal. The manifest grants only
`storage`, `model` and `glance`. This example offers no app agent and invents
no Chat tab, account or login form.

## Run and validate

From the App Flow root, with `hub` and `card-host` already built:

```sh
tools/octo doctor
tools/octo run examples/api-migration-lab/bundle --hidden --detach --port 8197
tools/octo shot 8197 /tmp/api-migration-lab.png
curl -s http://127.0.0.1:8197/quit
tools/octo check examples/api-migration-lab/bundle
```

Automated native input and restart validation (supply your built binary paths;
the output directory must not exist):

```sh
python3 examples/api-migration-lab/verify-native.py \
  --card-host /path/to/card-host --hub /path/to/hub \
  --output /tmp/api-migration-lab-evidence
```

The driver copies the bundle to an isolated directory, runs hidden native
windows, types multiline English/Chinese content, exercises empty input,
saves, calls genuinely absent services and restarts the process. It records
binary/source/driver hashes, real screenshots, widget snapshots and logs,
and stops only the processes it starts. Failure also writes `result.json`.
It neither contacts a model nor accesses any normal application profile.

## Evidence and limits

Native macOS behavior checks passed with the cached `card-host` identified
in [validation.json](validation.json): populated startup, empty-input refusal,
editing, saving, both service-error paths and exact restart persistence.
The committed [screenshot](bundle/screenshots/01-main.png) is the real
post-restart native capture, inspected with system fonts disabled. Earlier
captures from this older host contained incomplete repaint frames; those are
not visual acceptance evidence. No UI-soak or performance score is claimed.

`card-host` answers that no service serves `model` or `glance`. Successful
inference, actual Glance publication/withdrawal, summary expansion, a public
release and every phone platform remain **unverified**. Use a configured
compatible OctoSense shell for those checks. This unsigned example is not an
App Hub submission; no human publishing or visual approval is implied.
