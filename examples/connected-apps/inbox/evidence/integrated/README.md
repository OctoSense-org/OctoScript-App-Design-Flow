# Installed Inbox acceptance — 2026-10-06

This is a macOS hidden native **full OctoSense Shell** test. It uses a normally
signed local catalog/install, the installed app’s actual consent and peer broker,
real **DeepSeek `deepseek-v4-flash`** inference, admitted Inbox guidance and host
tools. Only Gmail and its credential vault are synthetic, selected by a
non-default `acceptance-fixtures` build feature in an exact, marked private
profile. A normal build cannot enable that dependency through an environment
variable. This is not a live Google account test.

Codex drives native pointer/text input and reviews original PNGs. DeepSeek
performs the incoming-mail decisions and draft tools; Codex does not write the
model’s draft or publication into host storage. The two synthetic messages are
a clinic appointment asking for confirmation and a promotional newsletter.

## Observed journey

The production forward-baseline collector routes both new message IDs to the
account’s app peer. The clinic gets one durable card and notification; the
newsletter gets a durable quiet decision. Both pending events drain to zero.
A successful final answer alone cannot acknowledge an event: the host requires
a recorded quiet decision or an app/account-bound published card.

From the clinic card, Email → Reply → Chat → Reply uses one host draft. Native
input creates a reply for 9:00 AM, then the person’s chat request asks for
10:30 AM Pacific and retains the medication-list sentence. DeepSeek calls the
message/read/edit/read-back tools. The saved revision and editable Reply contain
the requested time and retained sentence. Native review renders that same
immutable recipient, subject and body. An instrument click cannot supply the
required physical approval; no provider send attempt occurs. Cancel preserves
the unsent draft.

These are two bounded relevance examples, not a statistical classifier-quality
claim. Built-in News requests during Shell startup are unrelated and excluded.
No live OAuth, actual Gmail read/send, delivery, physical approval, MiniMax,
Android keyboard/lifecycle or OnePlus 6 success is claimed.

## Receipts and original pixels

The [integrated receipt](integrated-receipt.json) records the signed bundle
digest, app/guidance/driver hashes, actual tool sequences, saved reply and
per-capture binary hashes. The [cold receipt](cold-receipt.json) records the
separate final-binary lifecycle check. Model inference was completed before the
last modal-input/close-routing fix; the final binary reran restoration and
review checks against the same durable account and draft, without another
model turn. These are distinct build receipts, not a claim that both runs used
the same binary.

| Actual peer turn | Elapsed time | Result |
| --- | --- | --- |
| Clinic event | 9.006 s | Published one bound card; durable decision recorded |
| Newsletter event | 4.628 s | Quiet decision, no card |
| Human draft request | 8.835 s | Message + draft read, draft edit, saved draft read-back |

The clinic's first 231-character summary was rejected by the tool's 200-character
limit. DeepSeek received the error and repaired it to 151 characters. The updated
length guidance was present in its real turn; it did not guarantee first-pass
compliance. The receipt retains this failure rather than hiding the retry.

Original 2800 × 1798 native pixels, individually inspected:

- [Restored clinic-only summary](cold-summary.png).
- [Actual DeepSeek chat and reachable composer](06-chat-result.png).
- [Same edited reply after cold restart](cold-reply.png).
- [Immutable review and refused instrument approval](cold-refused.png).
- [Draft retained after collapsing a pending review](cold-resume.png).

The final modal check first focused the underlying editor, opened native review,
then injected text and a pointer aimed at the hidden Chat control. Neither
reached the app. Cancelling and saving left revision 3 and its exact body
unchanged. Back to editing closed this originating sheet while normal Inbox was
also resident. Collapsing the pending review revoked its ticket; reopening the
workspace retained the unsent reply. No provider submission occurred.

Repairs discovered through these runs: a Fill app root previously collapsed in
Glance's Fit ancestor; generic shell Chat duplicated the template's own tabs;
the native review background was transparent; expanded Glance could not host a
review sheet; modal input and close requests needed to stay with the originating
host sheet. The final captures verify those specific desktop paths. They are
not a numerical UX score or a phone acceptance result.

## Reproduce the isolated run

Build in the matching OctoSense checkout:

```sh
cargo build --locked --release -p octosense-shell --features mobile-apps,acceptance-fixtures --example connected-install --example connected-inbox-e2e --example connected-app-host
```

From App Design Flow, the launcher below uses an explicitly selected model
profile and the matching pinned kernel binary. The paths are inputs, not files
shipped in this repository. Choose a new private `RUN_ROOT`; the launcher refuses
a reused root or occupied instrument port. It copies only model configuration,
not conversations or app data; keep the result private and out of git.

```sh
python3 examples/connected-apps/inbox/launch_integrated.py --octosense "$OCTOSENSE_CHECKOUT" --profile-root "$RUN_ROOT" --model-profile "$MODEL_PROFILE" --kernel "$PINNED_OCTOS_BINARY" --port 8195
```

Use the Makepad instrument on that owned port. Capture `/g`, inspect the normal
agent disclosure, and activate **Allow**. The harness establishes the forward
baseline and then releases the two synthetic emails. Wait for
`apps/.host/inbox-e2e-receipt.json` to report `events_processed` and pending zero;
do not treat process launch as successful inference.

Open the clinic summary and inspect the original email. Compose this reply:

> Thank you. I confirm Tuesday, October 13 at 9:00 AM Pacific.
> I will bring my medication list.

Switch to the app’s Chat and ask:

> Please change my reply to ask for 10:30 AM Pacific instead of 9:00 AM on Tuesday,
> October 13. Keep the sentence about bringing my medication list. Do not send.

Read the actual Reply and native review, then cancel. Do not substitute remote
input for physical send approval. Capture original `/g` PNGs under `RUN_ROOT`.
The read-only collector verifies the signed installation, actual model/tool
traces, durable decisions and saved draft, exporting only selected fields and
explicitly selected PNG basenames:

```sh
python3 examples/connected-apps/inbox/collect_integrated.py --profile-root "$RUN_ROOT" --binary "$OCTOSENSE_CHECKOUT/target/release/examples/connected-inbox-e2e" --output "$RECEIPT_DIR" --capture 02-glance.png --capture 07-reply-edited.png --capture 09-native-review-opaque.png
curl --silent http://127.0.0.1:8195/quit
```

For the cold check, wait until that owned port closes, then use the same marked
profile without reinstalling or copying credentials again:

```sh
python3 examples/connected-apps/inbox/launch_integrated.py --restart --octosense "$OCTOSENSE_CHECKOUT" --profile-root "$RUN_ROOT" --kernel "$PINNED_OCTOS_BINARY" --port 8195
```

Reopen the restored clinic card, inspect Reply, test review cancellation, and
close the owned process with `/quit`. A changed binary is recorded separately
in `active-binary.sha256`; keep per-image build attribution in
`capture-builds.json` when exporting captures from more than one build.

The collector’s success is a state assertion; original-pixel review remains a
separate requirement. It never copies model profiles, tokens, raw peer prompts
or full application logs. The source bundle remains unsigned for publication;
ephemeral fixture signing only proves the ordinary installation boundary.

Additional executed checks in OctoSense: `connected_events::tests` passed 2/2,
including failed peer → durable pending event → 60-second error backoff;
`acceptance_fixtures::tests` passed 1/1 for exact-root activation and refusal to
replace live registrations. The final source bundle's App Hub gate reports
`org.octosense.samples.inbox 0.1.0 — PASSED`, with the expected unsigned warning.

## 中文说明

这是 macOS 隐藏窗口中完整 OctoSense Shell 的集成验证，实际运行已签名安装流程、
应用代理同意、代理调度、DeepSeek v4 Flash 推理和工具路由。Gmail 数据与凭据库
是仅验收构建启用的隔离模拟依赖，不是真实 Google 登录。预约邮件生成一张卡片，
促销邮件静默；聊天修改与 Reply、原生审核使用同一份保存草稿。自动化操作不能
批准发送。真实 Gmail 读取／送达、物理批准、MiniMax 和 OnePlus 6 尚未验证。
模型配置和完整日志只保留在本机私有目录，公开回执只导出允许的字段与虚构截图。
最终冷启动测试还验证了审核弹窗阻止输入穿透、取消只关闭原审核界面、收起审核会
撤销待批准请求，以及再次展开保留同一份草稿。真实模型运行与最终冷启动使用的
二进制摘要分别记录。预约筛选 9.006 秒、促销静默 4.628 秒、聊天修改 8.835 秒；
模型第一次摘要过长，被工具拒绝后自行修正，此失败也保留在回执中。
