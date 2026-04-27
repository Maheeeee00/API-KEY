@echo off
setlocal EnableExtensions
cd /d "%~dp0"

REM ------------------------------------------------------------------
REM Portable Node.js (edit NODE_DIR if you move the folder)
REM Default matches: node-v24.15.0-win-x64
REM Leave NODE_DIR empty to use Node from PATH instead.
REM ------------------------------------------------------------------
set "NODE_DIR=C:\Users\laptop World\Downloads\node-v24.15.0-win-x64\node-v24.15.0-win-x64"

REM Optional override: create node_path.txt with ONE line = folder containing node.exe
if exist "%~dp0node_path.txt" (
  set /p NODE_DIR=<"%~dp0node_path.txt"
)

if defined NODE_DIR if exist "%NODE_DIR%\node.exe" (
  set "PATH=%NODE_DIR%;%PATH%"
  echo Using Node from: %NODE_DIR%
) else (
  where node >nul 2>nul
  if errorlevel 1 (
    echo Could not find node.exe
    echo Edit NODE_DIR in run_local.bat ^(line ~12^) to your portable folder, OR
    echo create node_path.txt with one line: full path to the folder that contains node.exe
    pause
    exit /b 1
  )
  echo Using Node from PATH
)

echo.
echo Starting local server for Sallybus...
echo After it starts, open: http://127.0.0.1:5500/sallybus%%20generator.html
echo Press Ctrl+C to stop.
echo.

if exist "%NODE_DIR%\npx.cmd" (
  "%NODE_DIR%\npx.cmd" --yes serve . -l 5500
) else (
  npx --yes serve . -l 5500
)
