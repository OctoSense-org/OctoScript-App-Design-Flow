# DeepSeek 通过 App Studio 生成的卡片

[English](README.md) | 简体中文

**Email Action DS** 和 **Meeting Planner DS** 的卡片、交互代码及图标由
DeepSeek V4 Flash 在 OnePlus 6 的系统 Agent 中生成。它读取 Card Studio skill
和 App Design Flow 文档，自行调用 Studio 渲染、检查控件、注入输入、查看截图并修复。
Codex 提供需求和缺陷反馈，负责打包与独立验证，没有修改生成的卡片、Splash 或图标源码。
上一级原有示例保留原来的作者归属，不算 DeepSeek 生成。

在手机打开 **Hackathon Demos → App Hub**，选择名称以 **DS** 结尾的应用。
邮件点击 **Ask app agent for a reply**，首次允许 Agent 后重试；检查 AI 草稿，
点击 **Review reply** 审核完整正文和收件人，再确认本地模拟投递。撤销只删除该邮件的回执。
会议点击 **Open full view**，询问共同空闲时段；返回卡片选择时段、审核并确认本地预约。
新增 14:00 冲突后须重新审核，可改选 15:30；**All busy / Reset demo** 演示失败与恢复。
离线回复和首个空闲时段按钮明确标注为离线逻辑，不冒充模型回答。

手机上用右侧滚动条访问下方控件。草稿编辑框的长行需要横向滚动，审核页面会完整换行。
这里 L0/L1/L2 指速览、展开卡片、完整应用三种展示深度；只有 `.card` 使用
Octoscript L0，交互视图使用 Splash。速览文件已渲染，不代表已接入真实通知或速览屏。

本次 Studio 只允许 storage 预览。每个目录保留模型生成的 `preview-manifest.json`；
正式宿主使用 `bundle/manifest.json` 声明 Agent 和 turn 能力，两者运行相同的源码。
真实模型调用需要正常安装和独立授权，预览成功不能代替这项验证。

[英文说明](README.md) 给出完整运行命令、代码阅读顺序和技能入口。
[验证记录](validation/README.md) 区分模型自己执行的 Studio 检查、33 项独立桌面检查
及手机集成验证，并保留源码哈希、工具调用和需求反馈。模型的 `DESIGN.md / REVIEW.md`
是中间轮次记录，不是最终验收结论。遇到错误应将具体输入、真实结果和预期约束交回模型修复，
再做原生验证，不能只凭模型自评或渲染成功认定功能完成。

示例只使用虚构账号数据；不连接真实邮箱或日历，也不验证跨应用委派、后台通知或公开发布。
公开提交前，发布者须替换 listing 中的身份和隐私政策占位信息。
