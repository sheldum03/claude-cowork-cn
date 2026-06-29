#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Claude Desktop 中文补丁 - 轻量版
版本: 1.0.0
仓库: https://github.com/sheldum03/claude-cowork-cn

设计理念:
    只做核心的三件事 —— 复制翻译文件、把中文加进语言白名单、写入用户语言配置。
    不修改 app.asar，不重签名，不破坏完整性校验。
    代码精简、风险低、易维护，翻译覆盖率约 70%。

翻译资源来自 javaht/claude-desktop-zh-cn 项目，特此致谢。

用法:
    macOS:   sudo python3 install.py
    Windows: 以管理员身份运行 python install.py

    可选参数:
        --lang zh-CN|zh-TW|zh-HK   指定语言（跳过交互选择）
        --restore                   恢复（删除中文文件并重置配置）
        --dry-run                   预演，不实际修改
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, Optional

VERSION = "1.0.0"

SUPPORTED_LANGUAGES = {
    "1": {"code": "zh-CN", "name": "简体中文"},
    "2": {"code": "zh-TW", "name": "繁体中文（中国台湾）"},
    "3": {"code": "zh-HK", "name": "繁体中文（中国香港）"},
}
LANG_NAME = {v["code"]: v["name"] for v in SUPPORTED_LANGUAGES.values()}

# 语言白名单：匹配 Claude 前端 JS 里的语言数组，允许已追加任意中文变体
LANG_LIST_PATTERN = (
    r'\["en-US","de-DE","fr-FR","ko-KR","ja-JP","es-419","es-ES",'
    r'"it-IT","hi-IN","pt-BR","id-ID"(?:,"zh-CN"|,"zh-TW"|,"zh-HK")*\]'
)
BASE_LANG_LIST = (
    '["en-US","de-DE","fr-FR","ko-KR","ja-JP","es-419","es-ES",'
    '"it-IT","hi-IN","pt-BR","id-ID"'
)

# system prompt 中文指令：写入 Claude 全局指令文件 ~/.claude/CLAUDE.md
# 用成对标记包裹，方便幂等写入和干净移除
SYSTEM_PROMPT_BEGIN = "<!-- claude-cowork-cn:begin -->"
SYSTEM_PROMPT_END = "<!-- claude-cowork-cn:end -->"
SYSTEM_PROMPT_TEXT = "请一律使用简体中文进行回答和代码注释。"
SYSTEM_PROMPT_BLOCK = (
    f"{SYSTEM_PROMPT_BEGIN}\n{SYSTEM_PROMPT_TEXT}\n{SYSTEM_PROMPT_END}"
)


class ClaudePatcher:
    """轻量版补丁主类"""

    def __init__(self, dry_run: bool = False):
        self.system = platform.system()
        self.dry_run = dry_run
        self.paths = self._resolve_paths()
        self.script_dir = Path(__file__).resolve().parent
        self.resources_dir = self.script_dir / "resources"

    # ---------- 路径解析 ----------

    def _resolve_paths(self) -> Dict[str, Optional[Path]]:
        """根据操作系统定位 Claude Desktop 的关键目录"""
        if self.system == "Darwin":  # macOS
            app = Path("/Applications/Claude.app")
            return {
                "app": app,
                "resources": app / "Contents/Resources",
                "i18n": app / "Contents/Resources/ion-dist/i18n",
                "assets": app / "Contents/Resources/ion-dist/assets/v1",
                "config": Path.home() / "Library/Application Support/Claude/config.json",
                "claude_md": Path.home() / ".claude/CLAUDE.md",
            }

        if self.system == "Windows":
            localappdata = os.environ.get("LOCALAPPDATA", "")
            appdata = os.environ.get("APPDATA", "")
            base = Path(localappdata) / "Programs" / "Claude" if localappdata else None
            return {
                "app": base,
                "resources": (base / "resources") if base else None,
                "i18n": (base / "resources/ion-dist/i18n") if base else None,
                "assets": (base / "resources/ion-dist/assets/v1") if base else None,
                "config": (Path(appdata) / "Claude/config.json") if appdata else None,
                "claude_md": Path.home() / ".claude/CLAUDE.md",
            }

        raise SystemExit(f"不支持的操作系统: {self.system}")

    # ---------- 前置检查 ----------

    def check_prerequisites(self) -> bool:
        print("检查安装环境...")

        resources = self.paths.get("resources")
        if not resources or not resources.exists():
            print(f"  ✗ 未找到 Claude Desktop 安装")
            print(f"    期望路径: {resources}")
            print(f"    请确认已安装官方 Claude Desktop")
            return False
        print(f"  ✓ 找到 Claude Desktop: {resources}")

        if not self.resources_dir.exists():
            print(f"  ✗ 未找到翻译资源目录: {self.resources_dir}")
            print(f"    请确保 resources/ 与本脚本在同一目录下")
            return False
        print(f"  ✓ 找到翻译资源: {self.resources_dir}")
        return True

    # ---------- 退出正在运行的 Claude ----------

    def _is_claude_running(self) -> bool:
        """检测 Claude 进程是否仍在运行"""
        try:
            if self.system == "Darwin":
                r = subprocess.run(["pgrep", "-x", "Claude"], capture_output=True, timeout=3)
                return r.returncode == 0
            if self.system == "Windows":
                r = subprocess.run(
                    ["tasklist", "/FI", "IMAGENAME eq Claude.exe", "/NH"],
                    capture_output=True, text=True, timeout=3,
                )
                return "Claude.exe" in (r.stdout or "")
        except Exception:
            pass
        return False

    def quit_claude(self) -> None:
        """安装前退出 Claude，避免它退出时用内存中的旧 locale 覆盖配置文件"""
        if self.dry_run:
            print("\n[预演] 跳过退出 Claude")
            return
        if not self._is_claude_running():
            print("\nClaude 未在运行，跳过退出。")
            return
        print("\n正在退出 Claude（避免覆盖语言设置）...")
        try:
            if self.system == "Darwin":
                subprocess.run(
                    ["osascript", "-e", 'tell application "Claude" to quit'],
                    capture_output=True, timeout=10,
                )
            elif self.system == "Windows":
                # 不带 /F 是优雅退出
                subprocess.run(
                    ["taskkill", "/IM", "Claude.exe"],
                    capture_output=True, timeout=10,
                )

            # 轮询等待最多 8 秒
            for _ in range(16):
                if not self._is_claude_running():
                    print("  ✓ Claude 已退出")
                    return
                time.sleep(0.5)

            # 超时强杀
            print("  ⚠ 优雅退出超时，强制结束 Claude 进程")
            if self.system == "Darwin":
                subprocess.run(["pkill", "-9", "Claude"], capture_output=True)
            elif self.system == "Windows":
                subprocess.run(["taskkill", "/IM", "Claude.exe", "/F"], capture_output=True)
            time.sleep(1)
        except Exception as e:
            print(f"  ⚠ 退出 Claude 时出现问题（可忽略，请确保手动退出）: {e}")

    def launch_claude(self) -> None:
        """安装完成后重新启动 Claude，使其加载新的中文配置"""
        if self.dry_run:
            print("\n[预演] 跳过启动 Claude")
            return
        print("\n正在重新启动 Claude...")
        try:
            if self.system == "Darwin":
                subprocess.run(["open", "-a", "Claude"], capture_output=True, timeout=10)
            elif self.system == "Windows":
                base = self.paths.get("app")
                exe_path = None
                if base and base.exists():
                    # 优先根目录
                    if (base / "Claude.exe").exists():
                        exe_path = base / "Claude.exe"
                    else:
                        # 递归找，取最近修改的
                        candidates = list(base.rglob("Claude.exe"))
                        if candidates:
                            exe_path = max(candidates, key=lambda p: p.stat().st_mtime)
                if exe_path:
                    subprocess.Popen([str(exe_path)])
                    print("  ✓ 已启动 Claude")
                else:
                    print("  ⚠ 未找到 Claude.exe，请手动启动 Claude")
                    return
            print("  ✓ 已启动 Claude")
        except Exception as e:
            print(f"  ⚠ 启动 Claude 时出现问题（请手动打开 Claude）: {e}")

    # ---------- 核心步骤 1：复制语言文件 ----------

    def copy_language_files(self, lang: str) -> bool:
        print(f"\n[1/3] 安装 {lang} 语言文件...")
        ok = True

        # 前端翻译：与目标机器的 en-US.json 按 key 合并，未翻译的 key 回退英文
        frontend_src = self.resources_dir / f"frontend-{lang}.json"
        frontend_dst = self.paths["i18n"] / f"{lang}.json"
        en_path = self.paths["i18n"] / "en-US.json"

        if not frontend_src.exists():
            print(f"  ✗ 缺少前端翻译文件: {frontend_src.name}")
            return False

        try:
            zh_data = json.loads(frontend_src.read_text(encoding="utf-8"))
            if en_path.exists():
                en_data = json.loads(en_path.read_text(encoding="utf-8"))
                merged = {k: zh_data.get(k, v) for k, v in en_data.items()}
                translated = sum(1 for k, v in en_data.items() if zh_data.get(k, v) != v)
                fallback = len(en_data) - translated
                content = json.dumps(merged, ensure_ascii=False, indent=2) + "\n"
                self._write(frontend_dst, content)
                print(f"  ✓ 前端翻译: {translated} 条已翻译, {fallback} 条回退英文")
            else:
                self._copy(frontend_src, frontend_dst)
                print(f"  ✓ 前端翻译: {frontend_dst.name}（未找到 en-US.json，直接复制）")
        except Exception as e:
            print(f"  ✗ 前端翻译失败: {e}")
            ok = False

        # 桌面外壳翻译
        desktop_src = self.resources_dir / f"desktop-{lang}.json"
        if desktop_src.exists():
            try:
                self._copy(desktop_src, self.paths["resources"] / f"{lang}.json")
                print(f"  ✓ 桌面外壳翻译: {lang}.json")
            except Exception as e:
                print(f"  ✗ 桌面外壳翻译失败: {e}")
                ok = False

        # Statsig（可选）
        statsig_dir = self.paths["i18n"] / "statsig"
        statsig_src = self.resources_dir / f"statsig-{lang}.json"
        if statsig_dir.exists() and statsig_src.exists():
            try:
                self._copy(statsig_src, statsig_dir / f"{lang}.json")
                print(f"  ✓ Statsig 翻译: {lang}.json")
            except Exception as e:
                print(f"  ⚠ Statsig 翻译跳过: {e}")

        # macOS 原生菜单 .strings（仅 macOS）
        if self.system == "Darwin":
            strings_src = self.resources_dir / f"Localizable-{lang}.strings"
            if not strings_src.exists():
                strings_src = self.resources_dir / "Localizable.strings"
            if strings_src.exists():
                for lproj in (f"{lang}.lproj", f"{lang.replace('-', '_')}.lproj"):
                    out_dir = self.paths["resources"] / lproj
                    try:
                        if not self.dry_run:
                            out_dir.mkdir(parents=True, exist_ok=True)
                        self._copy(strings_src, out_dir / "Localizable.strings")
                    except Exception as e:
                        print(f"  ⚠ 原生菜单 {lproj} 跳过: {e}")
                print(f"  ✓ macOS 原生菜单资源已安装")

        return ok

    # ---------- 核心步骤 2：修改语言白名单 ----------

    def patch_language_whitelist(self, lang: str) -> bool:
        print(f"\n[2/3] 修改语言白名单...")
        assets = self.paths.get("assets")
        if not assets or not assets.exists():
            print(f"  ✗ 未找到前端资源目录: {assets}")
            return False

        replacement = f'{BASE_LANG_LIST},"{lang}"]'
        pattern = re.compile(LANG_LIST_PATTERN)

        for js_file in sorted(assets.glob("*.js")):
            try:
                content = js_file.read_text(encoding="utf-8")
            except Exception:
                continue

            if not pattern.search(content):
                continue

            new_content = pattern.sub(replacement, content, count=1)
            if new_content == content:
                # 白名单已经是目标状态（已包含 lang）
                print(f"  ✓ 语言白名单已包含 {lang}: {js_file.name}")
                return True

            self._write(js_file, new_content)
            print(f"  ✓ 已修改语言白名单: {js_file.name}")
            return True

        print(f"  ✗ 未找到语言白名单位置（Claude 的 bundle 格式可能已变化）")
        return False

    # ---------- 核心步骤 3：写入用户配置 ----------

    def set_user_locale(self, lang: str) -> bool:
        print(f"\n[3/3] 设置用户语言配置...")
        config_path = self.paths.get("config")
        if not config_path:
            print(f"  ✗ 无法确定配置文件路径")
            return False

        try:
            config: Dict = {}
            if config_path.exists():
                try:
                    config = json.loads(config_path.read_text(encoding="utf-8"))
                except json.JSONDecodeError:
                    backup = config_path.with_suffix(".json.bak-invalid")
                    if not self.dry_run:
                        try:
                            shutil.copy2(config_path, backup)
                            self._chown_to_sudo_user(backup)
                        except Exception as be:
                            print(f"  ⚠ 备份损坏配置失败: {be}")
                    print(f"  ⚠ 现有配置不是有效 JSON，已备份到 {backup.name}，将重新创建")
            config["locale"] = lang
            content = json.dumps(config, ensure_ascii=False, indent=2) + "\n"

            if not self.dry_run:
                config_path.parent.mkdir(parents=True, exist_ok=True)
                config_path.write_text(content, encoding="utf-8")
                self._chown_to_sudo_user(config_path)
            print(f"  ✓ 已设置语言为 {lang}: {config_path}")
            return True
        except Exception as e:
            print(f"  ✗ 设置配置失败: {e}")
            return False

    # ---------- 可选步骤：注入 system prompt 中文指令 ----------

    def inject_system_prompt(self) -> bool:
        """往 ~/.claude/CLAUDE.md 注入中文指令（带标记，幂等）"""
        print(f"\n[可选] 注入 system prompt 中文指令...")
        md_path = self.paths.get("claude_md")
        if not md_path:
            print(f"  ✗ 无法确定 CLAUDE.md 路径")
            return False

        try:
            existing = ""
            if md_path.exists():
                existing = md_path.read_text(encoding="utf-8")

            # 已存在本工具写入的块 -> 替换为最新内容（幂等）
            if SYSTEM_PROMPT_BEGIN in existing and SYSTEM_PROMPT_END in existing:
                pattern = re.compile(
                    re.escape(SYSTEM_PROMPT_BEGIN) + r".*?" + re.escape(SYSTEM_PROMPT_END),
                    re.DOTALL,
                )
                new_content = pattern.sub(SYSTEM_PROMPT_BLOCK, existing, count=1)
                action = "已更新"
            else:
                # 追加到文件末尾，与已有内容隔一个空行
                sep = "" if existing == "" else ("\n" if existing.endswith("\n") else "\n\n")
                if existing and not existing.endswith("\n\n"):
                    sep = "\n\n" if not existing.endswith("\n") else "\n"
                new_content = existing + sep + SYSTEM_PROMPT_BLOCK + "\n"
                action = "已注入"

            if not self.dry_run:
                md_path.parent.mkdir(parents=True, exist_ok=True)
                md_path.write_text(new_content, encoding="utf-8")
                self._chown_to_sudo_user(md_path)
                self._chown_to_sudo_user(md_path.parent)
            print(f"  ✓ {action}中文指令: {md_path}")
            print(f"    内容: {SYSTEM_PROMPT_TEXT}")
            return True
        except Exception as e:
            print(f"  ✗ 注入失败: {e}")
            return False

    def remove_system_prompt(self) -> None:
        """从 ~/.claude/CLAUDE.md 移除本工具注入的中文指令块"""
        md_path = self.paths.get("claude_md")
        if not md_path or not md_path.exists():
            return
        try:
            existing = md_path.read_text(encoding="utf-8")
            if SYSTEM_PROMPT_BEGIN not in existing:
                return
            pattern = re.compile(
                r"\n*" + re.escape(SYSTEM_PROMPT_BEGIN) + r".*?" + re.escape(SYSTEM_PROMPT_END) + r"\n*",
                re.DOTALL,
            )
            new_content = pattern.sub("\n", existing).lstrip("\n")
            if not self.dry_run:
                md_path.write_text(new_content, encoding="utf-8")
            print(f"  ✓ 已移除 system prompt 中文指令: {md_path}")
        except Exception as e:
            print(f"  ⚠ 移除 system prompt 指令失败: {e}")

    # ---------- 恢复 ----------

    def restore(self, lang: str) -> bool:
        # 先退出 Claude，避免它退出时用内存中的旧 locale 覆盖配置文件
        self.quit_claude()

        print(f"\n正在恢复（移除 {lang} 中文文件并重置配置）...")
        removed = 0

        targets = [
            self.paths["i18n"] / f"{lang}.json",
            self.paths["resources"] / f"{lang}.json",
            self.paths["i18n"] / "statsig" / f"{lang}.json",
        ]
        if self.system == "Darwin":
            for lproj in (f"{lang}.lproj", f"{lang.replace('-', '_')}.lproj"):
                targets.append(self.paths["resources"] / lproj / "Localizable.strings")

        for t in targets:
            if t and t.exists():
                if not self.dry_run:
                    try:
                        t.unlink()
                    except Exception as e:
                        print(f"  ⚠ 删除失败 {t.name}: {e}")
                        continue
                print(f"  ✓ 已删除: {t}")
                removed += 1

        # 重置配置为 en-US
        config_path = self.paths.get("config")
        if config_path and config_path.exists():
            try:
                config = json.loads(config_path.read_text(encoding="utf-8"))
                config["locale"] = "en-US"
                if not self.dry_run:
                    config_path.write_text(
                        json.dumps(config, ensure_ascii=False, indent=2) + "\n",
                        encoding="utf-8",
                    )
                print(f"  ✓ 已将语言重置为 en-US")
            except Exception as e:
                print(f"  ⚠ 重置配置失败: {e}")

        # 移除 system prompt 中文指令
        self.remove_system_prompt()

        print(f"\n注意: 语言白名单的修改不会被还原（不影响功能），"
              f"如需彻底还原请重新安装 Claude Desktop。")
        print(f"已删除 {removed} 个文件。")

        # 重新启动 Claude，使其加载恢复后的配置
        self.launch_claude()

        return True

    # ---------- 文件操作辅助 ----------

    def _copy(self, src: Path, dst: Path) -> None:
        if self.dry_run:
            print(f"    [dry-run] 复制 {src.name} -> {dst}")
            return
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)

    def _write(self, path: Path, content: str) -> None:
        if self.dry_run:
            print(f"    [dry-run] 写入 {path}")
            return
        path.write_text(content, encoding="utf-8")

    def _chown_to_sudo_user(self, path: Path) -> None:
        """sudo 运行时把配置文件归属还给原用户，避免权限问题（仅 macOS/Linux）"""
        uid = os.environ.get("SUDO_UID")
        gid = os.environ.get("SUDO_GID")
        if uid and gid and hasattr(os, "chown"):
            try:
                os.chown(path, int(uid), int(gid))
            except Exception:
                pass

    # ---------- 安装编排 ----------

    def install(self, lang: str, with_system_prompt: bool = False) -> bool:
        print("\n" + "=" * 60)
        print(f"Claude Desktop 中文补丁 - 轻量版 v{VERSION}")
        print("=" * 60)
        print(f"目标语言: {LANG_NAME.get(lang, lang)}")
        print(f"安装路径: {self.paths['resources']}")
        if self.dry_run:
            print("模式: 预演（dry-run，不会实际修改任何文件）")
        print()

        # 先退出 Claude，否则它退出时会用内存里的旧 locale 覆盖我们写入的中文设置
        self.quit_claude()

        results = [
            self.copy_language_files(lang),
            self.patch_language_whitelist(lang),
            self.set_user_locale(lang),
        ]
        if with_system_prompt:
            results.append(self.inject_system_prompt())
        return all(results)


# ---------- 命令行交互 ----------

def print_banner() -> None:
    print()
    print("  Claude Desktop 中文补丁 · 轻量版")
    print(f"  v{VERSION}  |  简洁 · 快速 · 安全")
    print()


def select_language() -> str:
    print("请选择要安装的语言:\n")
    for key, lang in SUPPORTED_LANGUAGES.items():
        print(f"  [{key}] {lang['name']}")
    print()
    while True:
        choice = input("请输入选项 [默认 1]: ").strip() or "1"
        if choice in SUPPORTED_LANGUAGES:
            return SUPPORTED_LANGUAGES[choice]["code"]
        print("无效选项，请重新输入")


def warn_admin_if_needed() -> bool:
    """提示权限不足，返回是否继续"""
    system = platform.system()
    if system == "Darwin" and hasattr(os, "geteuid") and os.geteuid() != 0:
        print("⚠ 修改 /Applications/Claude.app 通常需要管理员权限")
        print(f"  建议使用: sudo python3 {sys.argv[0]}")
        return (input("是否仍要继续尝试? [y/N]: ").strip().lower() == "y")
    if system == "Windows":
        try:
            import ctypes
            if not ctypes.windll.shell32.IsUserAnAdmin():
                print("⚠ 此操作通常需要管理员权限")
                print("  建议右键以管理员身份运行")
                return (input("是否仍要继续尝试? [y/N]: ").strip().lower() == "y")
        except Exception:
            pass
    return True


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Claude Desktop 中文补丁 - 轻量版"
    )
    parser.add_argument("--lang", choices=["zh-CN", "zh-TW", "zh-HK"],
                        help="指定语言，跳过交互选择")
    parser.add_argument("--restore", action="store_true",
                        help="恢复：移除中文文件并重置语言为 en-US")
    parser.add_argument("--dry-run", action="store_true",
                        help="预演模式，不实际修改文件")
    parser.add_argument("--system-prompt", dest="system_prompt",
                        action="store_true", default=None,
                        help="注入中文 system prompt 指令（跳过交互询问）")
    parser.add_argument("--no-system-prompt", dest="system_prompt",
                        action="store_false",
                        help="不注入中文 system prompt 指令（跳过交互询问）")
    args = parser.parse_args()

    print_banner()

    try:
        patcher = ClaudePatcher(dry_run=args.dry_run)
    except SystemExit as e:
        print(f"✗ {e}")
        return 1

    if not patcher.check_prerequisites():
        print("\n前置条件不满足，已退出。")
        return 1

    if not args.dry_run and not warn_admin_if_needed():
        print("\n已取消。")
        return 1

    # 恢复模式
    if args.restore:
        lang = args.lang or select_language()
        patcher.restore(lang)
        print("\n恢复完成，请重启 Claude Desktop。")
        return 0

    # 安装模式
    lang = args.lang or select_language()

    # 决定是否注入 system prompt 中文指令
    if args.system_prompt is not None:
        with_sp = args.system_prompt
    else:
        print()
        ans = input(
            "是否让 Claude 默认用简体中文回答和写代码注释？\n"
            "（会写入 ~/.claude/CLAUDE.md，可随时用 --restore 移除）[Y/n]: "
        ).strip().lower()
        with_sp = ans in ("", "y", "yes")

    success = patcher.install(lang, with_system_prompt=with_sp)

    # 无论成功失败都重启 Claude（install 过程中已关闭它）
    patcher.launch_claude()

    print("\n" + "=" * 60)
    if success:
        print("✓ 安装完成!")
        print(f"\nClaude 已重新启动，界面应已切换为「{LANG_NAME.get(lang, lang)}」。")
        print("如果没有自动切换，点击左下角头像 -> Language 手动选择。")
        if with_sp:
            print("\n已注入 system prompt 中文指令，Claude 将默认用简体中文回答。")
        print("\n说明: 轻量版覆盖约 70% 界面。系统菜单、在线 claude.ai")
        print("      页面的部分内容仍为英文，属正常现象。")
    else:
        print("✗ 安装过程中出现错误，请检查上方日志。")
    print("=" * 60)
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
