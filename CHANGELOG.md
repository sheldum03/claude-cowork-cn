# 变更日志

本项目遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [Unreleased]

### 新增
- 可选功能：往 `~/.claude/CLAUDE.md` 注入中文指令，让 Claude 默认用简体中文回答和写代码注释
  - 安装时交互询问，或用 `--system-prompt` / `--no-system-prompt` 直接指定
  - 带注释标记的幂等写入，`--restore` 时干净移除，不影响用户已有内容

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
