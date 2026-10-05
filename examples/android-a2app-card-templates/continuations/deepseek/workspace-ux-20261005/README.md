# Phone workspace caption and navigation corrections

English | [简体中文](README.zh-CN.md)

On 2026-10-05, Glance workspace acceptance on a OnePlus 6 found that the
DeepSeek Photo and YouTube cards clipped their offline-data explanation.
DeepSeek v4 flash read both actual phone screenshots with `view_image` on
Android and changed each caption to `width: .fill`. The operator provided
feedback and copied the resulting files without editing their source.

The two `.glance.card` files supersede the corresponding `glance.card` files in
[turn 12](../turn-12/README.md). The six `.main.splash` files replace their
families' `bundle/main.splash`; all fixture data and other bundle files remain
unchanged.
[Provenance](provenance.json) records both successful model edits and the
original/output SHA-256 hashes; it excludes credentials and private reasoning.

The dark Paper host also exposed clipped navigation controls in all six Splash
programs. DeepSeek viewed the actual capture and supplied a first typography
patch, but the operator found that it still clipped States. After that screenshot
was returned to DeepSeek, it reduced `NavBtn` to an explicit 11-point font and
6-point padding, keeping the 44-point height. The second Android output fits all
four controls on the OnePlus 6. Both successive mutations are preserved and
replayed; the unsuccessful first attempt is not counted as a pass.

Navigation evidence: [before](screenshots/navigation-before.png),
[first attempt](screenshots/navigation-first-attempt.png), final
[Mail](screenshots/mail-navigation-after.png),
[Calendar](screenshots/calendar-navigation-after.png),
[News](screenshots/news-navigation-after.png),
[Finance](screenshots/finance-navigation-after.png),
[Photos](screenshots/photo-navigation-after.png),
[YouTube](screenshots/youtube-navigation-after.png).

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
`2026100503` for captions and `2026100504` for navigation, based on `a2a0524d`
plus the workspace acceptance changes.
From this directory, the executed source verification command is:

```sh
python3 verify.py
```

The verifier replays each recorded one-occurrence replacement against the
immutable originals and compares both file hashes. It does not claim a new
App Hub/store acceptance or an SMTP/video/photo integration test.
