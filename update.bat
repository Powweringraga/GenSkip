@echo off
title Build Executable - Genshin Skip Bot
echo ===================================================
echo   DANG DONG GOI UNG DUNG BANG PYINSTALLER...
echo ===================================================

:: 1. Chay PyInstaller dong goi code va thu muc templates
py -m PyInstaller --noconfirm --onedir --windowed --add-data "templates;templates" main.py

:: 2. Tự động copy thư mục templates ra ngoài folder main/ để đảm bảo luôn đọc được ảnh
if exist "dist\main" (
    echo.
    echo [+] Dang xao chep thư mục templates vào dist\main...
    xcopy /E /I /Y "templates" "dist\main\templates"
)


echo.
echo ===================================================
echo   HOAN TAT! File .exe va thu muc nam tai: dist\main\
echo ===================================================
@echo off
:: các câu lệnh update cũ của bạn giữ nguyên ở đây...

:: Bổ sung lệnh ép Windows cập nhật Date Modified sang thời gian hiện tại:
powershell -Command "(Get-Item 'main.py').LastWriteTime = Get-Date"
powershell -Command "(Get-Item 'vision.py').LastWriteTime = Get-Date"
powershell -Command "(Get-Item 'LLM_engine.py').LastWriteTime = Get-Date"

echo [OK] Da cap nhat thoi gian modified cho cac file!
pause