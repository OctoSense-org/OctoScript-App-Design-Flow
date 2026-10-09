#!/usr/bin/env python3
"""Generate docs/HOST-API-FAMILIES.md and .zh-CN.md from docs/host-api-families.json.

The JSON is a snapshot of the per-family table kept on App Hub issue #172: for
every `host.request` family, which capability declares it, who the shells
actually serve, on which platforms, and since which release. Re-run after
updating the snapshot; do not edit the generated pages by hand."""
import json, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SNAP = os.path.join(ROOT, "docs", "host-api-families.json")
SERVES = {"store": ("store apps", "商店应用"), "system-only": ("system apps only (`os.*`)", "仅限系统应用（`os.*`）"),
          "per-app": ("one system app's own service", "某个系统应用自己的服务"), "mixed": ("some methods; see the note", "部分方法；见备注"),
          "none": ("no shell serves it", "没有任何 Shell 提供")}
SINCE = {"main (unreleased)": ("`main`, in no release yet", "`main`，尚未进入任何发行版")}
PLAT = {"android": "Android", "ios": "iOS", "openharmony": "OpenHarmony", "macos": "macOS", "windows": "Windows", "linux": "Linux", "web": "web"}
ENGINES = {"sheet", "photo", "word", "deck", "cad", "light", "sound", "design", "film", "effect", "vector", "pdf"}
NOTE = {
 "mail": ("Reads and notifications for the accounts the person connected for the app. A store app has no send path on RC1: `mail.send` answers `approval_required` and the review methods serve only Mail ([OctoSense #409](https://github.com/OctoSense-org/OctoSense/issues/409)).",
          "读取用户为应用连接的账户并发出通知。商店应用在 RC1 上没有发送路径：`mail.send` 返回 `approval_required`，审阅方法只响应 Mail（[OctoSense #409](https://github.com/OctoSense-org/OctoSense/issues/409)）。"),
 "calendar": ("Calendar's own service (`calendar is Calendar's own service`). For the person's Google Calendar, use `gcalendar`.", "Calendar 自己的服务（`calendar is Calendar's own service`）。要访问用户的 Google Calendar，请用 `gcalendar`。"),
 "photos": ("Only the system Photos app's `notify`.", "只响应系统应用 Photos 的 `notify`。"), "youtube": ("Only the system YouTube app's `notify`.", "只响应系统应用 YouTube 的 `notify`。"),
 "maps": ("The system Maps app's own service.", "系统应用 Maps 自己的服务。"), "ai-providers": ("The system AI providers app's own service.", "系统应用 AI providers 自己的服务。"),
 "llm": ("Manages the device's AI providers; `llm is for OctoSense's own apps.` Use `model`.", "管理设备上的 AI 提供商；`llm is for OctoSense's own apps.` 请用 `model`。"),
 "news": ("`The news service serves system apps only.`", "`The news service serves system apps only.`"),
 "clipboard": ("Declarable, and the gate admits it, but no shell serves `clipboard.*` on any release: every call fails.", "可以申请，准入检查也会通过，但任何发行版都没有 Shell 提供 `clipboard.*`：每次调用都会失败。"),
 "matrix": ("Not served by the OctoSense shells. Only the Rinx app serves `matrix.*`, through its own host, to its mini-apps.", "OctoSense 的 Shell 不提供。只有 Rinx 应用通过自己的宿主向其迷你应用提供 `matrix.*`。"),
 "octos": ("The app's own agent session, once the person allows it. Not on iOS.", "应用自己的 Agent 会话，用户允许后可用。iOS 上不提供。"),
 "wasm": ("Standard builds for macOS, Linux and Android on `main` (feature `wasm-functions`); no release yet ([Run your own Rust code](RUST.md)).", "`main` 上 macOS、Linux 和 Android 的标准构建（特性 `wasm-functions`）；尚无发行版（[运行自己的 Rust 代码](RUST.zh-CN.md)）。"),
 "camera": ("RC1 on Android and macOS, after the person's per-app consent on a host sheet and the OS camera prompt.", "RC1 在 Android 和 macOS 上提供；需要用户在宿主面板上对本应用的授权，操作系统的相机授权仍然适用。"),
 "location": ("RC1 on Android and macOS; `location.get` is Android only.", "RC1 在 Android 和 macOS 上提供；`location.get` 仅限 Android。"),
 "microphone": ("RC1 on Android and macOS; sound in camera recordings.", "RC1 在 Android 和 macOS 上提供；为相机录像加入声音。"),
 "runtime": ("`runtime.list` and `runtime.describe`; also answered by `card-host`.", "`runtime.list` 和 `runtime.describe`；`card-host` 也会响应。"),
 "model": ("One-shot calls within a daily budget; media and embeddings since RC1.", "每日预算内的一次性调用；媒体和嵌入向量从 RC1 起提供。"),
 "auth": ("Connections the person approves on a host sheet; backend sign-in on RC1.", "用户在宿主面板上批准的连接；RC1 支持后端登录。"),
 "github": ("Through a connection made with `auth`. The shell reviews each save, and RC1 cannot approve one on Windows or Linux.", "通过 `auth` 建立的连接；保存由 Shell 审阅，RC1 在 Windows 和 Linux 上无法批准。"),
 "gcalendar": ("Through a connection made with `auth`. The shell reviews each write, and RC1 cannot approve one on Windows or Linux.", "通过 `auth` 建立的连接；写入由 Shell 审阅，RC1 在 Windows 和 Linux 上无法批准。"),
 "gmail": ("Through a connection made with `auth`. The shell reviews each send, and RC1 cannot approve one on Windows or Linux.", "通过 `auth` 建立的连接；发送审阅由 Shell 负责，RC1 在 Windows 和 Linux 上无法批准。"),
 "glance": ("Cards on the Glance screen that open only this app.", "速览栏上的卡片，只会打开本应用。"),
}
DESKTOP_ENGINES = {"word", "deck", "cad", "light", "sound", "design", "film", "effect", "vector", "pdf"}
DESKTOP_ENGINE_NOTE = ("A craft engine behind a host service for system apps ([ADR 0013](https://github.com/OctoSense-org/OctoSense/blob/main/docs/adr/0013-craft-engines-as-pinned-services.md)), in desktop builds only on OctoSense `main` (feature `craft-engines`); the Windows build is unverified. Not a capability a store app can declare.", "面向系统应用的 craft 引擎宿主服务（[ADR 0013](https://github.com/OctoSense-org/OctoSense/blob/main/docs/adr/0013-craft-engines-as-pinned-services.zh-CN.md)），在 OctoSense `main` 上仅限桌面构建（特性 `craft-engines`）；Windows 构建尚未验证。商店应用无法申请。")
ENGINE_NOTE = ("A craft engine behind a host service for system apps ([ADR 0013](https://github.com/OctoSense-org/OctoSense/blob/main/docs/adr/0013-craft-engines-as-pinned-services.md)). Not a capability a store app can declare.", "面向系统应用的 craft 引擎宿主服务（[ADR 0013](https://github.com/OctoSense-org/OctoSense/blob/main/docs/adr/0013-craft-engines-as-pinned-services.zh-CN.md)）。商店应用无法申请。")
def cap(r, lang):
    c = r.get("capability")
    if isinstance(c, list): return ("、" if lang == "zh" else ", ").join(f"`{x}`" for x in c) if c else "—"
    if not c: return "—"
    if " (" in c:
        base, rest = c.split(" (", 1); rest = rest.rstrip(")")
        return f"`{base}`（{'方法级' if rest == 'method-level' else rest}）" if lang == "zh" else f"`{base}` ({rest})"
    return f"`{c}`"
def gen(lang):
    snap = json.load(open(SNAP, encoding="utf-8")); i = 0 if lang == "en" else 1
    L = []
    if lang == "en":
        L += ["# Host API families", "", "English | [简体中文](HOST-API-FAMILIES.zh-CN.md)", "",
              "Every `host.request` family, with the capability a manifest declares for it, who the shells actually serve, on which platforms, and since which release. **Declarable does not mean served:** the gate admits a capability from the contract's list, but the service decides whom it answers. This page is generated from [`host-api-families.json`](host-api-families.json), a snapshot of the table kept on [App Hub #172](https://github.com/OctoSense-org/OctoSense-App-Hub/issues/172); regenerate it with `tools/gen_host_api_families.py`, never edit it by hand.", "",
              f"Checked against: {'; '.join(snap['checked_against'])}.", "",
              "**In review, in no build you can download:** OctoSense [#402](https://github.com/OctoSense-org/OctoSense/pull/402) (with App Hub [#175](https://github.com/OctoSense-org/OctoSense-App-Hub/pull/175), contract 1.9) adds a `files` family (`files.status/import/export`), `storage.binary_write@1` (`fs.write_bytes`), `location.sample` and native external-link openers. Do not build on them until they ship.", "",
              "| Family | Capability | Serves | Platforms | Since | Note |", "| --- | --- | --- | --- | --- | --- |"]
    else:
        L += ["# 宿主 API 能力族", "", "[English](HOST-API-FAMILIES.md) | 简体中文", "",
              "每个 `host.request` 能力族：申请它所需的能力、Shell 实际响应的对象、支持的平台，以及从哪个版本开始提供。**可以申请不等于会响应**：准入检查只要求能力在契约列表中，响应哪些应用则由服务自己决定。本页由 [`host-api-families.json`](host-api-families.json) 生成，该文件是 [App Hub #172](https://github.com/OctoSense-org/OctoSense-App-Hub/issues/172) 上那张表的快照；请用 `tools/gen_host_api_families.py` 重新生成，不要手工修改。", "",
              f"核对基准：{'；'.join(snap['checked_against'])}。", "",
              "**评审中，尚未进入任何可下载的构建**：OctoSense [#402](https://github.com/OctoSense-org/OctoSense/pull/402)（配合 App Hub [#175](https://github.com/OctoSense-org/OctoSense-App-Hub/pull/175)，契约 1.9）新增 `files` 能力族（`files.status/import/export`）、`storage.binary_write@1`（`fs.write_bytes`）、`location.sample` 和原生的外部链接打开方式。在它们发行之前，不要依赖这些接口。", "",
              "| 能力族 | 能力 | 响应对象 | 平台 | 起始版本 | 备注 |", "| --- | --- | --- | --- | --- | --- |"]
    for r in snap["families"]:
        f = r["family"]; serves = SERVES.get(str(r.get("served_to")), (str(r.get("served_to")),)*2)[i]
        plats = "、".join(PLAT.get(p, p) for p in (r.get("platforms") or [])) if lang == "zh" else ", ".join(PLAT.get(p, p) for p in (r.get("platforms") or []))
        since = r.get("since"); since = SINCE.get(since, (since, since))[i] if since else "—"
        note = (DESKTOP_ENGINE_NOTE if f in DESKTOP_ENGINES else ENGINE_NOTE if f in ENGINES else NOTE.get(f, ("", "")))[i]
        L.append(f"| `{f}` | {cap(r, lang)} | {serves} | {plats or '—'} | {since} | {note} |")
    out = os.path.join(ROOT, "docs", "HOST-API-FAMILIES.md" if lang == "en" else "HOST-API-FAMILIES.zh-CN.md")
    open(out, "w", encoding="utf-8").write("\n".join(L) + "\n"); print("wrote", out)
gen("en"); gen("zh")
