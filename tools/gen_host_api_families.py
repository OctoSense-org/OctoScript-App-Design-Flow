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
SINCE = {"main (unreleased)": ("`main`, in no release yet", "`main`，尚未进入任何发行版"), "beta.1; `compose`/`review_send` rc.2": ("beta.1; `compose`/`review_send` rc.2", "beta.1；`compose`/`review_send` rc.2"), "rc.1; `record_*` rc.2": ("rc.1; `record_*` rc.2", "rc.1；`record_*` rc.2"), "rc.1; `sample` rc.2": ("rc.1; `sample` rc.2", "rc.1；`sample` rc.2"), "rc.2 (desktop macOS/Linux)": ("rc.2 (desktop macOS/Linux)", "rc.2（桌面 macOS/Linux）"), "rc.2 (system assistant only)": ("rc.2 (system assistant only)", "rc.2（仅系统助手）")}
PLAT = {"android": "Android", "ios": "iOS", "openharmony": "OpenHarmony", "macos": "macOS", "windows": "Windows", "linux": "Linux", "web": "web"}
ENGINES = {"sheet", "photo", "word", "deck", "cad", "light", "sound", "design", "film", "effect", "vector", "pdf"}
NOTE = {
 "mail": ("Reads and notifications for the accounts the person connected for the app. Since RC2 a store app can also send: `mail.compose` and `mail.compose_status` keep a draft, and `mail.review_send` (or `mail.send`) opens the host's native review, which approves only on macOS and Android; on Windows and Linux it fails with `Physical Mail send approval is unavailable on this platform`. On RC1 a store app had no send path ([OctoSense #409](https://github.com/OctoSense-org/OctoSense/issues/409)).",
          "读取用户为应用连接的账户并发出通知。从 RC2 起，商店应用也能发送：`mail.compose` 和 `mail.compose_status` 保存草稿，`mail.review_send`（或 `mail.send`）打开宿主的原生审阅界面，它只在 macOS 和 Android 上能确认；在 Windows 和 Linux 上以 `Physical Mail send approval is unavailable on this platform` 失败。在 RC1 上，商店应用没有发送路径（[OctoSense #409](https://github.com/OctoSense-org/OctoSense/issues/409)）。"),
 "files": ("RC2: `files.import`, `files.export` and `files.pick_photo` on macOS, Windows and Android, on Linux with zenity, qarma, matedialog or kdialog; `files.share` on Android only; 1 MiB per file, foreground only; chooser acceptance pending.", "RC2：`files.import`、`files.export` 和 `files.pick_photo` 在 macOS、Windows 和 Android 上提供，Linux 需要 zenity、qarma、matedialog 或 kdialog；`files.share` 仅限 Android；单个文件最大 1 MiB，仅限前台；选择器的验收待完成。"),
 "audio": ("RC2 on macOS and Android: `audio.play/status/stop` over one WAV, MP3, FLAC or Ogg file (at most 1 MiB and 60 s) in the app's storage, foreground only; needs `storage`; hardware acceptance pending.", "RC2 在 macOS 和 Android 上提供：`audio.play/status/stop` 在前台播放应用存储中的一个 WAV、MP3、FLAC 或 Ogg 文件（最大 1 MiB、最长 60 秒）；需要 `storage`；硬件验收待完成。"),
 "device_calendar": ("RC2 on macOS (EventKit) and Android Home: consent, calendar selection, bounded event reads and physically reviewed writes; OS-calendar interaction pending acceptance. Separate from `calendar` and `gcalendar`.", "RC2 在 macOS（EventKit）和 Android Home 上提供：授权、选择日历、有上限的日程读取和亲手点按确认的写入；与系统日历的实际交互待验收。与 `calendar` 和 `gcalendar` 是不同的服务。"),
 "calendar": ("Calendar's own service (`calendar is Calendar's own service`). For the person's Google Calendar, use `gcalendar`.", "Calendar 自己的服务（`calendar is Calendar's own service`）。要访问用户的 Google Calendar，请用 `gcalendar`。"),
 "photos": ("Only the system Photos app's `notify`.", "只响应系统应用 Photos 的 `notify`。"), "youtube": ("Only the system YouTube app's `notify`.", "只响应系统应用 YouTube 的 `notify`。"),
 "maps": ("The system Maps app's own service.", "系统应用 Maps 自己的服务。"), "ai-providers": ("The system AI providers app's own service.", "系统应用 AI providers 自己的服务。"),
 "llm": ("Manages the device's AI providers; `llm is for OctoSense's own apps.` Use `model`.", "管理设备上的 AI 提供商；`llm is for OctoSense's own apps.` 请用 `model`。"),
 "news": ("`The news service serves system apps only.`", "`The news service serves system apps only.`"),
 "clipboard": ("Declarable, and the gate admits it, but no shell answers `host.request(\"clipboard.*\")` on any release; the grant only unlocks a WebCard's write-only clipboard bridge.", "可以申请，准入检查也会通过，但任何发行版都没有 Shell 响应 `host.request(\"clipboard.*\")`；授权只解锁 WebCard 自己的只写剪贴板桥接。"),
 "matrix": ("Not served by the OctoSense shells. Only the Rinx app serves `matrix.*`, through its own host, to its mini-apps.", "OctoSense 的 Shell 不提供。只有 Rinx 应用通过自己的宿主向其迷你应用提供 `matrix.*`。"),
 "octos": ("The app's own agent session, once the person allows it. Not on iOS.", "应用自己的 Agent 会话，用户允许后可用。iOS 上不提供。"),
 "wasm": ("Desktop RC2 on macOS and Linux (not Windows) and standard Home source builds on Android (feature `wasm-functions`); RC1 did not serve it ([Run your own Rust code](RUST.md)).", "桌面 RC2 在 macOS 和 Linux 上提供（Windows 不提供），Android 上的标准 Home 源码构建也提供（特性 `wasm-functions`）；RC1 没有提供（[运行自己的 Rust 代码](RUST.zh-CN.md)）。"),
 "camera": ("Since RC1 on Android and macOS, after the person's per-app consent on a host sheet and the OS camera prompt.", "自 RC1 起在 Android 和 macOS 上提供；需要用户在宿主面板上对本应用的授权，操作系统的相机授权仍然适用。"),
 "location": ("Since RC1 on Android and macOS; `location.get` is Android only, and RC2 adds `location.sample`, a fresh foreground-only fix, on both.", "自 RC1 起在 Android 和 macOS 上提供；`location.get` 仅限 Android，RC2 新增的 `location.sample` 在两者上都能为前台应用获取实时位置。"),
 "microphone": ("Since RC1 on Android and macOS; sound in camera recordings. RC2 adds `microphone.record_*`: a short foreground recording (mono WAV, at most 30 s) into the app's storage; hardware acceptance pending.", "自 RC1 起在 Android 和 macOS 上提供；为相机录像加入声音。RC2 新增 `microphone.record_*`：在前台录一段短音频（单声道 WAV，最长 30 秒）存入应用存储；硬件验收待完成。"),
 "runtime": ("`runtime.list` and `runtime.describe`; also answered by `card-host`.", "`runtime.list` 和 `runtime.describe`；`card-host` 也会响应。"),
 "model": ("One-shot calls within a daily budget; media and embeddings since RC1.", "每日预算内的一次性调用；媒体和嵌入向量从 RC1 起提供。"),
 "auth": ("Connections the person approves on a host sheet; backend sign-in since RC1 (Windows and Linux: browser sign-in, reachable since RC2; writes refused).", "用户在宿主面板上批准的连接；自 RC1 起支持后端登录（Windows 和 Linux 用浏览器登录，RC2 起可用；拒绝写操作）。"),
 "github": ("Through a connection made with `auth`. The shell reviews each save, and no release approves one on Windows or Linux.", "通过 `auth` 建立的连接；保存由 Shell 审阅，任何发行版都无法在 Windows 和 Linux 上批准。"),
 "gcalendar": ("Through a connection made with `auth`. The shell reviews each write, and no release approves one on Windows or Linux.", "通过 `auth` 建立的连接；写入由 Shell 审阅，任何发行版都无法在 Windows 和 Linux 上批准。"),
 "gmail": ("Through a connection made with `auth`. The shell reviews each send, and no release approves one on Windows or Linux.", "通过 `auth` 建立的连接；发送审阅由 Shell 负责，任何发行版都无法在 Windows 和 Linux 上批准。"),
 "glance": ("Cards on the Glance screen that open only this app.", "速览栏上的卡片，只会打开本应用。"),
}
DESKTOP_ENGINES = {"word", "deck", "cad", "light", "sound", "design", "film", "effect", "vector", "pdf"}
DESKTOP_ENGINE_NOTE = ("A craft engine behind a host service for the system assistant ([ADR 0013](https://github.com/OctoSense-org/OctoSense/blob/main/docs/adr/0013-craft-engines-as-pinned-services.md)), shipped in desktop RC2 (feature `craft-engines`); Home builds leave it out. App Hub `main` lists the name as a declarable capability, but RC2's admission does not know it and no store app is served.", "面向系统助手的 craft 引擎宿主服务（[ADR 0013](https://github.com/OctoSense-org/OctoSense/blob/main/docs/adr/0013-craft-engines-as-pinned-services.zh-CN.md)），随桌面 RC2 发行（特性 `craft-engines`）；Home 构建不包含。App Hub `main` 已把该名称列为可申请的能力，但 RC2 的准入检查不认识它，也没有任何商店应用能得到服务。")
ENGINE_NOTE = ("A craft engine behind a host service for system apps ([ADR 0013](https://github.com/OctoSense-org/OctoSense/blob/main/docs/adr/0013-craft-engines-as-pinned-services.md)), shipped in desktop RC2 and kept by Home builds. App Hub `main` lists the name as a declarable capability, but RC2's admission does not know it and no store app is served.", "面向系统应用的 craft 引擎宿主服务（[ADR 0013](https://github.com/OctoSense-org/OctoSense/blob/main/docs/adr/0013-craft-engines-as-pinned-services.zh-CN.md)），随桌面 RC2 发行，Home 构建保留。App Hub `main` 已把该名称列为可申请的能力，但 RC2 的准入检查不认识它，也没有任何商店应用能得到服务。")
def cap(r, lang):
    c = r.get("capability")
    if isinstance(c, list): return ("、" if lang == "zh" else ", ").join(f"`{x}`" for x in c) if c else "—"
    if not c: return "—"
    if " (" in c:
        base, rest = c.split(" (", 1); rest = rest.rstrip(")")
        zh_rest = {'method-level': '方法级', 'App Hub main only': '仅 App Hub main'}.get(rest, rest)
        return f"`{base}`（{zh_rest}）" if lang == "zh" else f"`{base}` ({rest})"
    return f"`{c}`"
def gen(lang):
    snap = json.load(open(SNAP, encoding="utf-8")); i = 0 if lang == "en" else 1
    L = []
    if lang == "en":
        L += ["# Host API families", "", "English | [简体中文](HOST-API-FAMILIES.zh-CN.md)", "",
              "Every `host.request` family, with the capability a manifest declares for it, who the shells actually serve, on which platforms, and since which release. **Declarable does not mean served:** the gate admits a capability from the contract's list, but the service decides whom it answers. This page is generated from [`host-api-families.json`](host-api-families.json), a snapshot of the table kept on [App Hub #172](https://github.com/OctoSense-org/OctoSense-App-Hub/issues/172); regenerate it with `tools/gen_host_api_families.py`, never edit it by hand.", "",
              f"Checked against: {'; '.join(snap['checked_against'])}.", "",
              "**Shipped in [desktop RC2](../README.md#compatible-shell-download)** (source `4ccf8e06`, App Hub `95e4831a`, contract 1.10.0): the `files` family, `storage.binary_write@1` (`fs.write_bytes`), `location.sample`, native external-link openers on Windows and Linux, `audio.play/status/stop` and `microphone.record_*` over app-local files, the `device_calendar` family, app-scoped `mail.compose`, `mail.compose_status` and `mail.review_send`, and Splash controls for the `Video` widget (`video.playback_controls@1`, not a `host.request` method). Each row gives the platform scope; hardware acceptance of audio, the native choosers, calendar writes and SMTP delivery is pending ([host OS API status](https://github.com/OctoSense-org/OctoSense/blob/desktop-v0.1.0-rc.2/docs/host-os-api-status.md)). A method a platform lacks belongs under `host_api.optional`: a `required` entry blocks installing there.", "",
              "| Family | Capability | Serves | Platforms | Since | Note |", "| --- | --- | --- | --- | --- | --- |"]
    else:
        L += ["# 宿主 API 能力族", "", "[English](HOST-API-FAMILIES.md) | 简体中文", "",
              "每个 `host.request` 能力族：申请它所需的能力、Shell 实际响应的对象、支持的平台，以及从哪个版本开始提供。**可以申请不等于会响应**：准入检查只要求能力在契约列表中，响应哪些应用则由服务自己决定。本页由 [`host-api-families.json`](host-api-families.json) 生成，该文件是 [App Hub #172](https://github.com/OctoSense-org/OctoSense-App-Hub/issues/172) 上那张表的快照；请用 `tools/gen_host_api_families.py` 重新生成，不要手工修改。", "",
              f"核对基准：{'；'.join(snap['checked_against'])}。", "",
              "**已随[桌面 RC2](../README.zh-CN.md#下载兼容-shell) 发行**（源码 `4ccf8e06`，App Hub `95e4831a`，契约 1.10.0）：`files` 能力族、`storage.binary_write@1`（`fs.write_bytes`）、`location.sample`、Windows 和 Linux 上原生的外部链接打开方式、面向应用本地文件的 `audio.play/status/stop` 和 `microphone.record_*`、`device_calendar` 能力族、面向应用的 `mail.compose`、`mail.compose_status` 和 `mail.review_send`，以及 `Video` 控件的 Splash 控制接口（`video.playback_controls@1`，不是 `host.request` 方法）。各行给出平台范围；音频、原生选择器、日历写入和 SMTP 投递的硬件验收仍待完成（[宿主 OS API 状态](https://github.com/OctoSense-org/OctoSense/blob/desktop-v0.1.0-rc.2/docs/host-os-api-status.zh-CN.md)）。某个平台上没有的方法要放在 `host_api.optional` 下：写进 `required` 会导致无法在该平台安装。", "",
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
