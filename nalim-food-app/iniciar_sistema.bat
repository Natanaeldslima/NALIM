@echo off
title NALIM - Gestao Financeira Food Service
chcp 65001 > nul
cls

echo ==========================================================
echo        NALIM - GESTAO FINANCEIRA FOOD SERVICE
echo ==========================================================
echo.
echo [1/3] Verificando instalacao do Python...
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo ERRO: Python nao encontrado!
    echo Por favor, instale o Python em https://www.python.org/
    echo Certifique-se de marcar a opcao "Add Python to PATH" durante a instalacao.
    pause
    exit /b
)

echo [2/3] Verificando dependencias do sistema...
cd /d "%~dp0backend"
pip install -r requirements.txt --quiet

echo [3/3] Iniciando o servidor NALIM na porta 8000...
echo.
echo ==========================================================
echo  O sistema abrira no seu navegador em instantes:
echo  - Aplicativo Web: http://localhost:8000
echo  - Documentacao da API: http://localhost:8000/docs
echo.
echo  Contas de Acesso:
echo  * Dono:     dono@nalim.com.br / dono123
echo  * Gerente:  gerente@nalim.com.br / gerente123
echo  * Operador: operador@nalim.com.br / operador123
echo.
echo  (Para parar o sistema, feche esta janela ou aperte CTRL+C)
echo ==========================================================
echo.

start http://localhost:8000
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
pause
