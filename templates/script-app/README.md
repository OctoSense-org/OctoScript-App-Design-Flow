# Script app template

English | [简体中文](README.zh-CN.md)

A runnable OctoSense script app: **My Notes** (type a note, keep it in the
app's storage, tap it to remove it). `tools/octo new <dir>` copies it and
sets the id and name; run it with `tools/octo run <dir>/bundle`.

```text
script-app/
  README.md        this file (not copied)
  AGENTS.md        instructions for an agent working in the new app's repository (copied)
  .gitignore       keeps keys, build output and .local-state out of git (copied)
  bundle/          the app; the only thing ever submitted (copied)
    manifest.json  id my-notes, version 0.1.0, capability storage
    listing.json   store text: EVERY publisher value is a placeholder
    main.splash    the program
    assets/icon.svg
```

What it demonstrates, all verified in `card-host`: state in top-level `let`s,
a loader started with `start_timeout(0.05, …)`, `fs.exists/read/write` in the
app's jail, `parse_json`/`to_json`, `ui.<id>.text()/set_text()/render()`, an
`on_render` list with an empty state, `ButtonFlat{on_click}`, and
`GestureView{on_tap}` rows.

Deliberately incomplete, so a copy cannot be published by accident:

- `listing.json` names `screenshots/01-main.png`, which does not exist. The
  gate refuses the bundle until you capture a real screenshot
  (`tools/octo shot`). Do not add a dummy image.
- The publisher name, support URL and privacy-policy URL are placeholders
  (`tools/octo check` notes them). A person replaces them.
- `platforms` says `android`; replace it with what you actually ran it on
  (a `card-host` run on a Mac is `macos`). A person confirms the claim.

Origin: a draft script-app template made alongside OctoSense-App-Hub (never
committed there; App Hub's `templates/app/` is the card-app starter), with one fix: the list's empty state is a separate `if`
before the `for`, because `if … else for …` in `on_render` drew nothing for
the empty branch and left stale rows. Next steps: [docs/QUICKSTART.md](../../docs/QUICKSTART.md).
