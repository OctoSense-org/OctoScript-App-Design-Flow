# Desktop evidence — 2026-10-03

**51/51 native checks passed.** [The report](desktop-native.json) records
each assertion, injected input and SHA-256 of every final bundle file.
[Provenance](provenance.json) identifies the runtime revisions and test driver.
This is a macOS release build using the actual Makepad Metal renderer in a
hidden window, with a 412 × 892 logical viewport and 824 × 1784 captures.
Codex drove the native instrument; no app-agent model operated these tests.

**Follow-up:** [DeepSeek and OnePlus 6 checks](LIVE-SHELL.md) now cover the
real shell path. This desktop report and its original provenance remain
unchanged: their scope is the standalone host's local/unavailable behavior.

Reproduce from the repository root after the normal native setup:

```sh
python3 -B examples/agentic-hackathon/scripts/verify_native.py
```

The driver preserves a new report, state, logs and gate output in ignored
`build/<timestamp>/`. It closes only its own instances. A new run updates
bundle screenshots and stamps; review those captures and replace this frozen
report only after checking the final files. Do not edit recorded hashes to
make old evidence match changed source.

## Verified

- Email: populated inbox, blank-draft rejection, exact recipient, edited
  reply, second-message identity, one local delivery, immutable delivery
  receipt, targeted undo, handled-message filter, newsletter access,
  persistence, reset and preservation of a human draft after an unavailable
  agent request.
- Calendar: populated busy events, required selection, interval conflict,
  first-free fallback, exact attendees, conflict introduced after review,
  refusal without a write, successful alternative, duplicate prevention,
  persistence, targeted undo, no-slot state and reset.
- Both: blank questions, explicit standalone-host agent-unavailable results,
  preserved submitted questions, clean native runtime logs and final App Hub checks. File reads inspect the
  local action results; a screen label alone is not considered a saved action.
- All eight bundle captures were visually inspected. Review screens show the
  recipient or attendees, full proposal and confirmation controls. Receipt
  screens distinguish saved local actions from real account operations.

Final gate result excerpts:

```text
demo.email-action 0.1.0 — PASSED
  [warning] publisher-signature: unsigned: accountability rests on the hub alone
demo.meeting-planner 0.1.0 — PASSED
  [warning] publisher-signature: unsigned: accountability rests on the hub alone
```

The wrapper also reports publisher/support/privacy template placeholders.
These deliberately remain for the contestant to replace. Admission is not
independent review, a store submission or authorization to publish.
[Author answers](../REVIEW-ANSWERS.md) cover all eight scanner questions.

## Failures caught and repaired

Native execution rejected an unsupported `RightWrap` enum; the multiline
draft now uses the runtime's `Right{wrap: true}`. Pixel review found flat
buttons whose default text had no contrast; both apps now specify readable
foreground/background colors. Reusing a scroller retained its offset between
pages and hid confirmation details; each page now owns a separate scroller.
Tests also caught the need to preserve the committed reply in its receipt
after later draft edits and to derive the inbox count from handled state.
Final screenshot review also caught the question field reverting to its default after an agent error; submitted questions now remain visible for review and retry. The final run includes those repairs. Earlier raw failures remain in the
local ignored build directories.

## Separate live validation

The [follow-up report](LIVE-SHELL.md) records successful desktop and OnePlus 6
DeepSeek turns, consent, Android scoped file reads and confirmation flows.
It also records local Stop behavior, restart persistence and remaining limits.
`card-host` implements no agent service; none of those results is inferred
from its unavailable response. The private catalog keys and provider reuse
were authorized for the isolated rehearsal; no credentials enter this repo.

The phone ran normal catalog-admitted apps in a separate test package.
Android App Studio's storage-only preview is not equivalent coverage.
The reference listings remain the original macOS metadata; this is a device
rehearsal, not an Android App Hub release. These examples do not implement
custom agent tools, cross-app delegation, notifications or glance cards.

## 中文说明

**51/51 桌面原生检查通过**，包括真实控件输入、文件结果、重启、冲突复核、
防重复、撤销、重置，以及 Agent 不可用时保留人工草稿。8 张截图均已打开审查。
测试由 Codex 驱动 Makepad 原生工具执行，没有由应用中的模型操作测试。
报告记录最终 bundle 的 SHA-256；运行时版本与测试脚本哈希见 provenance.json。

后续的[真实模型验证](LIVE-SHELL.md)已覆盖桌面和 OnePlus 6 的 DeepSeek 回答、
授权、手机受限文件读取及确认流程，并记录本地停止、重启持久化和剩余限制。
独立 card-host 没有 Agent 服务，不能把不可用路径当成真实 Agent 成功证据。
私有目录签名和提供商复用已获用户授权，凭据不进入仓库。
Android 使用独立测试包的正常目录应用宿主，保留全部 Agent 权限。
商店列表仍是原始 macOS 元数据；本次是设备验证，不是 Android 商店发布。
