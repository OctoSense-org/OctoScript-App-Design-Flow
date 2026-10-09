# Script Tool State

[English](README.md) | 简体中文

将旧 `on_agent_tool` 回调迁移到当前 `app_tool(name, call_id)` 的示例。
编辑器与工具共用一份保存的主题偏好和修订号。助手可读取，并在明确要求下修改；
没有邮件、日历、网络或 Glance 权限。参见[迁移指南](../../docs/SUBMISSION-API-MIGRATIONS.zh-CN.md)。

manifest 声明 `script-tools-v1`；`tools.json` 声明有界的
`toolstate.preferences`、`toolstate.set_preferences`，实现方为应用。
处理器从 `request` 读取宿主绑定的参数，先保存再 `complete`，未知名称用 `fail` 拒绝。

## 原生验收

**不要删除 `script-tools-v1` 来让 `card-host` 接受。** 该宿主拒绝所需 ABI。
先构建配套 OctoSense 变更中的 `app-tool-acceptance`，再在 App Flow 运行：

```sh
python3 examples/script-tool-state/verify-native.py \
  --host /path/to/app-tool-acceptance --hub /path/to/hub \
  --output /tmp/script-tool-state-evidence
```

输出目录必须不存在。驱动先捕获真实预览作为临时应用包的商店截图，再重新 stamp。
原生程序验证临时签名准入，绑定实际脚本工具，等待 instrument 看到初始化后的 UI
才调用工具。检查精确返回结果、可见状态，再通过真实输入修改、重启并用工具读取保存值。
还必须通过错误账号、未声明工具、非法参数与工具所有者注销后的拒绝检查。

签名私钥只存在内存，不产生公共发布者身份。所有数据虚构且隔离。原生调用进入点位于
生产 peer/同意检查之后，不证明模型推理、用户允许代理运行、公开商店安装、外部效果或手机执行。
失败保留记录，只清理自己启动的隐藏窗口。结果在输出目录 `result.json`，截图仍需目视检查。

**macOS 已验证：** OctoSense `77b7c6b5` 的 release 程序通过签名闸门、真实工具分发、
精确状态与返回值、中英编辑、重启持久化和四类拒绝检查。关闭系统字体后，四张原生
Metal 图已检查，内容与控件完整。见 [validation.json](validation.json)。

两个私有变异版本也按预期失败：把处理器改回 `on_agent_tool` 返回
`app_handler_missing`；删除 `script-tools-v1` 在工具绑定时被拒绝。未修改参赛者仓库。
这仍是开发示例，不是上架应用，也不是模型或手机测试。
