@echo off
:: Script de instalación para Archivo Maestro - Organizador de Archivos
:: Descarga e instala todas las dependencias automáticamente

echo ********************************************
echo * INSTALADOR AUTOMÁTICO - ARCHIVO MAESTRO *
echo ********************************************
echo.

:: Verificar versión de Python
echo [Paso 1] Verificando instalación de Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python no está instalado o no está en el PATH.
    echo Descárgalo desde: https://www.python.org/downloads/
    echo Asegúrate de marcar "Add Python to PATH" durante la instalación.
    pause
    exit /b 1
)

echo Python está instalado correctamente.
echo.

:: Instalar dependencias
echo [Paso 2] Instalando dependencias requeridas...
echo --------------------------------------------
pip install --upgrade pip
pip install pillow pdfminer.six tkinterdnd2

if %errorlevel% neq 0 (
    echo ERROR: Falló la instalación de dependencias.
    echo Soluciones posibles:
    echo 1. Ejecuta CMD como Administrador
    echo 2. Verifica tu conexión a Internet
    pause
    exit /b 1
)

echo --------------------------------------------
echo Todas las dependencias se instalaron correctamente.
echo.

:: Ejecutar la aplicación
echo [Paso 3] Iniciando Archivo Maestro...
echo.
python archivo_maestro.py

if %errorlevel% neq 0 (
    echo ERROR: No se pudo iniciar la aplicación.
    echo Verifica que el archivo "archivo_maestro.py" esté en la misma carpeta.
    pause
    exit /b 1
)

pause