# 把 OctoSense 应用发布到 App Hub

[English](PUBLISHING.md) | 简体中文

未注明中文版的链接指向英文文档。

让能运行的脚本应用通过本地检查，进入 GitHub 证明和 App Hub 审核流程。先完成清单、商店信息、真实截图和审核答案；tag 工作流再生成并验证封存的发布包，无需开发者签名密钥。当前实现限制见 §3.6。

**开 App Hub 提交 issue，才是请求发布。** 填写仓库、版本/commit、截图和请求的权限；可以在 release 准备好之前开 issue，之后补充 tag、工作流结果和 release pack。审核人员对确切的 release 运行准入检查，并在 issue 中反馈缺项或拒绝原因；App Hub 管理员批准确切的候选版本后，Hub 才发布签名目录条目。创建 GitHub release 本身不会提交或批准应用。

其余内容由 App Hub 的两份文档负责：

| 需要了解 | 阅读 |
| --- | --- |
| 准入检查的规则、能力名称、保留 id、清单和商店信息的字段、签名 | App Hub 的 [PUBLISHING.zh-CN.md](https://github.com/OctoSense-org/OctoSense-App-Hub/blob/main/docs/PUBLISHING.zh-CN.md) |
| 签名、打 tag、提交 issue、审核人员检查什么、常见拒绝原因 | App Hub 的 [SUBMITTING.zh-CN.md](https://github.com/OctoSense-org/OctoSense-App-Hub/blob/main/docs/SUBMITTING.zh-CN.md) |

- 在 [QUICKSTART](QUICKSTART.zh-CN.md) 的 §1–6 都走通之后，从这里开始：应用已能在 `card-host` 中运行，你也测试过它的交互。
- **HUMAN** 标出需要用户授权的把关节点：发布者身份与隐私文本、声明的平台、发布 tag 和提交。到了这些节点，Agent 停下、汇报，然后等待。

## 1. 发布的是什么

只有 `bundle/`。应用仓库中的其他内容（`AGENTS.md`、笔记、开发工具、密钥、日志、`.local-state/`、`build/review.json`）都留在它之外。

```text
my-app/
  AGENTS.md  README.md  .gitignore        不提交
  .github/workflows/publish-app.yml       发布工作流；不放进应用包
  .gitattributes                         由 tools/octo new 复制：bundle/** -text，让 Git 永不改写应用包
  build/review.json                      不提交（hub scan 的输出）
  .local-state/                          不提交（card-host 的 jail）
  bundle/                                提交的内容
    manifest.json      id、版本、名称、完整性、能力、主机
    listing.json       商店展示的内容
    main.splash        程序（卡片应用则是 page.card + kit/）
    assets/icon.svg    商店信息引用的图标（PNG 或 SVG，正方形）
    screenshots/01-main.png   真实截图，PNG 格式，1 到 8 张，由商店信息引用
```

`bundle/` 中只能有准入检查认识的文件类型。macOS 的 Finder 会在你打开过的文件夹中生成 `.DS_Store` 文件，准入检查会拒绝这些文件；请在写入摘要之前删除它们。已发布的参考应用在 `bundle/` 旁边还放了 `PRIVACY.md`、`publisher.json` 和 `review/` 文件夹，这种结构见 [SUBMITTING §1](https://github.com/OctoSense-org/OctoSense-App-Hub/blob/main/docs/SUBMITTING.zh-CN.md#1-安排仓库结构)。

## 2. 准入检查的规则

`hub check` 就是准入检查：App Hub 检查你的提交时，运行的也是这份代码。它先输出 `<id> <version> — PASSED` 或 `<id> <version> — REFUSED`，再为每个检查结果输出一行。`[refused]` 行会阻止准入；`[warning]` 行不会，但审核人员能看到。逐条规则见 App Hub 的 [准入检查的规则](https://github.com/OctoSense-org/OctoSense-App-Hub/blob/main/docs/PUBLISHING.zh-CN.md#准入检查的规则) 一节。最常遇到的拒绝该如何修复，见[常见拒绝原因及修复](https://github.com/OctoSense-org/OctoSense-App-Hub/blob/main/docs/SUBMITTING.zh-CN.md#常见拒绝原因及修复)。

截图是否真的截自这个应用、商店信息的文字是否属实、图标缩小后是否看得清、隐私政策所写是否真实，准入检查都不判断。这些由审核人员把关。

## 3. 分步操作

每个 shell 中先设置一次这些变量：

```sh
export HUB=/path/to/hub                # tools/octo doctor 会输出这个路径
export APP=~/apps/my-app               # 应用仓库
export B="$APP/bundle"
```

### 3.1 把清单定稿

编辑 `$B/manifest.json`：

- `id`：确定最终值，最后一段不能是保留名（[QUICKSTART §3](QUICKSTART.zh-CN.md#3-创建应用)）。
- `version`：每次提交都用新值（`0.1.0`，然后是 `0.1.1`……）。签名目录中已有的版本，准入检查会拒绝；发布 tag 也使用同一个版本号。
- `capabilities`：只列出应用已实现的功能用到的能力（[CAPABILITIES](CAPABILITIES.zh-CN.md)）。
- `network.hosts`：程序用到的每个主机，写纯主机名（`api.example.com`）。
- `integrity` 留给 `hub stamp` 填写。

全部字段见 App Hub 的 [清单](https://github.com/OctoSense-org/OctoSense-App-Hub/blob/main/docs/PUBLISHING.zh-CN.md#清单) 一节。

### 3.2 把商店信息定稿

修改 `$B/listing.json` 中的**每一个**值。模板中的发布者名称、`example.com` URL 和描述都是占位内容。准入检查接受它们，审核人员不接受；只要它们还在，`tools/octo check` 就会输出提示。

- `platforms`：只写你实际运行过应用的平台（**HUMAN**：由人确认）。在 Mac 上用 `card-host` 运行，对应的是 `macos`。`tools/octo new` 写入的是你用 `--platform` 传入的平台；删掉没有测试过的平台。
- `category`、`age_rating` 等字段的取值见 App Hub 的 [商店信息](https://github.com/OctoSense-org/OctoSense-App-Hub/blob/main/docs/PUBLISHING.zh-CN.md#商店信息) 一节。
- `publisher.privacy_policy_url`：一个确实存在的 HTTPS URL（**HUMAN**：隐私政策的文字由发布者负责）。如果应用包附带 `tools.json`，应用就有 Agent，请在商店信息和隐私文本中写明。
- 图标：遵循 App Hub 的 [`docs/ICONS.zh-CN.md`](https://github.com/OctoSense-org/OctoSense-App-Hub/blob/main/docs/ICONS.zh-CN.md)。

商店信息是已签名版本的一部分：以后要修改其中的文字，就得发布新版本。

### 3.3 截取真实截图

运行未签名的应用，用真实输入把它操作到你想展示的状态，截图，查看 PNG，然后退出：

```sh
tools/octo run "$B" --port 8141 --hidden --detach
curl -s "127.0.0.1:8141/click?x=150&y=140&wait=1"      # 让输入框获得焦点
curl -s "127.0.0.1:8141/t?t=Call%20the%20dentist&wait=1"
curl -s "127.0.0.1:8141/click?x=366&y=140&wait=1"      # 按下 Add
tools/octo shot 8141 "$B/screenshots/01-main.png"
curl -s 127.0.0.1:8141/quit
```

`shot` 会输出 `wrote …/01-main.png (824x1784, … bytes). Look at it before you ship it.` 这一行。它会等应用的控件出现、画面稳定下来，再保存 `GET /g?raw=1` 的结果。直接用 `curl -s "127.0.0.1:8141/g?raw=1" -o out.png` 保存的是当时的帧，可能只画了一半。截图的尺寸就是窗口的像素尺寸：在 Retina Mac 上是 412x892 点的 2 倍。

- 签名之前截图：`card-host` 会拒绝已签名的应用包。
- 在 `listing.json` 中最多列出 8 张截图。
- 绝不要发布错误画面、空白的首帧、效果图，或根据 `/snap` 重新绘制的图片。

### 3.4 写入摘要并检查

```sh
tools/octo check "$B"
# 手动执行同样的步骤：
"$HUB" stamp "$B"
"$HUB" check "$B" --allow-unsigned
```

在用模板创建、已截好图的应用上运行，输出如下：

```text
my-notes 0.1.0 — PASSED
  [warning] publisher-signature: unsigned: accountability rests on the hub alone
  grants: capabilities {"storage"}, hosts {}, storage 16777216 bytes, agent none
```

同一个应用在 `screenshots/01-main.png` 还不存在时的输出（退出码 1）：

```text
my-notes 0.1.0 — REFUSED
  [warning] publisher-signature: unsigned: accountability rests on the hub alone
  [refused] listing: screenshots/01-main.png is named by the listing but is not in the bundle
  grants: capabilities {"storage"}, hosts {}, storage 16777216 bytes, agent none
hub: the bundle was refused
```

对照应用在界面上实际做的事检查 `grants:` 行；如果授权超出所需，就从清单中删减。`storage 16777216 bytes` 是商店应用的 16 MiB 存储上限。应用声明了 `storage` 但没有设置 `storage.max_bytes` 时，得到的就是这个上限；没有声明 `storage` 的应用得到 `storage none`，什么都存不了。

要对照已发布的签名目录检查版本，给上面任一条检查命令加上 `--catalog <App Hub checkout>/catalog-v2.json`。准入检查会拒绝已经发布过的版本：

```text
  [refused] version: version 0.1.0 of org.octosense.samples.githubnotes is already published; publish a new version
```

`tools/octo check` 会在检查之前为未签名的应用包重新写入摘要，所以即使你 commit 的摘要已经过时，它也会通过。每次 commit 之前，把它作为最后一步运行。tag 工作流另行生成并验证封存的发布 pack（§3.7）；源码检查不能代替发布者证明验证。

### 3.5 回答审核问题

```sh
mkdir -p "$APP/build"
"$HUB" scan "$B" --packet "$APP/build/review.json"
```

```text
wrote the review packet to …/build/review.json
no --reviewer given; the packet holds 7 questions for one
```

审核包中有清单、商店信息、授权、程序、Agent 文件（如有）和问题。审核包不含截图，请自己把截图附到 issue 中。问题共 7 个；应用包附带 `tools.json`、`AGENT.md` 或 skills 时，还有关于 Agent 文件的第 8 个问题。逐题书面作答，例如写在 `$APP/review/ANSWERS.md` 中；审核人员问的也是这些问题（[SUBMITTING §8](https://github.com/OctoSense-org/OctoSense-App-Hub/blob/main/docs/SUBMITTING.zh-CN.md#8-审核检查什么)）。对可编辑源码回答审核问题。仅在可选的旧版 Ed25519 路径中，扫描已签名应用包的 `hub scan` 需要 `--publisher-key <publisher-id>=<hex public key>`。

<a id="36-发布者密钥human"></a>

### 3.6 GitHub 发布者身份（HUMAN）

新应用默认使用自己的公开 GitHub 仓库和 GitHub Actions 证明。开发者无需生成
`publisher.key`，也无需添加仓库签名 secret。用自己的账户发布前，请审阅发布者
信息和工作流。

**可用状态：** 此路径需要应用契约 1.8.0 和 `publisher-github-v1`。
两个真实 GitHub release 已通过证明验证，以及原生 Store 的安装、启动校验、更新、
撤回和篡改拒绝检查（[验收记录](https://github.com/OctoSense-org/OctoSense-App-Hub/blob/main/reviews/github-publisher-v1/acceptance.json)）。
这些 Store 检查使用隔离的测试目录；测试应用没有提交或获准进入 Hub。
[桌面 RC1](../README.zh-CN.md#下载兼容-shell)现已发布。macOS 公开示例安装/更新及隔离手机测试应用的验收另有发行证据；这些不代表你的应用 UX 或提供商效果通过验证。
旧宿主会拒绝这个要求。`publisher-toolchain.json` 必须指定经过评审的不可变
App Hub commit；安装命令会拒绝缺失或浮动的版本。

对已有的可编辑应用目录，在 App Flow 仓库中运行以下命令安装工作流：

```sh
tools/octo publish-github "$APP"
```

`tools/octo new` 也会安装 `.github/workflows/publish-app.yml`。命令只写入这个文件，
不会推送、发布、提交或批准应用。除非显式加上 `--replace`，否则不会覆盖不同的
已有工作流。无需开发者签名 secret；工作流使用 GitHub 的短期任务令牌和 OIDC
权限生成证明并创建 release。

仓库保留已测试、未签名的 `bundle/` 源码。审阅并 commit 工作流、源码、真实截图
和 `.gitattributes`，存放在公开应用仓库。为该 commit 创建并推送一个**新**的
`v<manifest.version>` tag，例如清单版本为 `0.1.0` 时使用 `v0.1.0`。
绝不要移动或重建已发布的 tag。

<a id="37-为最终字节签名human"></a>

### 3.7 在 GitHub Actions 中证明最终字节

推送 tag 后，工作流用固定版本的 App Hub 工具依次执行：

1. `hub publisher-prepare` 检查应用包，绑定仓库名称、不可变的仓库/所有者 ID、
   工作流路径、tag 和 commit，并在 `bundle/` 之外写入规范化清单。
2. GitHub 的 `actions/attest` 为该清单生成证明。原生验证器检查 GitHub 托管的
   tag-push 工作流身份及源码 commit。
3. `hub publisher-attach` 把证明嵌入 `integrity.github.attestation`，随后
   `hub publisher-verify` 验证它。
4. `hub publisher-pack` 再次验证，不重新写入摘要，产出 `app.bundle.pack.json`。
   release 还包含 `octosense-app-manifest.json` 和 `release-receipt.json`。

这些是工作流阶段，不是本地生成密钥的步骤。附有证明的应用包已经封存，不能再
修改、重新写入摘要或删除证明。`card-host` 没有发布者证明验证器，不能运行它。
发布前测试可编辑源码，准入后在兼容的 Store 宿主中测试发布包。tag 的源码归档
和附有证明的 release pack 是不同产物；仅检查源码不能验证已发布的证明。

日常更新时，修改并测试源码、递增 `manifest.version`，再从同一个仓库、所有者和
工作流身份推送匹配的新 tag。准入检查会验证身份连续性。release receipt 记录
发布输入和 pack 摘要，不代表 App Hub 已批准应用。

### 3.8 提交（HUMAN）

向 OctoSense-App-Hub 开 `Submit <app id> <version>` issue，表达发布意图。
提供仓库、版本/commit、截图、请求的权限和审核答案。可以先开 issue，再准备 release。
工作流成功后，在同一 issue 补充 release URL、tag、工作流运行和确切的 pack/摘要；
Hub 准入之前需要这些经过验证的字节。当前 issue 字段见 App Hub 的
[SUBMITTING.zh-CN.md](https://github.com/OctoSense-org/OctoSense-App-Hub/blob/main/docs/SUBMITTING.zh-CN.md)。

- 创建 GitHub release 不会自动获得 App Hub 准入。
- 不要在 pull request 中手改 Hub 的签名目录、索引或已准入产物。受保护的审核和发布工作流会准入确切的应用包。
- Agent 可以准备工作流，并在 `build/SUBMISSION.md` 起草 issue；不能声称尚未
  观察到的发布、审核或批准已经发生。对外部操作遵循用户的授权。

### 3.9 App Hub 接下来做什么

审核人员验证发布者证明和应用包，运行准入检查，并在 issue 中反馈拒绝原因。随后由 App Hub 管理员批准确切的版本，再由 Hub 把它发布到签名目录。目前还没有任何 OctoSense 发布版提供它；见 §3.6。需要修改时发布新版本和新 tag，不要替换旧字节。

手动 Ed25519 签名仍是旧工作流的**可选兼容路径**，不是新 GitHub 发布流程的一步。下节保留旧本地演练的命令和记录；已有参考版本及其签名保持原样。

## 4. 在本地演练商店流程

**可选的旧格式兼容演练。** 本节命令和历史结果使用 Ed25519 发布者/目录密钥，
不是 GitHub 发布的必需步骤，也不能验证 `publisher-github-v1`。请使用专门准备的
旧格式测试包，绝不要为附有 GitHub 证明的发布包重新写入摘要。
此旧格式镜像需显式设置 `OCTOSENSE_HUB_CATALOG=legacy`，并使用新的应用数据目录。
已经缓存 v2 的应用库拒绝降级到旧格式；不会离线转换。

在自己的机器上走一遍完整的发布和安装流程，用你自己的信任锚签名（以一把一次性根密钥代替 App Hub 的根密钥），看看设备上会发生什么。演练还会运行应用的宿主服务，这是 `card-host` 做不到的。镜像及其密钥放在 `build/` 下，绝不要放进 `bundle/`。

### 4.1 发布到本地镜像

用一次性 Hub 密钥把已签名的应用包发布到镜像，然后验证镜像。发布者公钥就是 `hub pubkey` 输出的十六进制字符串；这一步不需要私钥。`keygen` 会拒绝已经存在的文件，所以再次运行这段命令之前，先删除 `$APP/build/keys`（里面只有一次性密钥）：

```sh
M="$APP/build/mirror"; mkdir -p "$M" "$APP/build/keys"
ANCHOR=$("$HUB" keygen "$APP/build/keys/anchor.key")        # 一次性密钥，绝不用 App Hub 的
"$HUB" keygen "$APP/build/keys/working.key" >/dev/null
CERT=$("$HUB" certify --anchor "$APP/build/keys/anchor.key" --working "$APP/build/keys/working.key")
"$HUB" publish "$B" --catalog "$M/catalog.json" --key "$APP/build/keys/working.key" \
  --anchor-cert "$CERT" --publisher <publisher-id> \
  --publisher-key "<publisher-id>=<hex public key>" \
  --repo https://github.com/you/my-app --commit "$(git -C "$APP" rev-parse HEAD)" --out "$M"
"$HUB" verify "$M/catalog.json" --anchor "$ANCHOR"
```

`publish` 应输出 `published my-test-notes 0.1.0 (catalog sequence 1)`，`verify` 应输出 `catalog sequence 1 verified, 1 entries`。以上输出是在 macOS 上用较早版本的 App Hub 和测试应用 Test Notes（`my-test-notes`）记录的。

### 4.2 在桌面端 Shell 中安装并打开应用

让 OctoSense 桌面端 Shell 指向这个镜像。把 [OctoSense](https://github.com/OctoSense-org/OctoSense) 克隆到你的工作区，并按它的 [README](https://github.com/OctoSense-org/OctoSense/blob/main/README.zh-CN.md#环境准备) 完成环境准备。`tools/setup.py` 会把锁定版本的 Makepad、OctoScript 和 OctoScript-Makepad 放进 `OctoSense/.sources/`，并给 Makepad 打上 OctoSense 评审过的补丁，所以 Shell 不会复用工作区中的检出目录；`--cache ..` 会复用这些检出目录中的 Git 对象。环境准备不到 1 分钟；冷构建 `cargo build --release -p octosense` 需要 5 到 9 分钟：

```sh
cd <workspace> && git clone https://github.com/OctoSense-org/OctoSense.git
cd OctoSense && python3 tools/setup.py --cache ..
```

```sh
cd <workspace>/OctoSense
OCTOSENSE_HUB_CATALOG=legacy OCTOSENSE_HUB="$M" OCTOSENSE_HUB_ANCHOR="$ANCHOR" \
  OCTOSENSE_HOME="$APP/build/desktop-home" OCTOSENSE_APP_DATA="$APP/build/desktop-apps" \
  MAKEPAD_REMOTE=8399 cargo run --release -p octosense
```

`OCTOSENSE_HOME` 和 `OCTOSENSE_APP_DATA` 让这次测试不影响你自己的 `~/.octosense`。通过远程控制桥操作窗口时，加上 `MAKEPAD_HIDE_WINDOWS=1` 可以让窗口不出现在屏幕上。然后：

1. 在 dock 中打开 **App Hub**，你的应用会出现在列表中。
2. 点击 **Get**，再点击 **Install**。
3. 点击 **Open**。应用在自己的窗口中运行，日志中出现 `card: <app id> running under …`。
4. 操作应用，最后用 `curl -s 127.0.0.1:8399/gq` 结束。

已在 macOS 上验证：应用的交互、存储以及向已声明主机发出的请求，表现都与在 `card-host` 中一致。

- 用 `<text>` 绘制的 `icon.svg` 在商店中显示为空白图块。请像模板那样，用形状和路径绘制图标。
- 声明了 `auth` 的应用需要从 OctoSense `main` 构建的 Shell或 [RC1 发行版](../README.zh-CN.md#下载兼容-shell)；当前带 GitHub 证明的应用使用 RC1。beta.1 的商店会拒绝这个能力。你在这里构建的 Shell 没有提供商注册信息，要由你自己提供，而且注册信息绝不放进应用。提供方式有两种：在 `cargo` 编译 Shell 时设置构建变量，例如 `OCTOSENSE_GITHUB_CLIENT_ID`（[配置发行版本](https://github.com/OctoSense-org/OctoSense/blob/main/crates/oauth-service/README.zh-CN.md#配置发行版本维护者)）；或者写入 `$OCTOSENSE_APP_DATA/.host/oauth/clients.json`（这里是 `$APP/build/desktop-apps/.host/oauth/clients.json`），它会取代编译进去的那组注册信息（[高级运维覆盖配置](https://github.com/OctoSense-org/OctoSense/blob/main/crates/oauth-service/README.zh-CN.md#高级运维覆盖配置)）。接入真实提供商后的实际使用大多未验证（[CAPABILITIES § 限制](CAPABILITIES.zh-CN.md#限制)）。
- 这只是用你自己的信任锚做的演练。标准构建只信任 App Hub 的信任锚。

### 4.3 可选：用独立商店安装

App Hub 的独立商店 `appstore` 不需要 Shell 也能从同一个镜像安装应用，但它打不开应用：只有 Shell 的 Card runner 能运行已安装的应用。

`octosense-appstore-app` 始终开启 App Hub 的 `text-input-state-query` 特性，所以只能基于 OctoSense 打过补丁的 Makepad 构建。在未打补丁的 Makepad 上，构建会失败并报 `no variant … TextInputStateQuery`。你日常使用的工作区要保持未打补丁，因为 `tools/setup-native.py --check` 会拒绝打过补丁的 Makepad 源码树；请在第二个工作区中构建商店：

1. 按 [QUICKSTART §1](QUICKSTART.zh-CN.md#1-前置条件) 搭建第二个工作区。
2. 按 `runtime-patches.lock.json` 列出的顺序，把 OctoSense 的 Makepad 补丁打到这个工作区的 `makepad/` 上：先打其中的 `patch`，再依次打每个 `stacked` 条目。使用 §4.2 中检出的 OctoSense：

   ```sh
   cd <second-workspace>
   python3 - <workspace>/OctoSense <<'EOF'
   import json, subprocess, sys
   octosense = sys.argv[1]
   lock = json.load(open(f"{octosense}/runtime-patches.lock.json"))["makepad"]
   for patch in [lock["patch"]] + [s["patch"] for s in lock["stacked"]]:
       subprocess.run(["git", "-C", "makepad", "apply", f"{octosense}/{patch}"], check=True)
   EOF
   ```

3. 在这个工作区的 App Hub 检出目录中构建商店。`appstore` 可执行文件会生成在它的 `target/release/` 中：

   ```sh
   cd <second-workspace>/OctoSense-App-Hub
   cargo build --release -p octosense-appstore-app
   ```

4. 在商店中打开镜像：

   ```sh
   OCTOSENSE_HUB_CATALOG=legacy OCTOSENSE_HUB="$M" OCTOSENSE_HUB_ANCHOR="$ANCHOR" OCTOSENSE_APP_DATA="$APP/build/store-data" \
     MAKEPAD_REMOTE=8143 <second-workspace>/OctoSense-App-Hub/target/release/appstore
   ```

预期结果（在 macOS 上用较早版本的 App Hub 记录）：商店列出“1 app(s) from …/mirror”，并显示商店信息。它的按钮标签都是大写字母。**GET** 会安装应用（`Installed Test Notes 0.1.0 — 1 capability(ies)`），并把应用包解压到 `store-data/my-test-notes/bundle` 下；**OPEN** 不会显示应用。

## 5. 人工把关节点

| 把关节点 | Agent 为什么停下 |
| --- | --- |
| GitHub 发布者身份与发布工作流（3.6、3.7） | 发布绑定公开仓库、所有者、工作流、tag 和 commit；由人授权以这个身份发布。 |
| 发布者名称、支持联系方式、隐私政策文本（3.2） | 这些法律声明和个人声明只有发布者本人才能作出。 |
| 声明的平台（3.2） | 每个平台声明都要对应一次由人执行或记录的实际运行；Agent 无法为此担保。 |
| 为发布打 tag（3.8） | tag 标识审核人员检查的确切字节，永不移动。 |
| 开提交 issue（3.8） | 这是以发布者的名义行事。 |
| 在 OctoSense-App-Hub 中批准提交或合并 | 只有 App Hub 管理员能批准提交，也只有 App Hub 维护者能合并。 |

## 6. 检查表（复制后从上到下执行）

`tools/octo package-help` 会输出一个简短版本；这里的版本多了 `--hidden`、`.DS_Store` 和发布证明检查。

```text
[ ] tools/octo doctor                                   -> hub 和 card-host 均为 [ok]
[ ] manifest.json：id 已定稿（最后一段不是保留名），version 是新值，capabilities 最小化，每个主机都已声明
[ ] listing.json：没有占位内容；category/platforms/age_rating 取值合法；隐私政策 URL 是 HTTPS 且真实存在（HUMAN）
[ ] 图标位于商店信息指定的路径；小尺寸下清晰可辨（App Hub docs/ICONS.md）
[ ] tools/octo run "$B" --port 8141 --hidden --detach   -> 输出含 "admitted" 的一行
[ ] 每个交互都以原生方式操作过（点击、输入、轻触），并观察到效果（截图、/snap 或 jail 中的文件）
[ ] 用 tools/octo shot 从未签名的应用包截图，每张都打开看过；都已列入 listing.json
[ ] curl -s 127.0.0.1:8141/quit                         -> {"ok":1}
[ ] find "$B" -name .DS_Store -delete                    -> bundle/ 中只剩准入检查认识的文件类型
[ ] tools/octo check "$B"                               -> "— PASSED"（只有未签名警告）
[ ] tools/octo check "$B" --catalog <App Hub catalog-v2.json>   -> 没有 version 或 continuity 拒绝
[ ] mkdir -p "$APP/build"; hub scan "$B" --packet "$APP/build/review.json"   -> 7 个问题都已书面作答（附带 tools.json、AGENT.md 或 skills 时为 8 个）
[ ] git -C "$APP" check-attr text -- "$B/manifest.json"   -> "text: unset"（QUICKSTART §3）
[ ] git status 中只有应用源码和已评审的工作流，没有 secret、.local-state 或 build/
[ ] tools/octo publish-github "$APP" -> 已审阅 .github/workflows/publish-app.yml；无需开发者密钥
[ ] HUMAN：commit 已测试源码和工作流，再推送新的 v<manifest.version> tag
[ ] GitHub 工作流成功；publisher-verify 和 publisher-pack 验证带证明的发布包通过
[ ] release pack、规范化清单和 receipt 齐全；兼容宿主安装单独验证，或明确标记待验证
[ ] HUMAN：提交 issue 表达发布意图，附仓库/版本/commit、截图和权限（可提前开）
[ ] 在同一 issue 补充成功工作流和确切 release pack；Hub 检查、管理员批准、目录发布另行执行
[ ] 汇报：验证了什么、在哪个平台上验证、哪些没有验证
```
