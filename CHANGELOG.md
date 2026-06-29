# 变更日志

本项目遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [Unreleased]

### 新增
- 安装前自动退出 Claude、安装后自动重启，使中文语言设置立即生效，无需手动切换
  - 解决了"安装后仍显示英文、需手动切语言"的问题（原因是 Claude 运行时退出会用内存里的旧 locale 覆盖配置）
- 可选功能：往 `~/.claude/CLAUDE.md` 注入中文指令，让 Claude 默认用简体中文回答和写代码注释
  - 安装时交互询问，或用 `--system-prompt` / `--no-system-prompt` 直接指定
  - 带注释标记的幂等写入，`--restore` 时干净移除，不影响用户已有内容

### 改进
- `quit_claude` 改用轮询等待，最多 8 秒，超时才强杀，降低数据损坏风险
- `quit_claude` 新增进程检测，未运行时跳过退出
- `launch_claude` Windows 下递归查找 `Claude.exe`，支持版本子目录结构
- `restore` 流程对称地加入退出/重启，确保卸载后配置正确恢复
- 安装失败时也会重启 Claude，避免用户发现 Claude "消失了"
- `patch_language_whitelist` 简化判断逻辑，消除冗余和潜在误判
- `set_user_locale` 在配置损坏时先备份为 `.bak-invalid` 再覆盖，降低数据丢失风险

### 计划中
- 可选的硬编码文本替换模块（提升覆盖率到 ~80%）
- 自动备份功能
- 监控 Claude 新版本兼容性的 CI

## [1.0.0] - 2026-06-28

### 新增
- 首个正式版本
- 核心功能：复制翻译文件、修改语言白名单、写入用户配置
- 前端翻译与目标机器 en-US.json 按 key 合并，未翻译内容回退英文
- 支持简体中文、繁体中文（中国台湾）、繁体中文（中国香港）
- macOS 原生菜单 .strings 资源安装
- 一键安装入口：`install-mac.command`、`install-windows.bat`
- 命令行参数：`--lang`、`--restore`、`--dry-run`
- 恢复功能

### 技术特点
- 单文件脚本，无第三方依赖
- 不修改 app.asar，不重签名
- 跨平台支持 macOS 和 Windows
