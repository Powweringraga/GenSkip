@echo off
echo Dang dong goi lai file .exe...
py -m PyInstaller --noconfirm --onedir --add-data "templates;templates" main.py
echo.
echo === DONG GOI HOAN TAT! File .exe nam trong dist/main/ ===
pause
