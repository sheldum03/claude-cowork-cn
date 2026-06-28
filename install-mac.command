#!/bin/bash
# Claude Desktop 中文补丁 - 轻量版 · macOS 双击入口
# 双击本文件即可运行；会自动请求管理员权限并启动安装脚本。

set -euo pipefail

DIR="$(cd "$(dirname "$0")" && pwd)"
PYTHON="/usr/bin/python3"
if [ ! -x "$PYTHON" ]; then
  PYTHON="$(command -v python3 || true)"
fi
if [ -z "$PYTHON" ]; then
  echo "✗ 未找到 python3，请先安装 Python 3。"
  echo "  按回车退出。"
  read -r _
  exit 1
fi

INSTALLER="$DIR/install.py"
if [ ! -f "$INSTALLER" ]; then
  echo "✗ 未找到 install.py，请确认本脚本与 install.py 在同一目录。"
  echo "  按回车退出。"
  read -r _
  exit 1
fi

echo "Claude Desktop 中文补丁 - 轻量版"
echo "目录: $DIR"
echo

echo "请选择操作："
echo "  [1] 安装中文补丁"
echo "  [2] 恢复 / 卸载补丁"
echo
read -rp "请输入选项 [1/2，默认 1]: " action_choice

case "${action_choice:-1}" in
  2) ACTION_ARGS="--restore" ;;
  *) ACTION_ARGS="" ;;
esac
echo

echo "请选择语言："
echo "  [1] 简体中文"
echo "  [2] 繁体中文（中国台湾）"
echo "  [3] 繁体中文（中国香港）"
echo
read -rp "请输入选项 [1/2/3，默认 1]: " lang_choice
case "${lang_choice:-1}" in
  2) LANG_CODE="zh-TW" ;;
  3) LANG_CODE="zh-HK" ;;
  *) LANG_CODE="zh-CN" ;;
esac
echo

echo "需要管理员权限来修改 /Applications/Claude.app。"
echo "请按提示输入这台 Mac 的登录密码。"
echo

if [ "$(id -u)" -ne 0 ]; then
  sudo "$PYTHON" "$INSTALLER" --lang "$LANG_CODE" ${ACTION_ARGS:+$ACTION_ARGS}
else
  "$PYTHON" "$INSTALLER" --lang "$LANG_CODE" ${ACTION_ARGS:+$ACTION_ARGS}
fi

echo
echo "完成。按回车退出。"
read -r _
