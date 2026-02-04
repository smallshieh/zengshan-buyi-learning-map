@echo off
chcp 65001 > nul
echo ========================================================
echo       增刪卜易 - Obsidian 學習庫發佈工具
echo ========================================================
echo.

echo [1/2] 正在執行連結健康檢查...
python scripts/verify_links.py --all
if %errorlevel% neq 0 (
    echo.
    echo ⚠️  警告：連結檢查發現問題或執行失敗。
    echo 請檢查上方的錯誤訊息。
    echo.
    pause
)

echo.
echo [2/2] 正在建立發佈包 (.zip)...
python scripts/build_release.py

if %errorlevel% neq 0 (
    echo.
    echo ❌ 發佈包建立失敗！
) else (
    echo.
    echo ✅ 發佈流程完成！
    echo 請檢查 releases 資料夾。
)

echo.
pause
