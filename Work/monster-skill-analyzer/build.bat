@echo off
chcp 65001 >nul
title Monster Skill Analyzer - 빌드

echo ========================================
echo   .exe 파일 빌드 시작
echo ========================================

:: PyInstaller 확인
python -c "import PyInstaller" >nul 2>&1
if %errorlevel% neq 0 (
    echo PyInstaller 설치 중...
    pip install pyinstaller
)

:: 빌드 실행
pyinstaller ^
    --onefile ^
    --noconsole ^
    --name "MonsterSkillAnalyzer" ^
    --add-data "src;src" ^
    --add-data "credentials;credentials" ^
    --hidden-import streamlit ^
    --hidden-import gspread ^
    --hidden-import plotly ^
    --hidden-import pandas ^
    launcher.py

echo.
echo ========================================
echo   빌드 완료: dist/MonsterSkillAnalyzer.exe
echo ========================================
pause
