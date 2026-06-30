# Claude Desktop 怎么设置中文？一键安装中文补丁教程（2026 最新）

## 前言

Claude Desktop 是 Anthropic 官方推出的桌面客户端，支持 macOS 和 Windows。但截至目前，官方并没有内置简体中文界面。本文介绍一个开源工具 **claude-cowork-cn**，用一个 Python 脚本就能给 Claude Desktop 添加中文界面，整个过程只需几秒钟。

## 这个工具是什么？

[claude-cowork-cn](https://github.com/sheldum03/claude-cowork-cn) 是一个轻量级 Claude Desktop 中文补丁。它的核心设计理念是：

- **不修改 app.asar**：不碰 Electron 的核心包，不破坏完整性校验
- **不重签名**：不需要关闭 macOS 的 SIP 或 Gatekeeper
- **无第三方依赖**：纯 Python 标准库实现，一个脚本搞定
- **风险极低**：只复制翻译资源文件 + 改一行配置，随时可还原

支持三种中文变体：简体中文（zh-CN）、繁体中文-台湾（zh-TW）、繁体中文-香港（zh-HK）。

## 安装步骤

### macOS

```bash
# 1. 克隆仓库
git clone https://github.com/sheldum03/claude-cowork-cn.git
cd claude-cowork-cn

# 2. 运行安装（需要 sudo 权限写入 /Applications）
sudo python3 install.py
```

或者双击仓库里的 `install-mac.command` 文件，它会自动请求管理员权限。

### Windows

```powershell
# 1. 克隆仓库
git clone https://github.com/sheldum03/claude-cowork-cn.git
cd claude-cowork-cn

# 2. 以管理员身份运行
python install.py
```

或者右键 `install-windows.bat` → 以管理员身份运行。

### 安装过程中会发生什么？

脚本会自动完成以下操作：

1. **退出正在运行的 Claude**（避免 Claude 退出时覆盖配置）
2. **复制中文翻译文件**到 Claude 的 i18n 目录
3. **修改语言白名单**，让语言菜单出现中文选项
4. **写入用户配置**，将 locale 设为所选语言
5. **重新启动 Claude**，界面即为中文

整个过程全自动，无需手动切换语言。

## 让 Claude 默认用中文回答

除了界面汉化，这个工具还有一个实用的可选功能：让 Claude 默认用简体中文回答问题和写代码注释。

安装时脚本会询问是否启用。原理是往 `~/.claude/CLAUDE.md`（Claude 的全局指令文件）写入一句话：

> 请一律使用简体中文进行回答和代码注释。

这是 Claude 官方支持的机制，纯文本写入、零风险。也可以通过命令行参数直接指定：

```bash
sudo python3 install.py --system-prompt      # 启用
sudo python3 install.py --no-system-prompt   # 不启用
```

## 翻译覆盖范围

轻量版覆盖约 70% 的界面文本，包括：

- 主聊天窗口、侧边栏
- 设置页面
- 常见对话框和提示按钮

以下部分不会被翻译（这是轻量方案的取舍）：

- macOS 系统菜单栏（File、Edit、View 等）
- 在线 claude.ai 页面的部分内容
- 少量硬编码在 JS 中的英文文本

如果需要更高覆盖率，可以使用完整版 [javaht/claude-desktop-zh-cn](https://github.com/javaht/claude-desktop-zh-cn)。

## 卸载 / 还原

```bash
sudo python3 install.py --restore
```

一条命令恢复原状：删除中文文件、重置语言为英文、移除注入的中文指令。

## Claude Desktop 更新后怎么办？

Claude Desktop 自动更新后会覆盖翻译文件，中文会消失。解决方法很简单：重新运行一次安装脚本即可。

## 常见问题

**Q: 安装后界面还是英文？**

确保安装前 Claude 已完全退出。脚本会自动处理，但如果异常情况下没退出干净，可以手动退出后重新运行脚本。

**Q: 会不会破坏 Claude Desktop？**

不会。本工具只做文件复制和配置修改，不碰核心代码。如有任何问题，`--restore` 一键还原，或直接重装 Claude 即可。

**Q: 和完整版有什么区别？**

完整版修改 app.asar 实现更高覆盖率（接近 100%），但需要重签名、流程更复杂。轻量版不碰 app.asar，覆盖率约 70%，但安装简单、风险更低、维护成本小。两者是不同取舍，不是上下位关系。

## 总结

| 特性 | 说明 |
|------|------|
| 安装时间 | < 10 秒 |
| 依赖 | Python 3.7+（无第三方库） |
| 覆盖率 | ~70% 界面文本 |
| 风险 | 极低（不改 app.asar） |
| 还原 | `--restore` 一键恢复 |
| 平台 | macOS / Windows |

项目地址：https://github.com/sheldum03/claude-cowork-cn

如果觉得有用，欢迎 Star 支持。
