# DeepSeek Harness 任意门卜卜主题

为 DeepSeek Harness Web 界面制作的“任意门”卜卜主题插件。

它会把默认品牌区替换为任意门卜卜形象，并加入五个卜卜欢迎画面、手绘道路、公交车、彩色工作区图标和工作中的橙色卜卜。主题支持浅色、深色和“跟随系统”，macOS 切换外观后会自动适配。

<p align="center">
  <img src="assets/plugin/dsh-theme-anydoor/assets/dsh-five-bobu.png" alt="五个任意门卜卜" width="420">
</p>

## 主要功能

- 独立 Cordis 客户端插件，不覆盖 Harness 官方四个 UI 模块。
- 侧边栏显示卜卜图标和“任意门”品牌名。
- 首屏显示五个卜卜、双行标语、手绘道路和右下角公交车。
- 工作区使用彩色圆点图标，模型选择区显示工作中的橙色卜卜。
- 自动适配浅色和深色模式，也支持“跟随系统”实时切换。
- 使用独立插槽优先级，避免 `single slot` 重复注册报错。
- 安装前自动备份，支持一键恢复到安装前状态。
- 安装脚本可重复运行，已安装最新版时不会重复修改。

## 适用环境

当前版本：`dsh-theme-anydoor 1.1.0`

| 项目 | 要求 |
| --- | --- |
| 操作系统 | macOS |
| DeepSeek Harness | `0.1.1-rc.2` |
| Python | 能运行 `python3` |
| Node.js | 能运行 `node` |
| 默认页面 | `http://127.0.0.1:3080/` |

> 本项目只安装主题，不负责安装 DeepSeek Harness。请先确认原版 Harness 能正常启动，并至少运行过一次 `dsh web`。

## 安装方法一：下载 ZIP（适合普通用户）

1. 打开本仓库首页，点击绿色 **Code** 按钮。
2. 点击 **Download ZIP**，下载后双击解压。
3. 打开“终端”。输入 `cd` 和一个空格，然后把解压后的文件夹拖进终端窗口，按回车。
4. 先运行只读检查：

   ```bash
   python3 scripts/theme_manager.py status
   ```

5. 确认输出中的 Harness 版本是 `0.1.1-rc.2`，再执行安装：

   ```bash
   python3 scripts/theme_manager.py install
   ```

6. 安装成功后，终端会显示一行以 `Restart:` 开头的命令。复制并运行这条命令。如果旧服务仍在运行，先在它的终端窗口按 `Control + C` 停止。
7. 浏览器打开：<http://127.0.0.1:3080/>
8. 如果还是旧画面，按 `Command + Shift + R` 强制刷新一次。

## 安装方法二：使用 Git

```bash
git clone https://github.com/zhuguli1021-eng/install-deepseek-harness-anydoor-theme.git
cd install-deepseek-harness-anydoor-theme
python3 scripts/theme_manager.py status
python3 scripts/theme_manager.py install
```

安装完成后，运行脚本输出的 `Restart:` 命令，再访问 <http://127.0.0.1:3080/>。

## 如何确认安装成功

再次运行：

```bash
python3 scripts/theme_manager.py status
```

正常结果应包括：

```text
Theme status: installed
Profile dependency: configured
Loader patch: configured
```

也可以检查服务和图片资源：

```bash
curl -s -o /dev/null -w 'page HTTP %{http_code}\n' http://127.0.0.1:3080/
curl -s -o /dev/null -w 'asset HTTP %{http_code}\n' http://127.0.0.1:3080/assets/dsh-brand-bobu.png
```

两个结果都应为 `HTTP 200`。

## 更新到最新版

通过 Git 安装的用户：

```bash
git pull origin main
python3 scripts/theme_manager.py install
```

通过 ZIP 安装的用户：重新下载最新 ZIP，解压后再次运行：

```bash
python3 scripts/theme_manager.py install
```

更新后需要重新运行脚本显示的 `Restart:` 命令。

## 卸载或恢复

查看可用备份：

```bash
python3 scripts/theme_manager.py backups
```

恢复最近一次安装前的状态：

```bash
python3 scripts/theme_manager.py restore
```

恢复后同样需要重启 Harness。脚本只恢复安装清单里记录的文件，不会删除整个 `~/.dsh` 目录。

## 常见问题

### 提示 `Unsupported Harness version`

当前主题只验证过 Harness `0.1.1-rc.2`。脚本会主动停止，不会把该版本的样式强行安装到其他版本。

### 打不开 `127.0.0.1:3080`

这通常表示 Harness 服务没有运行。重新执行安装脚本最后显示的 `Restart:` 命令。

### 安装后仍然显示旧主题

先重启 Harness，再按 `Command + Shift + R` 强制刷新浏览器。

### 出现 `single slot ... priority 0` 报错

请更新到本仓库最新版并重新执行安装。本版本已把任意门品牌插槽设为 `priority: -1`，避免与官方优先级 `0` 冲突。

### 深色模式下文字看不清

请确认安装的是 `1.1.0` 或更新版本。本版会读取 Harness 的 `data-ds-dark-theme` 标记，在浅色和深色玻璃卡片之间自动切换。

### 自动发现了错误的 Harness 安装目录

使用 `--root` 指定包含 `dsh/package.json` 的 `@deepseek-ai` 目录：

```bash
python3 scripts/theme_manager.py status --root /path/to/node_modules/@deepseek-ai
python3 scripts/theme_manager.py install --root /path/to/node_modules/@deepseek-ai
```

## 安装器会修改哪些位置

- `~/.dsh/profiles/web/packages/dsh-theme-anydoor/`
- `~/.dsh/profiles/web/node_modules/dsh-theme-anydoor/`
- `~/.dsh/profiles/web/package.json`
- `~/.dsh/profiles/web/cordis.patch.yml`
- 当前 Harness Web 前端中的 `dsh-*.png` 图片资源
- 自动备份目录：`~/.dsh-anydoor-theme/backups/`

安装器不会读取或输出账号密码、Token 或 `~/.dsh/.credentials.yaml`。

## 项目结构

```text
assets/plugin/dsh-theme-anydoor/  主题插件和图片
scripts/theme_manager.py          安装、检查、备份和恢复工具
references/compatibility.md       兼容性与验收说明
SKILL.md                          Codex Skill 工作流程
```

## 技术说明

插件通过 Harness 官方品牌插槽注册任意门组件，并把优先级设为 `-1`。官方品牌保持优先级 `0`；Harness 会显示数值更低的注册项。深色模式由 Harness 已解析的 `body[data-ds-dark-theme]` 标记驱动，因此手动选择浅色、深色或跟随 macOS 系统都能正确切换。
