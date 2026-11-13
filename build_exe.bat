@echo off
pip install pyinstaller
pyinstaller --onefile --windowed --name LocalCode app.py
echo Copy the "problems" folder next to dist\LocalCode.exe
