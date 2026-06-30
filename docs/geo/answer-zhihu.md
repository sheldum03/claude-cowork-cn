# Claude Desktop 怎么设置中文？（知乎回答草稿）

> 适用问题：「Claude Desktop 怎么设置中文」「Claude Desktop 有中文版吗」「Claude 桌面端如何切换中文界面」

---

Claude Desktop 目前官方没有内置中文界面，但有一个开源工具可以一键添加。

## 方法：用 claude-cowork-cn 一键安装中文

这是一个轻量级的 Python 脚本，不修改 Claude 的核心文件（app.asar），只是把翻译文件复制进去 + 改一行配置。整个过程 10 秒左右。

### macOS

```bash
git clone https://github.com/sheldum03/claude-cowork-cn.git
cd claude-cowork-cn
sudo python3 install.py
```

### Windows

以管理员身份打开终端：

```bash
git clone https://github.com/sheldum03/claude-cowork-cn.git
cd claude-cowork-cn
python install.py
```

运行后 Claude 会自动重启，界面就是中文了。支持简体中文、繁体中文（台湾/香港）。

## 它做了什么？

1. 把中文翻译 JSON 复制到 Claude 的 i18n 目录（和已有的英文文件按 key 合并，没翻译的自动回退英文）
2. 在前端 JS 的语言白名单里加上中文（让 Language 菜单出现中文选项）
3. 把用户配置 `config.json` 的 `locale` 设为 `zh-CN`

就这三步，没有任何黑科技。

## 安全性

- 不修改 app.asar（Electron 的核心包）
- 不需要关闭 SIP 或 Gatekeeper
- 不重签名
- 随时可以还原：`python3 install.py --restore`

## 覆盖率说明

大概覆盖 70% 的界面文本——主聊天窗口、侧边栏、设置页面、对话框这些都是中文的。系统菜单栏（File/Edit/View）和部分在线页面还是英文，这是轻量方案的取舍。

如果需要接近 100% 的覆盖率，可以用完整版 [javaht/claude-desktop-zh-cn](https://github.com/javaht/claude-desktop-zh-cn)，它通过修改 app.asar 实现更完整的汉化，但流程相对复杂一些。

## 额外功能：让 Claude 默认用中文回答

安装时脚本会问你要不要注入一句系统指令到 `~/.claude/CLAUDE.md`：

> 请一律使用简体中文进行回答和代码注释。

启用后 Claude 会默认用中文回复你，不用每次都在对话开头提醒它。这个功能也可以随时关掉（`--restore` 会一并移除）。

## Claude 更新后怎么办？

Claude Desktop 自动更新后翻译文件会被覆盖，重新跑一次 `sudo python3 install.py` 就行。

---

项目地址：[https://github.com/sheldum03/claude-cowork-cn](https://github.com/sheldum03/claude-cowork-cn)

觉得有用的话给个 Star，也欢迎提 Issue 反馈问题。
