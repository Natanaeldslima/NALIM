@echo off
title NALIM - Gestao Financeira Food Service
chcp 65001 > nul
cls

echo ==========================================================
echo        NALIM - GESTAO FINANCEIRA FOOD SERVICE
echo ==========================================================
echo.
echo [1/3] Localizando interpretador Python...

set "PYTHON_EXE="

rem 1. Testa python no PATH padrao
where python >nul 2>nul
if %errorlevel% equ 0 (
    set "PYTHON_EXE=python"
)

rem 2. Testa Python instalado em FreeCAD
if not defined PYTHON_EXE (
    if exist "C:\Program Files\FreeCAD 0.21\bin\python.exe" (
        set "PYTHON_EXE=C:\Program Files\FreeCAD 0.21\bin\python.exe"
    )
)

rem 3. Testa Python padrao em AppData Programs
if not defined PYTHON_EXE (
    for /d %%D in ("%LOCALAPPDATA%\Programs\Python\Python*") do (
        if exist "%%D\python.exe" set "PYTHON_EXE=%%D\python.exe"
    )
)

if not defined PYTHON_EXE (
    echo AVISO: Python nao encontrado no computador.
    echo Abrindo o NALIM diretamente no seu navegador web...
    start "" "%~dp0index.html"
    echo.
    echo Sistema aberto com sucesso no navegador!
    echo (Para sincronizar multiplos navegadores como Chrome e Edge ou celulares,
    echo instale o Python marcando a opcao 'Add to PATH').
    timeout /t 5 >nul
    exit /b
)

echo Python encontrado: "%PYTHON_EXE%"
echo.
echo [2/3] Verificando dependencias do sistema...
cd /d "%~dp0backend"
"%PYTHON_EXE%" -m pip install -r requirements.txt --quiet --user

echo.
echo [3/3] Iniciando o servidor NALIM na porta 8000...
echo.
echo ==========================================================
echo  O sistema abrira no seu navegador em instantes:
echo  - Aplicativo Web: http://localhost:8000
echo  - App do Garcom:  http://localhost:8000/garcom
echo  - Documentacao:   http://localhost:8000/docs
echo.
echo  Contas de Acesso:
echo  * Dono:     dono@nalim.com.br / dono123
echo  * Gerente:  gerente@nalim.com.br / gerente123
echo  * Operador: operador@nalim.com.br / operador123
echo.
echo  (Para parar o servidor, feche esta janela ou tecle CTRL+C)
echo ==========================================================
echo.

start http://localhost:8000
"%PYTHON_EXE%" -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
pause
