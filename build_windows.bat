@echo off
REM PDFIndsigt — Build Windows .exe
REM Kør dette script på en Windows-maskine med Python installeret.
REM
REM 1. Installer Python fra python.org (husk at sætte flueben ved "Add to PATH")
REM 2. Åbn Command Prompt i denne mappe
REM 3. Kør: build_windows.bat

echo === PDFIndsigt Windows Build ===

echo Installing dependencies...
pip install pikepdf pypdf ttkbootstrap Pillow pyinstaller

echo Building .exe...
pyinstaller ^
  --name "PDFIndsigt" ^
  --windowed ^
  --onefile ^
  --noconfirm ^
  --clean ^
  --add-data "i18n;i18n" ^
  --add-data "assets;assets" ^
  --hidden-import pikepdf ^
  --hidden-import "pikepdf._core" ^
  --hidden-import pypdf ^
  --hidden-import ttkbootstrap ^
  --hidden-import "ttkbootstrap.themes" ^
  --hidden-import "ttkbootstrap.themes.standard" ^
  --hidden-import PIL ^
  --exclude-module matplotlib ^
  --exclude-module numpy ^
  --exclude-module scipy ^
  --exclude-module pandas ^
  main.py

echo.
echo Build complete!
echo .exe fil: dist\PDFIndsigt.exe
pause
