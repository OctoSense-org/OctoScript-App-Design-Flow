# Card app template (pointer)

English | [简体中文](README.zh-CN.md)

A **card app** is a `page.card` written in L0, the declarative card language,
with its `page.data.json` and `kit/`; the host converts it to widgets. You
generate it rather than write it: use the
[image-to-card flow](../../flows/image-to-card/FLOW.md) (or the
[Sketch kit flow](../../flows/kits/sketch/FLOW.md) for a kit), then finish it
with the common hand-off in
[flows/README.md](../../flows/README.md#every-flow-follows-the-same-contract);
the bundle carries `page.card` and `kit/` instead of `main.splash`.

App Hub's [`templates/app/`](https://github.com/OctoSense-org/OctoSense-App-Hub/tree/main/templates/app)
is the metadata scaffold for a card bundle: manifest, listing, icon and agent
instructions. It has no entry file (`page.card`) and no screenshot, so the
gate refuses it even after `hub stamp`, with `entry` and `listing` refusals. Add the
flow's `page.card` and `kit/` and a real capture, and replace its placeholder
`platforms` with the platforms you tested.

For CJK text, use the plain L0 role kit (`Surface`, `TextTitle`, `TextBody`,
…) and set no `font_src`: it draws Chinese with the built-in LXGW WenKai. A
kit's `font_src` may name only one built-in font,
`makepad_widgets:resources/Inter.ttf`, which has no CJK glyphs. A `.ttf` or
`.otf` file in the bundle, named by `font_src`, passes the gate but does not
load in `card-host` today, so do not ship one
([App Hub#75](https://github.com/OctoSense-org/OctoSense-App-Hub/issues/75)).
Check the text with `MAKEPAD_SYSTEM_FONTS=0`, so that a system font cannot
hide a missing glyph.

For an app with its own logic, state and requests, use the
[script-app template](../script-app/README.md) instead.
