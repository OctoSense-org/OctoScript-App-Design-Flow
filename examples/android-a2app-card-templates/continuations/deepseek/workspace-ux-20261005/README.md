# Phone workspace caption correction

English | [简体中文](README.zh-CN.md)

On 2026-10-05, Glance workspace acceptance on a OnePlus 6 found that the
DeepSeek Photo and YouTube cards clipped their offline-data explanation.
DeepSeek v4 flash read both actual phone screenshots with `view_image` on
Android and changed each caption to `width: .fill`. The operator provided
feedback and copied the resulting files without editing their source.

These two files supersede only the corresponding `glance.card` files in
[turn 12](../turn-12/README.md). Data and Splash bundles are unchanged.
[Provenance](provenance.json) records both successful model edits and the
original/output SHA-256 hashes; it excludes credentials and private reasoning.

The follow-up phone captures below show the complete explanation after the
Favorite / Watch later action. Collapse/reopen preserved that local choice;
the host's Chat composer remained reachable with the Android keyboard.
The cards still use fictional data and cannot load media or perform external
actions. This correction does not establish a new overall UX score.

| Card | Before | After |
| --- | --- | --- |
| Photos | [Clipped caption](screenshots/photo-before.png) | [Wrapped caption](screenshots/photo-after.png) |
| YouTube | [Clipped caption](screenshots/youtube-before.png) | [Wrapped caption](screenshots/youtube-after.png) |

Verified on OctoSense's isolated Android acceptance package, build
`2026100503`, based on `a2a0524d` plus the workspace acceptance changes.
From this directory, the executed source verification command is:

```sh
python3 verify.py
```

The verifier replays the recorded one-occurrence replacement against the
immutable originals and compares both file hashes. It does not claim a new
App Hub/store acceptance or an SMTP/video/photo integration test.
