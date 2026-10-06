# Inbox Assistant local evidence — 2026-10-06

Codex authored the sample, drove the real Makepad instrument and inspected the
original native PNGs. All messages, recipients and edits here are fictional.
This page records the earlier standalone fixture checks. They used no Google
account, model inference, real email, physical approval or phone interaction.
The later [installed full-shell acceptance](integrated/README.md) separately
exercises the actual peer and real DeepSeek with synthetic Gmail.

The machine-readable [interaction receipt](run-receipt.json) and
[restart receipt](restart-receipt.json) identify source, workspace template,
manifest, driver, native binary and captured images by SHA-256. The screenshots
are 824 × 1784 native captures from a 412 × 892 logical hidden macOS window,
including the host caption. They are not browser mockups or synthesized images.

## Commands and observations

From the App Design Flow root:

```sh
tools/octo doctor
python3 examples/connected-apps/inbox/build_bundle.py
tools/octo run examples/connected-apps/inbox/bundle --port 8194 --hidden --detach
python3 examples/connected-apps/inbox/verify_native.py --port 8194
curl --silent http://127.0.0.1:8194/gq
tools/octo run examples/connected-apps/inbox/bundle --port 8194 --hidden --detach
python3 examples/connected-apps/inbox/verify_native.py --port 8194 --restart-check
curl --silent http://127.0.0.1:8194/gq
tools/octo check examples/connected-apps/inbox/bundle
```

The driver uses native widget coordinates, pointer input, command-A and text
input; it does not set widget state through a mock API. It verifies:

| Journey | Observed result |
| --- | --- |
| Startup and second item | Fictional inbox is labelled; the second button opens Harbor Delivery, not the first clinic item |
| Editing | Exact multiline text including `谢谢。` survives Reply → Chat → Reply |
| Missing peer | Chat displays the actual `octos` service error and preserves the saved draft |
| Missing OAuth | Connect Google displays the actual `auth` service error |
| Sending fixture | Review & Send saves the fictional draft and explicitly refuses live sending |
| Folder states | Important shows two fixtures; Sent is empty; Inbox restores all three |
| Restart | The same delivery draft and exact edited text are restored |

The original captures are [Inbox](01-inbox.png), [Reply](02-reply.png),
[unavailable peer](03-chat-unavailable.png) and [restart](04-restart.png).
Current individual PNG inspection shows the title, sender, adjacent Email / Reply /
Chat navigation, editable body, Save/Review actions and reachable chat composer.
The Inbox list is a `ScrollYView`; the workspace has its own content area. These
checks do not exercise Android soft-keyboard resizing or actual Glance expansion.

The final `hub check --allow-unsigned` result is **PASSED** for
`org.octosense.samples.inbox`, with the expected unsigned warning and explicit
publisher placeholders. The matching Hub policy is
`85ccc533ef4f86853c67c6b3b3e6381773afbdab`. An earlier old `hub` binary refused the
new Gmail event aliases; rebuilding the matching tool resolved that admission
failure. `hub scan` produced eight review questions, answered locally in
`build/REVIEW-ANSWERS.md`. Admission is not publication or live-provider acceptance.

## Strict installation boundary

The companion OctoSense `connected-install` example installed this exact Inbox
bundle through a newly signed private catalog and separately signed bundle,
then reopened the policy. It rejected a modified installed source and another
app’s staging, confirmed source bundles were unchanged and removed its temporary
profile. No unsigned/developer bypass was used. Keys existed only in memory.
The executed command, from the OctoSense root, was:

```sh
cargo run --locked -p octosense-shell --features mobile-apps --example connected-install -- ../OctoScript-App-Design-Flow/examples/connected-apps/github-notes/bundle ../OctoScript-App-Design-Flow/examples/connected-apps/inbox/bundle ../OctoScript-App-Design-Flow/examples/connected-apps/google-calendar/bundle
```

Its local ignored receipt is `target/connected-install/receipt.json` in that
checkout. Inbox bundle digest:
`0b005c320205df3b59f61174f717a11456f3534e577cd49c30fd70eb4c1bca5e`.
This verifies signed Store installation and tamper boundaries; it does not
exercise the installed UI, OAuth consent, provider requests or the model.

## Connector and event tests

In the companion OctoSense checkout:

```sh
cargo test -p octosense-oauth-service --lib inbox
cargo check -p octosense-oauth-service --features host
```

The Inbox/durable-event tests pass **15 tests**. They cover mixed/synthetic
provenance rejection; exact revision and immutable review snapshot; cancellation,
expiry, cross-app review, account replacement and replay; durable claim before
transport; accepted versus unknown outcomes; threaded MIME and header injection;
typed deleted-message versus transient-provider errors; complete history-page
commit; expired-cursor rescan; stale leases and retries; event-account isolation;
full bounded queue reopening; baseline readiness; and retaining an already
verified publication decision across interrupted turns. A successful model
answer without a durable decision cannot acknowledge an event. Provider calls
use deterministic in-memory credentials and fake transports.

## Failures and limits

Earlier native captures under `failures/` show an intermittent missing Ask or
Reply control despite its widget remaining in the snapshot. Repeated fresh
launches and the current candidate have not reproduced those missing controls.
There is no app visibility-toggle workaround and no claim that the renderer's
root cause has been repaired. Static title/sender/status ink was separately
confirmed in original PNGs; a misleading grouped-image display was not counted
as a product defect.

Also repaired during development: absent optional message fields accessed as
mandatory Splash properties, unreadable focused placeholders, and reliance on
one-shot model output for draft chat. Current chat uses the account's app peer
and reads the authoritative host draft after its tools finish.

The standalone fixture alone did not verify actual peers, models or Shell
Glance; see the later integrated run above for those bounded checks. Still not
verified: live Google sign-in/read/send, broad relevance quality, cross-app
calendar booking, physical native send approval, recipient delivery,
Android keyboard/lifecycle/background scheduling, Linux or Windows. Android
Google authorization is unsupported until its native adapter is implemented.
No numerical UX score or production sign-off is claimed.

## 中文说明

以上是 Codex 使用真实 Makepad instrument 对虚构数据执行的本地测试。交互、
重启回执记录准确源码和截图摘要；它们不代表真实 Google 登录、模型筛选、
手机通知或发送成功。当前截图中的导航、编辑器和聊天输入可见。早期按钮偶发
消失的原图仍保留，当前无法复现，不能据此宣称底层渲染问题已修复。应用尚未
签名或发布；后续完整 Shell 测试已单独验证真实 DeepSeek 与模拟 Gmail 的代理、
工具和 Glance 流程，详见集成证据。真实 Google 账户、送达及 OnePlus 6 仍待验证。
