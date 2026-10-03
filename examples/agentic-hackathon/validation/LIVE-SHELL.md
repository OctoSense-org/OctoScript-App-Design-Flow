# DeepSeek desktop and OnePlus 6 rehearsal — 2026-10-03

**Both apps completed real DeepSeek V4 Flash turns on desktop and Android.**
On the OnePlus 6, the email agent read `inbox.json` and `state.json`; the meeting
agent read `calendar.json` and `state.json`. The scoped tool audit records
successful `files.read` operations for the correct app. This is stronger
evidence than a model merely saying it read a file.

[Structured evidence](live-shell.json) records the actual replies, fake saved
records, tool-audit fields, source/APK hashes and exact runtime patch lock.
[Phone instructions](../ANDROID.md) explain how to open the installed demo.
No provider profile, credentials, signing keys, full session or model reasoning
is included. The original [51-check desktop report](README.md) is unchanged.

## What ran

| Check | Desktop shell | OnePlus 6 / Android 15 |
| --- | --- | --- |
| Real provider | DeepSeek V4 Flash, no fallback provider | Same model in the isolated host's private configuration |
| App-agent consent | Allowed each app through its host sheet | Separate first-use consent for each app; retried after allowing |
| Email | AI draft → recipient review → one fake outbox entry | Same flow; saved body equals the reviewed draft; exact `maya@example.invalid` recipient |
| Calendar | Recommend 14:00 → add conflict → refuse → confirm 15:30 | Same flow, with `booking: null` after refusal and `slot-1530` after confirmation |
| File tools | Not independently audited in this follow-up | Both peers used successful scoped file reads; paths matched session tool calls |
| Whole-package restart | Covered for local behavior in the standalone report | Both apps reopened with their saved action and receipt intact |
| Stop | Not exercised here | Busy screen → Stop → idle/stopped screen still visible after 30+ seconds; booking unchanged |

Codex operated the Makepad desktop instrument and Android ADB input. DeepSeek
produced app-agent answers and made scoped file-tool calls; it did not operate
the screen. Phone screenshots are unmodified `adb exec-out screencap -p`
captures at 1080 × 2280, each opened and visually reviewed. This is actual
Android execution, not the desktop hidden renderer or App Studio preview.

## Inspect the phone journey

| State | Capture |
| --- | --- |
| Host consent, limited to this app | [Email consent](phone/email-consent.png) |
| Real AI draft | [Email answer](phone/email-answer.png) |
| Exact recipient and draft before the write | [Email review](phone/email-review.png) |
| One delivery still present after restart | [Email receipt](phone/email-restarted-receipt.png) |
| DeepSeek recommends the first shared free slot | [Calendar answer](phone/meeting-answer.png) |
| Stale proposal refused without booking | [Calendar conflict](phone/meeting-conflict.png) |
| Exact alternative and attendees | [15:30 review](phone/meeting-review1530.png) |
| Saved meeting still present after restart | [Meeting receipt](phone/meeting-restarted.png) |
| Local Stop remains idle | [Stopped agent](phone/meeting-stopped-later.png) |

The model's recommendations are separate from stored actions. The calendar
recommendation could not override the updated overlap check, and the email
draft created no outbox entry before explicit confirmation. All addresses,
events and outgoing records were fictional; no real account was connected.

## Provenance and setup

- App source: Design Flow `9e8c7ee`. All phone bundle files except signed
  manifests match the repository byte-for-byte. Signing canonicalized
  manifest defaults and added a disposable test signature; the bundle digest
  stayed unchanged. Both versions' file hashes are in the structured evidence.
- Shell: OctoSense `ccf8013`, App Hub dependency `0d5b47a`, octos `056173e`.
  Makepad base `c155f61d` includes that OctoSense commit's **locked product
  patch stack**. `python3 tools/setup.py --check` passed. No runtime source
  changes or increased script budget were introduced for these samples.
- Desktop Store installed both privately signed bundles after normal install
  approval. Those installed bundles/catalog were copied to a new phone test
  sandbox; desktop app state and consent were not copied. Android performed
  normal app admission and obtained its own app-agent consent.
- APK: `dev.makepad.octosense.hackathon`, label **Hackathon Demos**, ARM64
  release build with debug inspection enabled. Its SHA-256 is recorded. It
  neither replaced the existing Home/Bridge nor became the default launcher.
- Provider configuration and temporary catalog signing were authorized for
  this rehearsal. Only the existing DeepSeek configuration was reused. The
  apps access `octos.turn.start`; they never receive a provider credential.

## Failures and remaining limits

The first automated direct cold launch of Email Action failed with
`script time budget exceeded` at Splash line 6, and `view=false`. Both a
native frame capture and the visible Android screen were blank. It was an
execution failure, not missing screenshot permission. Opening **App Hub**
first, waiting for its catalog and tapping **Open** worked, including after
full package restarts. That is the validated demo entry. The cold direct-launch
bug remains unresolved; do not infer a general startup guarantee.

The model's calendar Markdown appears as literal formatting markers. It is
readable, but not a polished rich-text presentation. Selecting a slot redraws
the plan at the top, so the person scrolls to review again. Dragging over a
button can capture the gesture; swiping over text or using the right scrollbar
worked. The floating system control can overlap the sample's content.

Stop was verified locally. This run did not force a late callback or prove
that the remote provider stopped billing. Fresh Android Store downloading,
the full Android offline/undo/duplicate matrix, other devices, real mail or
calendar integration, system-agent routing, cross-app delegation, notifications
and glance publication remain outside this evidence. The reference listings
retain their original macOS metadata; there was no public App Hub submission.

## 中文说明

两个示例均已在桌面和 OnePlus 6 上接通 DeepSeek V4 Flash。手机审计确认：
邮件 Agent 读取自身 `inbox.json`、`state.json`；日历 Agent 读取自身
`calendar.json`、`state.json`。邮件审核后只新增一条本地发件记录；日历新增
14:00 冲突后拒绝确认，再成功保存 15:30。两者回执均在整包重启后保留。

测试由 Codex 操作真实控件，DeepSeek 负责回答和文件工具调用，没有操作屏幕。
手机本地 Stop 已验证，强制延迟回调和提供商实际取消仍未验证。首次自动直接
冷启动曾因 64 ms 预算产生空白，已验证的入口是先开 App Hub 再点 Open。
该启动问题、Markdown 原样显示和滚动位置重置均如实保留，不把设备验证写成
生产发布或全平台通过。
