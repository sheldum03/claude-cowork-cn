# Awesome List 收录 PR 准备

以下是适合提交收录的 awesome list 仓库和对应的 PR 内容。

---

## 1. awesome-claude（通用 Claude 工具列表）

**目标仓库**: https://github.com/alvinunreal/awesome-claude

**提交内容（添加到 Tools 或 Utilities 分类下）**:

```markdown
- [claude-cowork-cn](https://github.com/sheldum03/claude-cowork-cn) - Lightweight Chinese (Simplified/Traditional) localization patch for Claude Desktop. Single Python script, no app.asar modification.
```

**PR 标题**: `Add claude-cowork-cn - Chinese localization patch for Claude Desktop`

**PR 描述**:

```
Adding claude-cowork-cn, a lightweight open-source tool that adds Chinese UI to Claude Desktop.

- Single Python script, no third-party dependencies
- Supports zh-CN, zh-TW, zh-HK
- Does not modify app.asar or require re-signing
- Works on macOS and Windows
- Optional Chinese system prompt injection

Repository: https://github.com/sheldum03/claude-cowork-cn
```

---

## 2. taranjeet/awesome-claude

**目标仓库**: https://github.com/taranjeet/awesome-claude

**提交内容**:

```markdown
- [claude-cowork-cn](https://github.com/sheldum03/claude-cowork-cn) - A lightweight Chinese localization patch for Claude Desktop (macOS/Windows). No app.asar modification needed.
```

---

## 3. awesome-claude-code 系列（如果有 Desktop 相关分类）

**目标仓库**: 
- https://github.com/jqueryscript/awesome-claude-code
- https://github.com/hesreallyhim/awesome-claude-code

**提交内容**:

```markdown
### Localization / i18n

- [claude-cowork-cn](https://github.com/sheldum03/claude-cowork-cn) - Chinese UI patch for Claude Desktop. Lightweight single-script approach, supports Simplified & Traditional Chinese.
```

---

## 4. awesome-electron / awesome-i18n 类列表（备选）

搜索关键词：`awesome-electron-apps`, `awesome-i18n`, `awesome-localization`

**提交内容模板**:

```markdown
- [claude-cowork-cn](https://github.com/sheldum03/claude-cowork-cn) - Chinese localization for Claude Desktop (Electron app). Single Python script, no binary patching.
```

---

## 提交 PR 的步骤

1. Fork 目标仓库
2. 在适当分类下添加一行条目
3. 提交 commit，消息如: `docs: add claude-cowork-cn`
4. 创建 PR，标题简洁，描述说明项目是什么

建议优先提交 awesome-claude（alvinunreal 和 taranjeet 两个），因为它们与 Claude 生态直接相关，被 AI 引擎索引的概率最高。
