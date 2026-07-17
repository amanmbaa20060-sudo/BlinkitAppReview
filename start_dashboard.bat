@echo off
setlocal
cd /d "%~dp0"
echo Starting Category Expansion Insights dashboard...
python phase5\scripts\run_dashboard.py
if errorlevel 1 (
  echo.
  echo Dashboard failed to start. Ensure Python is installed and run:
  echo   python phase5\scripts\run_dashboard.py
  pause
)
