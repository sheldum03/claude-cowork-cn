#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""翻译资源冒烟测试：验证 resources/ 下的 JSON 格式有效、关键文件齐全"""

import json
import sys
from pathlib import Path

RESOURCES = Path(__file__).resolve().parent.parent / "resources"
LANGS = ["zh-CN", "zh-TW", "zh-HK"]


def test_json_valid() -> bool:
    ok = True
    for f in sorted(RESOURCES.glob("*.json")):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            count = len(data) if isinstance(data, (dict, list)) else 0
            print(f"  ✓ {f.name}: {count} 条")
        except Exception as e:
            print(f"  ✗ {f.name}: JSON 解析失败 - {e}")
            ok = False
    return ok


def test_required_files() -> bool:
    ok = True
    for lang in LANGS:
        for prefix in ("frontend", "desktop", "statsig"):
            f = RESOURCES / f"{prefix}-{lang}.json"
            if not f.exists():
                print(f"  ✗ 缺少必需文件: {f.name}")
                ok = False
    # macOS 菜单
    if not (RESOURCES / "Localizable.strings").exists():
        print("  ✗ 缺少 Localizable.strings")
        ok = False
    if ok:
        print("  ✓ 所有必需文件齐全")
    return ok


def main() -> int:
    print("=== 测试 1: JSON 格式有效性 ===")
    r1 = test_json_valid()
    print("\n=== 测试 2: 必需文件齐全 ===")
    r2 = test_required_files()

    print()
    if r1 and r2:
        print("✓ 所有测试通过")
        return 0
    print("✗ 测试失败")
    return 1


if __name__ == "__main__":
    sys.exit(main())
