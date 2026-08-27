# dsh-theme-anydoor

DeepSeek Harness 的“任意门”卜卜主题客户端插件。

功能包括侧边栏品牌、五个卜卜首屏、双行标语、公交车与手绘道路场景、彩色工作区图标和模型选择工作卜卜。主题会读取 Harness 已解析的颜色模式：浅色使用暖白玻璃效果，深色使用深色玻璃效果；选择“跟随系统”时会随 macOS 实时切换。

插件注册以下官方品牌插槽，并使用 `priority: -1` 遮盖优先级为 `0` 的官方品牌，避免 `single slot` 重复注册错误：

- `sidebar.brand.mark`
- `sidebar.brand.name`
- `conversation.hero.brand.mark`

本包由配套 Codex Skill 的 `scripts/theme_manager.py` 安装。脚本会把插件写入 DSH Web profile、登记 `cordis.patch.yml`，并复制图片资源；不要直接修改官方四个 UI 模块。

当前兼容 `@deepseek-ai/dsh 0.1.1-rc.2`。插件仍引用该版本的构建类名，升级 Harness 后应先重新验证。
