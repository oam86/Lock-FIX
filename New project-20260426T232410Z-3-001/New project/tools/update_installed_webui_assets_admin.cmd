@echo off
setlocal
set "SCRIPT_DIR=%~dp0"
set "SOURCE_ROOT=%SCRIPT_DIR%.."
powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "Start-Process powershell.exe -Verb RunAs -ArgumentList @('-NoProfile','-ExecutionPolicy','Bypass','-File','%SCRIPT_DIR%update_installed_webui_assets.ps1','-SourceRoot','%SOURCE_ROOT%')"
endlocal
