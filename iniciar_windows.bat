@echo off
setlocal EnableDelayedExpansion

echo ============================================================
echo      SISTEMA JOALHERIA ANTONIO RABELO - INICIANDO
echo ============================================================
echo.

REM Verificar se Python está instalado
echo [1/5] Verificando Python...
python --version >nul 2>&1
if !errorlevel! neq 0 (
    echo [ERRO] Python nao esta instalado ou nao esta no PATH.
    echo Por favor, instale Python 3.8+ de https://python.org
    echo.
    pause
    exit /b 1
)
echo       Python encontrado!

REM Verificar se Node.js está instalado
echo [2/5] Verificando Node.js...
node --version >nul 2>&1
if !errorlevel! neq 0 (
    echo [ERRO] Node.js nao esta instalado ou nao esta no PATH.
    echo Por favor, instale Node.js 16+ de https://nodejs.org
    echo.
    pause
    exit /b 1
)
echo       Node.js encontrado!

REM Instalar dependências do backend
echo [3/5] Configurando backend...
cd backend
if not exist "venv" (
    echo       Criando ambiente virtual Python...
    python -m venv venv
)

echo       Ativando ambiente virtual...
call venv\Scripts\activate.bat

echo       Instalando dependencias do backend...
pip install -r requirements.txt --quiet
if !errorlevel! neq 0 (
    echo [ERRO] Falha ao instalar dependencias do backend
    pause
    exit /b 1
)

REM Criar pasta data se não existir
if not exist "data" (
    echo       Criando pasta data...
    mkdir data
)

REM Iniciar backend em nova janela
echo [4/5] Iniciando servidor backend...
start "Backend - Joalheria Antonio Rabelo" cmd /k "venv\Scripts\activate.bat && python main.py"

REM Aguardar backend inicializar
echo       Aguardando backend inicializar...
timeout /t 5 /nobreak >nul

REM Instalar dependências do frontend
echo [5/5] Configurando frontend...
cd ..\frontend

if not exist "node_modules" (
    echo       Instalando dependencias do frontend...
    echo       Isso pode demorar alguns minutos na primeira vez...
    call npm install --legacy-peer-deps
    if !errorlevel! neq 0 (
        echo [ERRO] Falha ao instalar dependencias do frontend
        echo Tente executar manualmente: npm install --legacy-peer-deps
        pause
        exit /b 1
    )
) else (
    echo       Dependencias do frontend ja instaladas!
)

REM Iniciar frontend em nova janela
echo       Iniciando servidor frontend...
start "Frontend - Joalheria Antonio Rabelo" cmd /k "npm run dev"

REM Aguardar frontend inicializar
timeout /t 5 /nobreak >nul

REM Mensagem final
cls
echo ============================================================
echo      SISTEMA JOALHERIA ANTONIO RABELO - ATIVO
echo ============================================================
echo.
echo  BACKEND:  http://localhost:5000
echo  FRONTEND: http://localhost:5173
echo.
echo ============================================================
echo                    CREDENCIAIS DE ACESSO
echo ============================================================
echo.
echo  Usuarios do Sistema:
echo    Antonio Rabelo - Senha: rabeloce
echo    Antonio Darvin - Senha: darvince
echo    Maria Lucia   - Senha: luciace
echo.
echo ============================================================
echo.
echo  O sistema sera aberto automaticamente em 5 segundos...
echo.
echo  Pressione Ctrl+C nas janelas para parar os servidores
echo  Pressione qualquer tecla nesta janela para encerrar
echo ============================================================

REM Aguardar 5 segundos e abrir o navegador
timeout /t 5 /nobreak >nul
start "" "http://localhost:5173"

pause >nul

REM Finalizar processos ao fechar
echo.
echo Encerrando servidores...
taskkill /FI "WindowTitle eq Backend - Joalheria Antonio Rabelo*" /T /F >nul 2>&1
taskkill /FI "WindowTitle eq Frontend - Joalheria Antonio Rabelo*" /T /F >nul 2>&1
echo Sistema encerrado com sucesso!
timeout /t 2 /nobreak >nul
exit