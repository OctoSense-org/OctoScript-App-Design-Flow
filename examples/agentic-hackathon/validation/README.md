# Desktop evidence — 2026-10-03

**48/48 native checks passed.** [The report](desktop-native.json) records
each assertion, injected input and SHA-256 of every final bundle file.
[Provenance](provenance.json) identifies the runtime revisions and test driver.
This is a macOS release build using the actual Makepad Metal renderer in a
hidden window, with a 412 × 892 logical viewport and 824 × 1784 captures.
Codex drove the native instrument; no app-agent model operated these tests.

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
  clean native runtime logs and final App Hub checks. File reads inspect the
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
The final run includes those repairs. Earlier raw failures remain in the
local ignored build directories.

## Still unverified

Real model answers, workspace file-tool reads, shell consent, a successful
agent draft, busy/cancel/late-response behavior and Android execution have
not been exercised. `card-host` implements no agent service, so its error
path cannot validate these. The separate OctoSense desktop shell and pinned
octos CLI build successfully; starting a real-agent rehearsal still needs
the private catalog/provider setup. A private catalog signing key requires
the person's explicit request under the [publishing rule](../../../docs/PUBLISHING.md#36-publisher-key--human).

The reviewed Android App Studio accepts storage-only previews and cannot
host these agent-capable manifests. Android must use the normal catalog/app
path in a separate test package. Neither listing currently claims Android.
These examples do not implement custom agent tools, cross-app delegation,
notifications or glance cards.

## 中文说明

**48/48 桌面原生检查通过**，包括真实控件输入、文件结果、重启、冲突复核、
防重复、撤销、重置，以及 Agent 不可用时保留人工草稿。8 张截图均已打开审查。
测试由 Codex 驱动 Makepad 原生工具执行，没有由应用中的模型操作测试。
报告记录最终 bundle 的 SHA-256；运行时版本与测试脚本哈希见 provenance.json。

真实模型回答、Agent 文件读取、宿主授权、取消/延迟回调及 Android 尚未验证。
独立 card-host 没有 Agent 服务，不能把不可用路径当成真实 Agent 成功证据。
桌面 Shell 与内核已构建；私有目录和模型配置仍需准备。按上方发布规则，
创建私钥需要用户明确授权。Android 应走独立测试包的正常目录安装路径，
不能删掉 Agent 权限后声称等价验证。示例目前只声明 macOS。
