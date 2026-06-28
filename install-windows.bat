@echo off
setlocal EnableExtensions
chcp 65001 >nul 2>&1

REM Claude Desktop 中文补丁 - 轻量版 · Windows 入口
REM 右键以管理员身份运行本文件。

set "DIR=%~dp0"
set "INSTALLER=%DIR%install.py"

if not exist "%INSTALLER%" (
    echo [X] 未找到 install.py，请确认本脚本与 install.py 在同一目录。
    pause
    exit /b 1
)

REM 检查管理员权限
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [!] 需要管理员权限。
    echo     请右键本文件，选择"以管理员身份运行"。
    pause
    exit /b 1
)

REM 查找 python
where python >nul 2>&1
if %errorLevel% neq 0 (
    echo [X] 未找到 python，请先安装 Python 3 并加入 PATH。
    pause
    exit /b 1
)

echo Claude Desktop 中文补丁 - 轻量版
echo 目录: %DIR%
echo.

echo 请选择操作:
echo   [1] 安装中文补丁
echo   [2] 恢复 / 卸载补丁
echo.
set /p ACTION_CHOICE="请输入选项 [1/2，默认 1]: "
if "%ACTION_CHOICE%"=="2" (
    set "ACTION_ARGS=--restore"
) else (
    set "ACTION_ARGS="
)
echo.

echo 请选择语言:
echo   [1] 简体中文
echo   [2] 繁体中文（中国台湾）
echo   [3] 繁体中文（中国香港）
echo.
set /p LANG_CHOICE="请输入选项 [1/2/3，默认 1]: "
if "%LANG_CHOICE%"=="2" (
    set "LANG_CODE=zh-TW"
) else if "%LANG_CHOICE%"=="3" (
    set "LANG_CODE=zh-HK"
) else (
    set "LANG_CODE=zh-CN"
)
echo.

python "%INSTALLER%" --lang %LANG_CODE% %ACTION_ARGS%

echo.
echo 完成。
pause
