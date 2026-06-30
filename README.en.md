# Claude Desktop Chinese Patch · Lightweight

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-macOS%20%7C%20Windows-lightgrey.svg)]()

> The simplest way to add Chinese (Simplified/Traditional) UI to Claude Desktop — one Python script, a few seconds to install, no app.asar modification.

[中文说明](README.md) | [Changelog](CHANGELOG.md)

![Claude Desktop Chinese UI Screenshot](docs/images/screenshot-home.png)

---

## What is this?

**claude-cowork-cn** is a lightweight open-source tool that adds Simplified Chinese / Traditional Chinese interface to the Claude Desktop app. It requires no app.asar modification, no code signing, and no third-party dependencies. Works on macOS and Windows.

It does three things:

1. Copies Chinese translation files into Claude's resource directory
2. Adds Chinese to the frontend language whitelist (so it appears in the Language menu)
3. Sets the user config locale to Chinese

Supports: Simplified Chinese (zh-CN), Traditional Chinese - Taiwan (zh-TW), Traditional Chinese - Hong Kong (zh-HK).

Optionally injects a Chinese system prompt into `~/.claude/CLAUDE.md` so Claude defaults to responding in Chinese.

## Quick Start

### macOS

```bash
git clone https://github.com/sheldum03/claude-cowork-cn.git
cd claude-cowork-cn
sudo python3 install.py
```

### Windows

```powershell
git clone https://github.com/sheldum03/claude-cowork-cn.git
cd claude-cowork-cn
# Right-click install-windows.bat -> Run as Administrator
# Or in an admin PowerShell:
python install.py
```

Claude will restart automatically after installation with the Chinese UI active.

## CLI Options

```bash
python3 install.py                     # Interactive language selection
python3 install.py --lang zh-CN        # Specify language directly
python3 install.py --system-prompt     # Inject Chinese system prompt
python3 install.py --no-system-prompt  # Skip system prompt injection
python3 install.py --restore           # Uninstall: remove Chinese files, reset to English
python3 install.py --dry-run           # Preview only, no actual changes
```

## Coverage

The lightweight patch covers approximately 70% of the UI — main chat window, sidebar, settings, and common dialogs. System menu bar items and some online claude.ai content remain in English. For full coverage, see [javaht/claude-desktop-zh-cn](https://github.com/javaht/claude-desktop-zh-cn).

## How it Works

`install.py` is a single-file script with zero dependencies:

1. Locates the Claude Desktop installation (auto-detects macOS/Windows)
2. Merges Chinese translation JSON with the existing en-US.json (untranslated keys fall back to English)
3. Patches the language whitelist in the frontend JS bundle via regex
4. Sets `locale` in `~/Library/Application Support/Claude/config.json`

No binary patching, no integrity hash changes, no re-signing.

## Requirements

- macOS 10.14+ or Windows 10+
- Python 3.7+
- Claude Desktop installed

## Uninstall

```bash
python3 install.py --restore
```

## Credits

Translation resources from [javaht/claude-desktop-zh-cn](https://github.com/javaht/claude-desktop-zh-cn).

## License

[MIT](LICENSE)
