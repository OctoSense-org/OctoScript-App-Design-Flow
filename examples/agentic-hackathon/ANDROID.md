# OnePlus 6 demo with DeepSeek

Both references run in **Hackathon Demos**, an isolated OctoSense Android
package, with **DeepSeek V4 Flash** answering through each app's own peer.
The tested device is a OnePlus 6 / ONEPLUS_A6003 running Android 15.
The UI, fixtures and local writes run on the phone; model inference uses the
configured remote provider. [Evidence and limitations](validation/LIVE-SHELL.md).

## Open the prepared device

Open **Hackathon Demos → App Hub**, then **Open** beside **Email Action** or
**Meeting Planner**. This is package `dev.makepad.octosense.hackathon`, separate
from the phone's existing OctoSense Home. The two references are contained
apps inside that package, not two standalone APKs.

From a connected development machine, open its private App Hub directly:

```sh
adb -s YOUR_DEVICE_SERIAL shell am start \
  -n dev.makepad.octosense.hackathon/.MakepadApp \
  --es makepad.APP_CONFIG '{"test_actions":["launch-apphub"]}'
```

Wait for the two catalog entries before tapping **Open**. For a fresh test
process, `adb -s YOUR_DEVICE_SERIAL shell am force-stop dev.makepad.octosense.hackathon`
stops only this package and preserves its data. Change the serial for another
authorized device. Android Back can leave the package; reopen **Hackathon
Demos** to continue. Do not confuse the existing Home's catalog with this one.

1. **Email:** open Maya's message → **Ask agent to draft**. On first use, allow
   this app's agent in the host sheet, then retry the drafting action. Review
   the AI-written draft in **Action card → Review reply → Confirm demo
   delivery**. The receipt and **Undo demo delivery** concern a local outbox.
2. **Calendar:** **Agent → Ask app agent**; allow and retry on first use. Read
   the recommendation, select 14:00, and review. **Simulate calendar change**
   followed by confirmation must refuse the stale proposal. Select 15:30,
   review again, and confirm the local invitation. **Activity** shows its receipt.
3. **Offline:** the labeled sample-reply and first-free-time buttons work
   without a provider. They do not call DeepSeek or claim an AI answer.

Swipe over text or use the right scrollbar to reach lower controls. Selecting
a time redraws the plan and returns it to the top; scroll to **Review
invitation** again. The floating system control is outside the sample UI.

## Reproduce the host setup

This rehearsal used OctoSense `ccf8013`, its pinned Makepad `c155f61d`, and
octos kernel `056173e`. Build/install instructions for that source are in the
[phone README](https://github.com/OctoSense-org/OctoSense/blob/ccf8013f2bd7adbb6c20d5f52f47bcfbcbb55313/phone/README.md).
The local build used a separate Cargo target directory, package name and label:

```sh
cargo makepad android --sdk-path="$ANDROID_SDK" --abi=aarch64 \
  --package-name=dev.makepad.octosense.hackathon --app-label='Hackathon Demos' \
  --version-code=1 build -p octosense-home --release --locked --offline --features dev-mode
```

This command assumes the phone README's prepared toolchain, dependencies and
embedded Android octos executable. The validated APK was additionally built
debuggable for app-scoped `run-as` inspection and a private-catalog wrapper;
it is a development artifact, not a production release.

- Make signed **copies** of the bundles using the normal [private catalog
  rehearsal](../../docs/PUBLISHING.md#4-rehearse-the-store-path-locally).
  Keep test keys outside the checkout. On subsequent `hub publish` calls,
  supply the private catalog's public `--anchor` to verify its existing state.
- Point only the test host at that mirror and public anchor. In this build,
  a debug `wrap.sh` sets `OCTOSENSE_HUB`, `OCTOSENSE_HUB_ANCHOR` and
  `OCTOSENSE_LLM_VAULT=file`. Its environment contains no model credential.
  Catalog signature checks and app capability admission remain enabled.
- Configure DeepSeek in the **host**, not either bundle. In this rehearsal,
  an explicitly authorized copy of the existing DeepSeek configuration was
  placed in the test package's private
  `files/octos-home/.octos/profiles/_main.json`. No real mail/calendar accounts
  were copied. Do not print, commit or package that profile with an APK.
- The catalog and signed bundles were first installed through desktop Store
  consent, then those installed artifacts were seeded into the phone's
  isolated app directory. The phone still admitted both bundles and obtained
  separate app-agent consent. A fresh Android Store download/install was not
  part of this run.

## 中文速览

手机上打开 **Hackathon Demos → App Hub**，再打开两个示例。
DeepSeek V4 Flash 通过各自的应用 Agent 读取虚构账号工作区；应用拿不到模型密钥。
首次允许 Agent 后需重试一次。邮件必须审核收件人再确认本地投递；日历在确认时
重新检查冲突，14:00 被新增冲突占用后改选 15:30。操作只写本地虚构数据。

已验证真实手机输入、模型回答、文件读取、确认回执和会议重启持久化。
自动冷启动直接进入 Email Action 曾触发 64 ms 脚本预算并显示空白；本次验证
使用先打开 App Hub、再点 Open 的路径，没有提高预算或绕过权限。
当前为独立开发测试包，不替换原 Home，也不是商店发布。
