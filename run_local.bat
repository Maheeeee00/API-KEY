@echo off
cd /d "%~dp0"
echo Starting local server for Sallybus...
echo After it starts, open: http://127.0.0.1:5500/sallybus%%20generator.html
echo Press Ctrl+C to stop.
echo.
where node >nul 2>nul
if %ERRORLEVEL% neq 0 (
  echo Node.js not found. Install from https://nodejs.org/ then run this again.
  pause
  exit /b 1
)
npx --yes serve . -l 5500
