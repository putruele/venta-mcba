@echo off
setlocal enabledelayedexpansion

echo ========================================================
echo        ACTUALIZADOR DE DIARIO DE VENTAS - MCBA
echo ========================================================
echo.
echo Buscando Python en el sistema...

:: 1. Probar comando 'python' directo
python -c "import sys; print('OK')" >nul 2>&1
if !errorlevel! equ 0 (
    set PYTHON_EXE=python
    goto :found
)

:: 2. Probar comando 'py' directo
py -c "import sys; print('OK')" >nul 2>&1
if !errorlevel! equ 0 (
    set PYTHON_EXE=py
    goto :found
)

:: 3. Buscar usando 'where python' omitiendo WindowsApps (tienda de Windows)
for /f "tokens=*" %%i in ('where python 2^>nul') do (
    set "CURR_PATH=%%i"
    echo !CURR_PATH! | findstr /i "WindowsApps" >nul
    if errorlevel 1 (
        "!CURR_PATH!" -c "import sys; print('OK')" >nul 2>&1
        if !errorlevel! equ 0 (
            set PYTHON_EXE="!CURR_PATH!"
            goto :found
        )
    )
)

:: 4. Buscar en carpetas comunes de instalacion de Python (por usuario o del sistema)
set "COMMON_PATHS="
set "COMMON_PATHS=!COMMON_PATHS! "%USERPROFILE%\AppData\Local\Programs\Python""
set "COMMON_PATHS=!COMMON_PATHS! "C:\Program Files\Python*""
set "COMMON_PATHS=!COMMON_PATHS! "C:\Program Files (x86)\Python*""
set "COMMON_PATHS=!COMMON_PATHS! "C:\Python*""
set "COMMON_PATHS=!COMMON_PATHS! "%USERPROFILE%\miniconda3""
set "COMMON_PATHS=!COMMON_PATHS! "%USERPROFILE%\anaconda3""
set "COMMON_PATHS=!COMMON_PATHS! "%USERPROFILE%\AppData\Local\miniconda3""
set "COMMON_PATHS=!COMMON_PATHS! "%USERPROFILE%\AppData\Local\anaconda3""

for %%p in (!COMMON_PATHS!) do (
    :: Si la ruta tiene comodin o existe como carpeta principal
    for /d %%d in (%%p) do (
        if exist "%%d\python.exe" (
            "%%d\python.exe" -c "import sys; print('OK')" >nul 2>&1
            if !errorlevel! equ 0 (
                set PYTHON_EXE="%%d\python.exe"
                goto :found
            )
        )
        :: Revisar si esta en un subdirectorio (ej: Python311/python.exe)
        for /d %%s in ("%%d\Python*") do (
            if exist "%%s\python.exe" (
                "%%s\python.exe" -c "import sys; print('OK')" >nul 2>&1
                if !errorlevel! equ 0 (
                    set PYTHON_EXE="%%s\python.exe"
                    goto :found
                )
            )
        )
    )
)

:: 5. Buscar en el registro usando PowerShell como ultimo recurso
for /f "usebackq tokens=*" %%i in (`powershell -NoProfile -Command "Get-ItemProperty -Path 'HKCU:\Software\Python\PythonCore\*\*InstallPath' -Name '(default)' -ErrorAction SilentlyContinue | Select-Object -ExpandProperty '(default)'" 2^>nul`) do (
    if exist "%%i\python.exe" (
        "%%i\python.exe" -c "import sys; print('OK')" >nul 2>&1
        if !errorlevel! equ 0 (
            set PYTHON_EXE="%%i\python.exe"
            goto :found
        )
    )
)
for /f "usebackq tokens=*" %%i in (`powershell -NoProfile -Command "Get-ItemProperty -Path 'HKLM:\Software\Python\PythonCore\*\*InstallPath' -Name '(default)' -ErrorAction SilentlyContinue | Select-Object -ExpandProperty '(default)'" 2^>nul`) do (
    if exist "%%i\python.exe" (
        "%%i\python.exe" -c "import sys; print('OK')" >nul 2>&1
        if !errorlevel! equ 0 (
            set PYTHON_EXE="%%i\python.exe"
            goto :found
        )
    )
)

echo.
echo ========================================================
echo ERROR: No se pudo encontrar una instalacion de Python
echo ejecutable en su sistema.
echo.
echo Por favor:
echo 1. Instale Python desde: https://www.python.org/downloads/
echo 2. ASEGURESE de marcar la casilla:
echo    "Add Python to PATH" (Agregar Python al PATH)
echo    al inicio de la instalacion.
echo ========================================================
echo.
pause
exit /b 1

:found
echo Python detectado en: %PYTHON_EXE%
echo.

:: Verificar e instalar la librería de encriptación 'cryptography'
%PYTHON_EXE% -c "import cryptography" >nul 2>&1
if !errorlevel! neq 0 (
    echo Instalando libreria de encriptacion 'cryptography' necesaria...
    %PYTHON_EXE% -m pip install cryptography
    if !errorlevel! neq 0 (
        echo [ERROR] No se pudo instalar la libreria 'cryptography'. Revisa tu conexion a internet.
        pause
        exit /b 1
    )
)

echo Ejecutando script de actualizacion...
echo.

%PYTHON_EXE% "%~dp0update_data.py"

if !errorlevel! neq 0 (
    echo.
    echo [ERROR] Ocurrio un inconveniente al actualizar los datos.
    echo Revise los mensajes de error mas arriba.
    echo.
    pause
    exit /b 1
)

echo.
echo Actualizacion terminada con exito.
exit /b 0
