# 贡献指南

感谢你考虑为本项目做贡献！

## 贡献方式

### 改进翻译（最欢迎）

翻译文件都在 `resources/` 目录下：
- `frontend-zh-CN.json` 等：前端界面翻译
- `desktop-zh-CN.json` 等：桌面外壳翻译

修改步骤：
1. Fork 本项目
2. 编辑对应的 JSON 文件（注意保持 JSON 格式有效）
3. 提交 Pull Request，说明改了哪些词条以及为什么

### 报告 Bug

在 [Issues](../../issues) 使用 Bug 报告模板，请尽量提供：
- 操作系统和版本
- Python 版本
- 完整的错误日志
- 复现步骤

### 提议新功能

在 [Discussions](../../discussions) 发起讨论，或用 Feature Request 模板提 Issue。

## 开发约定

- 保持单文件、无第三方依赖的设计
- 不引入修改 app.asar / 重签名的逻辑（那是完整版的范畴）
- 改动 `install.py` 后，请运行本地测试确认核心逻辑正常
- 一个 PR 只做一件事，描述写清楚

## 本地测试

```bash
# 语法检查
python3 -m py_compile install.py

# 验证翻译文件格式
python3 tests/test_resources.py
```

## 行为准则

尊重他人，建设性讨论，欢迎新手。
