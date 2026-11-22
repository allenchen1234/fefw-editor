@echo off
setlocal
cd /d "%~dp0"

rem Use a project-local environment so the build does not alter system Python.
if not exist ".venv\Scripts\python.exe" (
    where py >nul 2>nul
    if errorlevel 1 (
        python -m venv .venv
    ) else (
        py -3 -m venv .venv
    )
    if errorlevel 1 goto :failed
)

set "PYTHON=%CD%\.venv\Scripts\python.exe"
"%PYTHON%" -m pip install -r requirements.txt pyinstaller==6.11.1
if errorlevel 1 goto :failed

"%PYTHON%" -m PyInstaller --clean --noconfirm --onefile --windowed --name "FEFW Save Editor" ^
    --add-data "unit_ids.json;." --add-data "item_ids.json;." --add-data "job_ids.json;." ^
    --add-data "supports.json;." --add-data "support_points.json;." ^
    --add-data "flag_names.json;." --add-data "skill_ids.json;." --add-data "map_spots.json;." ^
    --add-data "tutorial_names.json;." --add-data "facility_names.json;." --add-data "deed_names.json;." ^
    --add-data "boon_catalog.json;." --add-data "fast_travel_names.json;." --add-data "unit_catalog.json;." ^
    --add-data "item_stack.json;." editor.py
if errorlevel 1 goto :failed

echo.
echo Build complete: "%CD%\dist\FEFW Save Editor.exe"
exit /b 0

:failed
echo.
echo Build failed. Check the error messages above.
exit /b 1
