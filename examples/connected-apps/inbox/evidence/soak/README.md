# Inbox macOS UX soak — 2026-10-06

This run exercises the signed Inbox sample inside the actual hidden native
OctoSense Shell. Makepad injects pointer, key, text and scroll events. Gmail is a
compile-time acceptance fixture; DeepSeek v4 Flash performs real model inference.
Codex drives the native inputs and inspects original pixels. No real Google
account, delivery or physical send approval is exercised.

## Findings preserved before repair

The [original first-review capture](before-overlapping-review.png) shows the
native reply review overlapping the underlying Inbox editor. This is a visual
failure even though draft-state and approval checks succeeded. The second
attempt was stopped after 10 completed cycles (184.851 seconds), with no observed
instrument error. Its [receipt](before-receipt.json) and
[cycle data](before-cycles.json) remain separate from any repaired run. A later
review in that attempt was opaque, so the defect was intermittent/first-open,
not present in every sampled frame.

An [earlier attempt](first-instrument-failure.json) stopped after four completed
cycles when a waited native input returned HTTP 404. Its driver did not preserve
the response body, so the cause is unknown. The updated driver records response
bodies and never replays an uncertain input. A frame-wait timeout counts as a
responsiveness failure even if subsequent durable state proves the action was
applied.

The [earlier model receipt](before-model-receipt.json) records that isolated case:
clinic publication in 11.766 seconds, newsletter quiet decision in 6.980 seconds,
and the requested draft change in 9.594 seconds. The chat called message, draft
read, draft edit and draft read-back tools. None reported a tool error. This
model phase is completed; later native soak runs reuse its saved case and
identify their runtime binary separately rather than fabricating another turn.

## Repairs and final-source validation

Glance now draws the host review alone in its own script isolate while keeping
the Inbox VM and draft resident. The [first repaired review](fixed-first-review.png)
was inspected independently by the Inbox and Notes reviewers: its exact reply,
recipient and actions are readable without editor overlap. Inbox also refreshes
its actual local `gmail.events.status` every three seconds while its list is
open, with in-flight and bound-account guards. This does not fetch Gmail, call a
model or manufacture a monitoring state. The visible label changes to baseline
ready without pressing Refresh.

The fresh signed bundle digest is
`2ca58e32e871a5336c878691a0d6b257409a4208428f3731ee82fcae2e097caa`.
Its [real model receipt](model-receipt.json) records clinic publication in
19.325 seconds, newsletter quiet decision in 9.652 seconds and shared-draft
chat editing in 9.153 seconds, with no tool errors. All used the repaired
`8a146802…` binary. The subsequent sustained run reuses this same saved model
case and signed installation, without generating or editing a model trace.

A first attempt with the repaired source stopped after six completed cycles
because a native input returned an explicit frame-submission failure in
19.136 ms ([receipt](frame-submission-failure.json),
[exact response](frame-submission-errors.json)). This is an instrument/rendering
failure, not a five-second timeout. Makepad `poll_with_present` calls `apply`
before requesting the input's frame, then emits this error on `Some(false)`.
The final driver never replays this applied input: it records the failed
acknowledgement, obtains a read-only recovery frame and requires subsequent
exact-state assertions. It retains all such errors separately from functional
completion. An additional zero-cycle driver attempt found the remote port ready
before the window list; the driver now waits for the owned native window.

## Sustained run result

**33/33 functional cycles passed over 610.002 seconds, followed by cold restart.**
The [final receipt](soak-receipt.json), [all cycles](cycles.json) and
[native timings](native-input-timings.json) retain the exact bundle, binary,
Glance source and instrument source hashes. The final draft is revision 43;
its exact body survived the restart and native review. There were zero provider
send attempts and no physical approval. All owned Shell/kernel processes exited
and the instrument port closed.

The run executed 1,204 native input requests. Their frame-wait round-trip p50
was **8.168 ms**, p95 **18.548 ms**, and maximum **60.990 ms**. Two requests
returned the explicit frame-submission error (38.530 ms and 5.889 ms), so this is
**not a clean instrument/rendering pass**. There were no five-second frame-wait
timeouts. Neither failed acknowledgement caused an input replay. Read-only
recovery frames and the subsequent exact draft/state checks passed. The
[error responses](input-errors.json), [first recovery](input-error-01.png) and
[second recovery](input-error-02.png) are preserved. The original failure remains
unresolved in Makepad; the completion result does not hide it.

Process RSS increased from **510.02 MiB to 570.70 MiB** (+60.69 MiB). It includes
the entire Shell, rendering/capture caches and the retained app. This finite
loaded-host run establishes neither a memory leak nor leak freedom. It is not
an idle benchmark, a frames-per-second measurement or physical display latency.

Original pixels inspected individually:

- [Long review scrolled through line 24](cycle-10-review.png), with bottom actions reachable.
- [Final cycle review](cycle-33-review.png), opaque and still bound to the exact unsent reply.
- [Cold restored editable draft](05-cold-reply.png), showing saved revision 43.
- [Cold native review](06-cold-review.png), showing the same recipient, subject and body.

The first repaired review was also independently inspected by the Notes agent
and root reviewer. These are bounded visual checks, not a numerical UX grade.
The model trace proves the actual draft edit/read-back; an early chat capture
was taken before its UI callback settled and is not offered as a terminal
assistant-response screenshot. Native unsent-composer probes during the soak
are explicitly operator input, not additional model turns.

The instrument ordering is visible in
[Makepad `poll_with_present`](https://github.com/OctoSense-org/makepad/blob/c155f61d0e1600d2ec474209374444a38a09a470/platform/src/remote.rs#L1007):
`apply` precedes frame submission; a submission failure must never be treated as
permission to resend an action. The driver binds the inspected source hash as
well as the executable hash. Later Android-only source changes were not relabelled
as this Mac executable.

## Reproduce

Build and launch the isolated signed Inbox case as described in the
[installed acceptance guide](../integrated/README.md#reproduce-the-isolated-run).
Inspect the normal agent disclosure and activate Allow using the owned Makepad
instrument. From App Design Flow, run:

```sh
python3 examples/connected-apps/inbox/soak.py --profile-root "$RUN_ROOT" --octosense "$OCTOSENSE_CHECKOUT" --kernel "$PINNED_OCTOS_BINARY" --port 8395 --cycles 33 --duration-seconds 610
```

A new run creates its own evidence directory under the private profile and
refuses to overwrite it. The first phase waits for incoming-mail decisions,
creates a draft through the UI, asks the actual peer to change 9:00 AM to
10:30 AM and retain the medication-list sentence, then verifies its tool trace
and saved body. Each cycle uses native input to edit alternating short/long
Unicode text, scroll, change Email/Reply/Chat tabs, exercise the composer, open
immutable review, reject automated approval, cancel and collapse/reopen. Every
fifth cycle also collapses a pending review to revoke its ticket. Host draft
revision/body read-back is read-only and must match exactly. Cold restart
checks the same saved body and review. No send is approved.

To reuse the completed model case after a runtime repair, cold-launch the same
private profile with `launch_integrated.py --restart`, then add
`--reuse-model-case --run-name soak-repaired`. This reads the actual previous
model tool result; it does not rewrite model history or app storage. Keep all
model configuration and raw logs outside Git.

Reported input latency is the native HTTP command's `wait=1` round trip,
including its frame acknowledgement. It is **not FPS or display latency**.
Other native soaks and Android compilation were running concurrently, so these
are loaded-host observations, not an idle benchmark. Process RSS includes the
whole Shell and rendering/capture caches; a ten-minute trend is not a proof of
absence or presence of memory leaks.

## 中文说明

完整 Shell 持续测试完成 33／33 轮、610.002 秒，并通过冷启动恢复。每轮均由
Makepad 原生输入完成编辑、滚动、Email／Reply／Chat 切换、审核取消、收起再展开，
并只读核对主机保存的内容和版本。最终草稿为第 43 版，发送尝试为零。所有本轮
Shell 和代理内核进程已退出。

发现并修复了审核层与编辑器文字重叠，以及收件箱基线状态不自动刷新。修复后的
首张、长文本、最终及冷启动截图均逐张检查；首张还通过其他代理独立审视。
真实 DeepSeek 完成预约卡片发布、促销静默，以及同一草稿的时间修改和读回确认。
Gmail 仍为隔离模拟依赖，真实 Google 登录、送达、物理批准和 Android 不在本次
验证范围。

1,204 次原生输入的帧确认往返中位数为 8.168 毫秒，p95 为 18.548 毫秒，最大
60.990 毫秒；这不是帧率。最终运行保留了两次帧提交确认错误（不是五秒超时），
没有重放输入，只读恢复截图与后续保存状态检查通过。因此功能流程通过，但不能
称为无渲染／仪器错误的 UX 验收。RSS 从 510.02 增至 570.70 MiB；有限时长、
存在并行编译负载的测试不能证明存在或不存在内存泄漏。先前失败回执完整保留，
所有私人配置和原始日志留在本机隔离目录。
