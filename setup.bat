@echo off
chcp 65001 >nul
title A2M P2P - Build Script
echo ========================================
echo   A2M P2P Convertor - Build Script
echo ========================================
echo.

echo 📦 Installing requirements...
pip install setuptools==65.5.0 wheel==0.38.4
pip install -r requirements.txt
echo.

echo 🔨 Building executable...
pyinstaller --onefile --windowed --icon=p2p_icon.ico --name="A2M_P2P_Convertor" --add-data="p2p_icon.ico;." --add-data="p2p_logo.png;." --uac-admin --version-file=version.txt --hidden-import=jaraco --hidden-import=jaraco.functools main.py
echo.

echo ✅ Build complete! Check the 'dist' folder.
echo.
pause