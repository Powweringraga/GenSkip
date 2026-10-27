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
pause