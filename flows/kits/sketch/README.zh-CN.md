# Sketch 套件导入：Sketch → 原生控件 → 检查 → 修复

[English](README.md) | 简体中文

本流程从已获授权的 Sketch 设计套件生成**主题套件**（theme kit）。它不是应用设计流程。分步契约见 `FLOW.md`。

入口：在仓库根目录运行 `tools/beauty-pipeline.sh`。对于购买的设计套件，推荐的首选渲染器是**通过 release 版 Makepad Studio 运行的 splash-makepad**。较早的 theme/LLM L0 与桌面/设备通道仍保留在 `run_kit.py` 中，供已有的套件配置使用；本文不再记录或维护它们，桌面通道的客户端现已迁至 [OctoSense `apps/appcard`](https://github.com/OctoSense-org/OctoSense/tree/main/apps/appcard)。

全新安装请使用[通用复现指南](../../core/REPRODUCE.md)和[套件配置示例](../../core/examples/sketch-kit.json)。它们用本地输入替代了个人归档路径和设备设置。默认的原生循环会记录明确的外部视觉评审；它不需要模型服务商账户，也不会调用模型 CLI。参见[评审者契约](../../core/MODEL-REVIEW.md)。

对于 AI 生成的 UX 图像，请使用[图像到控件分支](../../image-lib/README.md)：`tools/beauty-pipeline.sh --ux-image --design weather-01`。它会保存明确的字体与布局提示词，测量实际生成的图像，挂载原生 L0 套件，并把 Studio 检查结果与截图差异合并进每一轮修复。首批评审集包含 10 个 Weather、10 个 News 和 10 个 Stocks 布局。图像分支的[明确映射规则](../../image-lib/MAPPING-RULES.md)要求在编译前使用原生的数据绑定图表和有文档记录的美术素材。它的语义审计独立于旧的 Sketch 矢量几何路线。

## 合成了什么

`input_format: "design"` 路线导入按源文件测量的 `.splash` 树，并用 `octoscript_makepad::design` 生成原生 Makepad 控件。它保留 Sketch 的分组层级和源 ID。这是固定布局的视觉移植；它不建立可复用的 L0–L3 组合、响应式行为，也不构成完整应用。

| Sketch 元素 | 原生合成 |
|---|---|
| Group | 带明确尺寸和绝对位置的嵌套 `View` |
| 文本 / 富文本 | `Label` / `DesignText`，内含可逐个检查的标签 |
| 可编辑字段 | `DesignInput`，派生自 `TextInput` |
| 按钮 | 源 `View` 内的原生 `Button`，保留可检查的标签和图形 |
| 选择胶囊 | 原生 `CheckBox`，配一个可独立检查的 `Label` |
| 滑块 / 区间 | 原生 `Slider`，包括两个可独立拖动的手柄 |
| 旧版 Taskplan 标签页 | `DesignButton`，一个保留源子节点的自定义 `View` |
| 开关 / 复选框 | 原生 `Toggle` / `CheckBox`，按套件样式化 |
| 单选 | Camo 使用原生 `RadioButton`；旧版 Taskplan 使用 `DesignRadio` |
| 简单形状、背景、边框 | 原生 `View` 表面属性 |
| 圆角玻璃 | 原生 `GaussRoundedView`，带源着色和模糊 |
| 玻璃提示框轮廓 | 原生 `Svg` 配 Gauss 背景纹理；标签和图标保持为控件 |
| 仅图形的 Overlay 混合 | 采样背景的原生 `Svg`，带源着色合成 |
| 旋转文本 | 原生 `DrawRotatedText`；源标签仍可检查 |
| 图标、装饰路径、受支持的效果 | 原生 `Svg` 曲面细分，保留原始画布 |
| 定量图表、波形、进度 | 原生数值控件和经评审的数据绑定；绝不使用静态 SVG/Image 绘制 |
| 照片或不受支持的图形特性 | `Image`，并逐元素记录回退原因 |

**优先使用 Makepad 原生控件，除非源特性无法表达。**新套件设置 `native_widgets_first: true`（见 `atro-native-all.json`）。现有 Taskplan 模板早于这一策略，包含许多图层 Image，包括按钮背景。新的合成先使用原生表面、文本和控件，再对受支持的矢量几何使用原生 SVG。位图回退必须指明源照片或不受支持的蒙版/滤镜特性；它不能悄悄替代文本、控件或整个屏幕。控件识别依赖套件的源符号；未知变体需要明确的映射和验证。整屏参考截图和文本不得成为实现素材。复合路径可以保持为单个图形，并保留其源祖先链。定量区域是例外：两个导入分支现在共用 `flows/core/policy.py` 和同一套映射规则。Sketch 合成的验收要求每个画板都有 `native/semantics/<screen>.json`，其中包含绑定到源层级和参考哈希的完整 `source_review`。被提名的图表/进度区域需要逐一决策。这些决策保留源 ID、确切的绘制归属、单位、定义域和数据来源。具名候选只是评审辅助；匿名数据区域必须明确标注。`semantic_lowering.py` 把折线、面积、环形、柱状、雷达、散点、波形和进度区域降级为原生数值适配器，同时把文本和控件保留为控件。源蒙版成为包裹数值绘制的原生裁剪容器。渐变、柱宽、气泡半径、弧形几何和雷达轴都有明确的、源自设计稿的样式和数值。不受支持的图表类型会失败，直到有对应适配器。`curve.py` 可以把单条经评审的 SVG 曲线测量为近似的归一化采样；这些采样不是还原出的业务数值。Studio 必须报告实际数组。尚未迁移的旧套件需要先完成语义迁移，其早先的视觉验收才能满足这一更严格的门禁。Taskplan、Atro 和 Camo 已完成迁移；源评审、导入、L0 提升和全新 Studio 验证步骤见[旧套件迁移](../../core/OLD-KIT-MIGRATION.md)。

关于常驻 Studio 桥接、超高画板的分配、声明式修复和重启协议，见[共享循环指南](../../core/README.md)。玻璃覆盖层属于拥有它的组件；提示框不得把画板背景移出场景捕获。当嵌套表面共享 Makepad 的背景纹理时，覆盖型玻璃材质保留其源着色来源。画板大小的玻璃背景在场景捕获中保留其前面的照片；之后的内容和重叠控件绘制在玻璃之上。源按钮的点击区域内边距不得把其标签放到玻璃背景之后。普通玻璃着色在 Overlay 混合之前合成。复选框的镂空保持透明，因此其标记显示的是实际背景而非固定颜色。玻璃覆盖在画板裁剪区域内评估，包括源背景超出画板边缘的键盘。模糊半径仍以逻辑点为单位；原生采样会考虑纹理 DPI 和 Gauss 重建核。SVG 玻璃使用与圆角表面相同的分数 mip 重建。源 alpha 蒙版给出的覆盖范围才能证明复合玻璃形状是否真正覆盖了另一种材质；仅凭包围盒无法证明。任何被推迟到玻璃之上的图形，也会推迟之后重叠的绘制，包括位于原始玻璃边界之外、但在导出阴影画布之内的标签。固定高度的文本框保留完整的原生文本，并把绘制裁剪到源文本框内。旋转图形使用变换后的边界做可见性检查。分组的旋转和镜像会传递到子几何和蒙版链。Sketch 的镜像在旋转后的父级坐标轴中应用。未绘制的蒙版轮廓保留其原生布局容器，而不凭空生成可绘制的 SVG 几何。独立蒙版自身的绘制仍受其祖先蒙版约束。Alpha 蒙版保留其填充和渐变用于后代覆盖，而不会绘制一个独立的黑色表面。轮廓蒙版只贡献其形状。Atro 使用 Sketch 文档中内嵌的确切 Montserrat 字重；它们的版本和哈希保存在 `native-fonts.json` 中。混排的 emoji 基线不代表多出一行文本。Sketch 不绘制的尾随段落换行保留在源来源记录中，不会生成空的原生布局行。明确的段落高度包含 Sketch 的居中行距；垂直对齐的文本也在源框内保留其偏移。导入器会补上 SVG 中缺失的偏移，并检测已包含行压缩的基线，避免在较短的固定行框上再次上移。

Camo 的 `camo-native-all.json` 覆盖 246 个移动端屏幕，包括 Sketch 页面名称相同的浅色页和深色页。页面 ID 和明确的画板名称防止一个主题覆盖另一个。归档中的 DM Sans 字体按字节原样安装并打包；平台字体使用本地文件资源。在 Sketch 解除符号或导出参考之前，CoreText 必须解析到确切的字体名称和文件。字体哈希和注册证据变化时，源缓存随之失效。SVG 文本只继承一次 `fill-opacity`，而分组不透明度会叠加合成。密码圆点映射为可编辑的掩码 TextInput 字形，并带有测量得到的墨迹和间距。按钮外阴影可以穿过透明的全尺寸包装层作用到其不透明背景上，而不会把标签拍平。已完成的导入只有在源、导入器、套件和每个生成素材的哈希都仍然一致时才会续用。Camo 的控件和截图需要与其他原生模板相同的 Studio 检查、交互和视觉门禁。Apple Color Emoji 在原生 Label 中使用测量得到的 CoreText 光学尺寸和位图基线偏移。Emoji 阴影保持原生：CachedView 渲染 Label 的 alpha 生成 Gaussian 阴影，前景则单独检查。SVG 填充规则会传递到原生曲面细分，包括 nonzero 重叠和反向绕行的孔洞。需要不受支持背景的祖先 Multiply/Soft Light 效果会成为带源上下文的单独图形回退；该路径会拒绝绘制区域内的文本或控件。要精确指定修复集合，请重复使用 `sketch_native.py --screen <exact-name>` 参数；`--only` 仍按子串选择。零 alpha 的源导出保留其哈希证据和原生布局边界，包括复合运算数 View。它们不会生成永远无法返回绘制边界的空 SVG 绘制节点。不透明分组的前景着色会传递到原生文本而不将其栅格化。当 Sketch 导出的 SVG 端点与栅格参考不一致时，线性渐变会从 Sketch 原始的点坐标空间值重建。坐标保留科学计数法，包括接近零的渐变端点。原生 SVG 按源的端点样式、连接方式、偏移和奇数长度模式渲染虚线描边。轴对齐矩形阴影使用 Makepad 的圆角矩形模糊渲染器。不受支持的背景混合只使用受影响图形的覆盖范围，并需要其源背景来计算混合。孔洞和内边距保持透明。导出器会拒绝任何与源文本相交的此类回退。报告记录该限制、相关的源 ID 和覆盖哈希。这也包括位于前景照片之上、而该照片被排除在 Window Gauss 共享场景纹理之外的单独效果。照片仍是 Image 控件，前景文本和控件仍为原生；回退只覆盖受影响的图形。Overlay 阴影和不受支持的 SVG 图案绘制保留该背景上下文，而不会把孤立的图层导出悄悄变成普通的 alpha 混合。

`composition.json` 记录路线、布局限制、每个屏幕生成的节点数量和清单哈希。数量是控件实例数，不是唯一素材数或屏幕覆盖率。仅有这个文件本身并不构成验收门禁。独立的 `composition-gate.json` 依据源归属、后端决策和素材名称审计生成的绘制控件。它会拒绝：无归属的 Images/SVGs、缺少位图原因、声称是源照片却没有位图参考、被拍平的画板、包含源文本/控件的绘制，以及被容器替代的文本/控件。画板大小的源照片是允许的，前提是其标签和控件仍为独立的原生控件。每个屏幕的 `.composition.json` 报告列出每个失败项的素材决策以及源/控件 ID。该策略审计本身并不能判断某个不受支持的渲染器特性是否可以实现；回退原因仍需要有源依据的评审。

## 一个循环

原生设计现在可以提升为 **Taskplan、Atro 和 Camo** 的可复用 L0 套件。原生导入之后运行 `python3 promote_l0.py --kit camo-native-all`（或 `atro-native-all` / `taskplan-native-all`）。它会把主题测量得到的 token、有类型的基础组件和复合组件写入 `Octoscript-Makepad/components/l0/native/`，并把 `.card`、`.data.json` 和 `.l0map.json` 屏幕实例写入 `work/<family>/native/l0/`。

用同一个 Studio 循环验证生成的 `camo-l0-all`、`atro-l0-all` 或 `taskplan-l0-all` 套件。`gate_kit.py` 还会检查共享定义、跨屏复用、完整的 Sketch 归属以及原生树等价性。`semantic_widgets.py` 能识别完整的按钮、字段、导航、项目卡片和音乐行。共享定义拥有其图层，并接收一个实例 ID 加上具名的内容/状态参数；宿主部件绑定保留 Sketch ID。运行时从 `octoscript-widgets::kit` 挂载 `KitButton`、`KitFormField`、`KitTabBar`、`KitBottomNavigation`、`TaskplanProjectCard` 和 `CamoTrackRow`。公共默认值在 `roles.l0` / `semantic_roles` 中。门禁要求每个被提升的边界都使用这些实际的 Studio 控件类型；同名的通用 View 不能通过。明确映射的透明原生控件填补 Atro 被动标签页和卡片/行操作的空隙，同时离线审计仍要求每个原始源属性和子节点都匹配。`semantic_interactions.py` 对照原生控件检查每个组件的初始启用/选中状态，然后在每个屏幕上操作所有导航项以及具有代表性的按钮/字段/卡片/行的操作和 setter，把观察结果记录在 `.semantic-interactions.json` 中，并恢复源状态。这些发现会进入修复交接，失败或缺失的语义证据会使套件门禁失败。导航探测还会以每通道 3/255 的容差采样选中/未选中的背景和下划线；状态标志变了而绘制未更新会失败。它们使用初始截图的源状态调色板来考虑合成的模态遮罩。不一致的调色板采样会失败，而不是掩盖遮挡。如果在同一测量位置由另一个原生控件接收了点击，探测会记录该遮挡并选择一个暴露在外的按钮。组件探测失败会在其余屏幕上继续收集，最后一起使运行失败。点击点还会排除测量得到的裁剪矩形内之后绘制的原生控件，因此浮动操作按钮不会拦截单选探测。完全被覆盖的控件会被记录，但不会声称已覆盖点击。缺失/仅宿主的检查仍会使结构门禁失败。逐元素的套件失败会与结构和视觉发现一起进入修复报告。

原生控件的实现是 `octoscript-widgets::design` 和 `octoscript-widgets::kit` 中可复用的注册项，与 beauty 宿主分离。标准 L0 文本角色也会接收导入的源字体和测量得到的字号。源屏幕模板保留固定画板布局；响应式布局和完整的应用工作流需要各自的证据。

`inherit_visual.py --kit <family>-l0-all` 只有在完整的 target/capture/prompt 哈希完全一致时，才能沿用已有的视觉结论。它从不复用结构检查、不给出新评分，也不接受发生变化的像素。发生变化的图像对需要重新做截图评审。参见[原生 L0 套件契约](https://github.com/OctoSense-org/Octoscript-Makepad/blob/main/docs/native-l0-kits.md)。

1. **导入源文件。**校验归档和源文档；在副本中解析符号和覆盖项。把原始 Sketch 画板导出为参考图。保留源 ID、层级、框架、字体、文本、蒙版和控件状态。
2. **合成控件。**生成经过检查的 Splash 树，并把节点映射为原生控件。优先使用内置控件和原生属性；保留文本和可编辑控件。对其余受支持的矢量使用原生 SVG。逐个导出回退图形，并考虑绘制边界、蒙版和阴影。不受支持的映射会失败，需要有源依据的实现。保持语义组件边界：按钮拥有其点击目标、标签、图标、背景和状态，即使它们通过不同的控件绘制。其底层绘制节点的数量与其可复用组件状态分开统计。
3. **在 Studio 中渲染。**启动 release 版 RunItem，设置画板视口，挂载生成的树，并等待字体、布局和解码后的图像纹理就绪。保存原生截图，拒绝空白、不完整或尺寸错误的捕获。在 Studio 初始标签页布局之后确认嵌入视口；如果该布局替换了请求的画板尺寸，就重复调整大小。当根节点仍被裁剪在 Studio 的初始视口内时，不要保存布局 nonce；等待整个画板的绘制区域。只消费返回给本桥接的临时截图，且在成功复制证据之后；复制失败的截图会保留其 Studio 源以便恢复。
4. **检查结构和控件。**使用 WidgetTreeDump、对每个生成 ID 的精确 WidgetQuery 以及 WidgetSnapshot。关联回 Sketch ID，比较层级、边界、可见性、文本、裁剪和控件状态。在存在相应控件时，操作原生输入的键入/恢复、密码掩码、焦点、复选框/开关点击以及两个滑块手柄，并恢复状态。对同一组源和生成的清单运行原生合成门禁；声明了 `native_widgets_first` 却没有原生控件映射不能通过。
5. **评审截图。**比较原始 Sketch 与原生输出的排版、颜色、图像和效果。要求当前结论为 `accept` 且评分至少 9/10（除非套件明确配置了阈值）。评审副本使用原生像素尺寸，透明的导出像素用白色窗口背景填充；原始 Sketch 导出保持不变。两个评审输入在评审者读取之前都会按内容哈希冻结。部分评审会保留其他屏幕的结论。相互独立的冻结图像对按有界批次评审（`--workers`，默认 3），由一个结论写入者写入。某个请求失败时，会保留同一批次中其他已完成的评审。文件锁还会串行化不同的评审调用，使聚焦修复不会覆盖完整运行中较新的行。有争议的视觉发现可以借助 `visual_evidence.py` 进行基于证据的追加评审。它保存测量的区域和原生边界，保留原始结论，并请求对完整图像对重新评审。门禁会校验所有证据哈希并保持相同的评分阈值；单凭测量或追加评审都不能推翻结构失败。
6. **修复并重新捕获。**阅读 `repair-feedback.json` 和逐元素报告，修复负责的导入器、控件、渲染器或素材导出代码，重新生成并重复。导入器会把之前的发现记录在 `.repair-input.json` 中；它不会自动编造代码修复。旧版 L0 作者可以在 LLM 修复轮次中使用这些发现。不要为了让缺陷通过而放宽容差。即使结构和截图评审都通过，合成失败也会进入逐屏修复队列。让 `acceptance.json` 中尚未完成的组件、布局和工作流工作保持可见，作为下一轮合成的内容。

`beauty` 运行一次导入/编写 + 原生捕获/检查/评审循环。修复后请重新运行。对于共享控件或渲染器的修复，请重新验证整个套件；一次小范围的成功探测并不能让未测试的屏幕通过。

## 从视觉模板到可复用页面

现有的设计导入器完成了固定画板的复现循环。下一轮合成有独立的要求：

1. 识别重复出现的源符号和语义分组，例如应用栏、按钮、字段、卡片和列表行。把每个实例映射为一个具名的共享组件，带有源 ID、属性、插槽和控件状态。重复的绝对定位 `View` 树并不构成复用。
2. 用原生流式容器、Fill/Fit 尺寸、内边距、间距和对齐来组合页面区块。内容可能超出视口时使用滚动。绝对定位只保留给有意的覆盖层和内部美术。
3. 渲染参考视口以及至少两个额外配置的宽度。在每个尺寸下检查边界、换行、裁剪和缺失内容；包括长文本和溢出情况。在每个尺寸下比较截图样式，有源参考时使用源参考，其余情况使用明确的布局预期。
4. 针对预期的状态迁移，操作导航、提交、选择和滚动。包括焦点、禁用和错误状态。原生 Button 的点击目标并不能证明其应用操作已接通。
5. 修复共享组件并重新验证其使用者。保留每个视口的截图、Studio 检查、状态迁移和源映射。

`acceptance.json` 明确报告 `scope: "fixed_artboard_parity"`。被提升的 L0 套件通过 `gate_kit.py` 建立共享组件复用，包括原生语义类型和组件行为。响应式布局和应用工作流仍为 `not_established`，并附有所需证据和下一步修复操作。组件事件并不能证明完整的应用工作流；数量、截图评分或配置标志都不能把它们提升为通过。

## 设置与运行

使用 `../core/examples/sketch-kit.json` 作为可共享的配置示例。为每个套件设置独立的输出目录、`source_archive`、`pages`、精确的 `screens`、`input_format: "design"`、`native_widgets_first: true`、`reference_renderer: "Sketch"`、`rails: ["splash-makepad"]`、`studio_embedded: true` 以及正确的 `design_scale`。把归档以及生成的模板/素材放在被忽略的 `work/` 下；不要发布购买的套件内容。

在 `flows/kits/sketch/.venv` 中按 `requirements.txt` 安装 Python 依赖。把 `SKETCHTOOL` 设为 Sketch.app 的原生 CLI，把 `CARGO_MAKEPAD` 设为打过补丁的 release 版 Studio 桥接。该桥接必须转发 WidgetSnapshot。使用 [Taskplan 报告](https://github.com/OctoSense-org/OctoScript-App-Design-Flow/blob/cbbda4da0a9d0fbf13497335dd3342b71f35e71f/docs/reviews/taskplan-native-parity-2026-09-05.md)中记录的开发版 Studio 视口持久化和后备缓冲分配修复。

用 `python3 tools/setup-native.py` 准备共享运行时（见 [NATIVE-WORKSPACE.md](../../../docs/NATIVE-WORKSPACE.md)）。启动 Studio 时，用一个 `splashref` 挂载指向准备好的 `octoscript-makepad` 检出，它默认位于本仓库旁边：

```sh
bash tools/beauty-studio.sh /path/to/makepad/target/release/makepad-studio --remote \
  --mounts="splashref:$(cd .. && pwd)/octoscript-makepad" \
  --bind=127.0.0.1:8001
export CARGO_MAKEPAD=/path/to/makepad/target/release/cargo-makepad
export SKETCHTOOL=/path/to/Sketch.app/Contents/MacOS/sketchtool
```

然后在仓库根目录运行：

```sh
# One full cycle, including saved findings from a previous native round.
tools/beauty-pipeline.sh --kit atro-native-all --stages beauty

# Rerender existing templates after a native runtime change.
tools/beauty-pipeline.sh --kit atro-native-all --stages splash-makepad

# Rerun all acceptance gates against saved evidence; no Studio build or new judge call.
# Missing/stale evidence or any gate failure exits nonzero and saves repair findings.
tools/beauty-pipeline.sh --kit atro-native-all --stages audit

# Refresh the composition/feedback/gallery from saved evidence; no GPU or judge call.
tools/beauty-pipeline.sh --kit atro-native-all --stages report
```

`author` 单独导入原生设计，而 `validate` 在无 UI 的情况下运行经过检查的组装。`doctor` 检查配置的依赖和门禁测试；在套件输入导入之后运行一次。UI 的构建和运行只通过 Studio RunItem 进行；验证改动前请清除上一次构建。`--rounds` 控制旧版作者阶段，而不是自动的原生代码修复。

## 验收与保存的证据

每个配置了源映射的设计屏幕都必须通过结构、原生合成策略和视觉评审。旧版 L0 卡片没有源映射的合成审计，在该门禁上被明确标记为 `not_applicable`。在原生优先策略之前导入的设计套件必须先迁移并重新导入才能通过；缺失或关闭的策略设置会失败。仅宿主的检查、缺失元素、缺失查询响应、错误的文本或状态、不可用的纹理、过度裁剪以及过期证据都会使验收失败。截图评分不能推翻结构失败。填充分析仍是附加诊断，不能替代任一门禁。

| 结构测量 | 默认容差（逻辑点） |
|---|---|
| 位置、对齐、间距 | 4 |
| 宽度和高度 | 6 |
| 裁剪 / 意外的文本溢出 | 2 |
| 各检查 API 之间的一致性 | 1 |

实际生效的 `structure_tolerances` 保存在每份结构报告中。参考/捕获/评审哈希把证据绑定到源、资源、二进制、检查数据和评审提示词。仅凭保存的 PNG 或以往的高分不能通过。

每个捕获旁边都有 `.portable.json`、`.native.json`、`.widgets.json`、`.queries.json`、`.snapshot.json`、`.layout.json`、`.structure.json`、`.capture.json`，以及适用时的交互证据。该目录还包含 `visual-gate.json`、`composition.json`、`composition-gate.json`、`acceptance.json`、`pipeline-run.json`、`repair-feedback.json` 和 `gallery.html`。画廊并排展示 Sketch 与 Makepad，并链接到结构差异、原生状态和合成信息。渲染器或评审失败时仍会生成修复/画廊交接，且原生阶段以非零状态退出。`report` 刷新产物；它不会修复失败的流水线运行，也不会凭空生成新的截图结论。`audit` 在最新的运行回执中记录 `operation: "audit_saved_evidence"`；它重新检查已有的捕获和评审，从不声称进行了新的渲染。

导入器、原生渲染器和截图评审者都接受重复的 `--only` 屏幕名子串，用于聚焦修复。共享改动之后请运行完整的原生阶段；聚焦的证据不能证明整个套件通过验收。

## 结果与限制

Camo 的 246 个移动端模板于 2026-09-06 通过了原生结构、合成和视觉门禁。Studio 构建 63 检查了 29,929 个节点；所有截图对的评分为 9–10/10。[Camo 报告](https://github.com/OctoSense-org/OctoScript-App-Design-Flow/blob/cbbda4da0a9d0fbf13497335dd3342b71f35e71f/docs/reviews/camo-native-parity-2026-09-05.md)链接了完整的对比画廊、修复证据和固定画板范围。

Atro 的 150 个画板原生运行通过了其配置的固定布局结构和视觉门禁：3,009 个文本节点、279 个 Button、48 个 Input、3,935 个 SVG 控件和 919 个 Image 实例，另有原生表面和选择控件。其保存的模板也通过了原生合成审计。范围和时效见 [Atro 报告](https://github.com/OctoSense-org/OctoScript-App-Design-Flow/blob/cbbda4da0a9d0fbf13497335dd3342b71f35e71f/docs/reviews/atro-native-parity-2026-09-05.md)以及当前生成的 `acceptance.json`。

Taskplan 的 79 个画板运行通过了其配置的原生结构和视觉门禁：1,952 个文本节点、97 个输入框、7 个开关、4,012 个图像节点和 8,672 个容器节点。容器包含组合控件。见[完整报告](https://github.com/OctoSense-org/OctoScript-App-Design-Flow/blob/cbbda4da0a9d0fbf13497335dd3342b71f35e71f/docs/reviews/taskplan-native-parity-2026-09-05.md)。这一历史结果早于强制执行的原生优先合成门禁以及之后的共享运行时改动；它不是当前的验收结果。

这些历史结果验证的是固定画板的复现。生成的 L0 套件现在增加了共享原生组件、组件操作和选中状态；它们的当前证据在 L0 对比索引（`work/l0-themes/index.html`）和每个 `l0-captures/acceptance.json` 中。响应式重排和完整的应用工作流需要单独的实现和测试。更早的五屏 L0 Taskplan 运行仍是一个失败的基线，记录在 [TASKPLAN-VALIDATION.md](TASKPLAN-VALIDATION.md) 中。

### 在现有 Octos 应用中使用套件组件

提升过程现在还会通过 `export_app_recipes.py` 导出 `Octoscript-Makepad/components/l0/native/app-recipes.json`。这些紧凑的配方保留源组件 ID、源屏幕名称、套件哈希和原生部件样式。用 `--check` 运行导出器可检测过期的配方。首批应用适配器把 Weather 与 Atro 控件、Stocks 与 Camo 行/标签页、News 与 Taskplan 卡片组合在一起。它们与 Sketch 宿主共用原生套件类的实现，并把已有的 L0 值/操作绑定到真实的 Button、Label 和 TextInput 子控件上。

应用适配有其自己的门禁：源关联的原生组件和子绑定必须在 Studio 中存在，控件状态和交互必须可用，测量得到的滚动画布必须包含最终的组合结果。流式的应用布局是有意的适配，不会继承画板一致性的通过结果。前后对比捕获、逐元素差异、源映射和验证脚本位于 [`docs/reviews/theme-phone-evidence/components/`](https://github.com/OctoSense-org/OctoScript-App-Design-Flow/tree/cbbda4da0a9d0fbf13497335dd3342b71f35e71f/docs/reviews/theme-phone-evidence/components)（已从此处移除；保留在历史中）。

页面结构是一个单独的适配步骤。六个人工编写的 L0 配方现位于 `Octoscript-Makepad/components/l0/pages/`：Weather 仪表盘/预报、Stocks 磁贴/图表，以及 News 杂志/紧凑版式。它们替换具名视图，同时保留应用的源/状态/事件声明。例如，内置的选择器可以选择 `weather@atro_light/dashboard`。每个适配后的页面都必须通过原生组件检查以及拓扑检查（区块顺序、列边界、条目数量、滚动和操作）；仅改变颜色无法满足该门禁。手机端对比和逐元素修复证据位于 [`docs/reviews/theme-phone-evidence/structures/`](https://github.com/OctoSense-org/OctoScript-App-Design-Flow/tree/cbbda4da0a9d0fbf13497335dd3342b71f35e71f/docs/reviews/theme-phone-evidence/structures)（已从此处移除；保留在历史中）。这是一个明确的人工编写配方层，而不是为每个移植的主题自动生成页面。
