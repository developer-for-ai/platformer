@echo off
set VENV_DIR=game_env
set COMMAND=%1
if "%COMMAND%"=="" set COMMAND=play

if "%COMMAND%"=="clean" goto clean
if "%COMMAND%"=="setup" goto setup
if "%COMMAND%"=="run" goto run
if "%COMMAND%"=="play" goto play
if "%COMMAND%"=="package" goto package
if "%COMMAND%"=="test" goto test
if "%COMMAND%"=="help" goto help
echo Unknown command: %COMMAND%. Use 'help' for usage.
exit /b 1

:clean
echo Cleaning build artifacts...
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d" 2>nul
del /s /q *.pyc 2>nul
if exist build\ rd /s /q build 2>nul
if exist dist\ rd /s /q dist 2>nul
if "%2"=="all" if exist %VENV_DIR%\ rd /s /q %VENV_DIR% 2>nul
echo Cleaned
goto end

:setup
echo Setting up Crystal Quest...
if not exist %VENV_DIR%\ (
    echo Creating virtual environment...
    python -m venv %VENV_DIR%
)
call %VENV_DIR%\Scripts\activate.bat
echo Installing dependencies...
python -m pip install --upgrade pip -q
pip install -r requirements.txt -q
echo Setup complete
goto end

:play
if not exist %VENV_DIR%\ (
    echo Setting up Crystal Quest...
    call :setup
)
call %VENV_DIR%\Scripts\activate.bat
python main.py
goto end

:run
if not exist %VENV_DIR%\ (
    echo Setting up Crystal Quest...
    call :setup
)
call %VENV_DIR%\Scripts\activate.bat
echo Starting Crystal Quest...
python main.py
goto end

:package
if not exist %VENV_DIR%\ (
    echo Run setup first
    exit /b 1
)
echo Packaging Crystal Quest...
call %VENV_DIR%\Scripts\activate.bat
pip show pyinstaller >nul 2>&1 || (
    echo Installing PyInstaller...
    pip install pyinstaller -q
)
echo Creating executable...
pyinstaller --onefile --windowed --name crystal-quest --add-data "game;game" --clean main.py
echo Executable created in dist\
goto end

:test
if not exist %VENV_DIR%\ (
    echo Run setup first
    exit /b 1
)
echo Running tests...
call %VENV_DIR%\Scripts\activate.bat
python -c "import game, pygame; from game.constants import *; from game.player import Player; from game.entities import *; print('All tests passed')"
goto end

:help
echo Usage: %0 {setup^|clean^|run^|play^|package^|test^|help}
goto end

:end
