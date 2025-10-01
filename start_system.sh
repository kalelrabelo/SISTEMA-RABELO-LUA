#!/bin/bash

echo "============================================"
echo "     SISTEMA DE JOALHERIA ANTONIO RABELO   "
echo "============================================"
echo ""

# Limpar portas antigas
echo "[1/4] Limpando portas anteriores..."
fuser -k 5000/tcp 2>/dev/null || true
fuser -k 5173/tcp 2>/dev/null || true
echo "✅ Portas liberadas"
echo ""

# Iniciar backend
echo "[2/4] Iniciando Backend (porta 5000)..."
cd /home/user/webapp/backend
source venv/bin/activate
python main.py &
BACKEND_PID=$!
echo "✅ Backend iniciado com PID: $BACKEND_PID"
echo ""

# Aguardar backend iniciar
echo "Aguardando backend iniciar..."
sleep 3

# Iniciar frontend
echo "[3/4] Iniciando Frontend (porta 5173)..."
cd /home/user/webapp/frontend
npm run dev &
FRONTEND_PID=$!
echo "✅ Frontend iniciado com PID: $FRONTEND_PID"
echo ""

# Aguardar tudo iniciar
echo "[4/4] Aguardando serviços ficarem prontos..."
sleep 5

echo "============================================"
echo "     SISTEMA INICIADO COM SUCESSO!          "
echo ""
echo "     Frontend: http://localhost:5173        "
echo "     Backend:  http://localhost:5000        "
echo ""
echo "     CREDENCIAIS DE ACESSO:                 "
echo "     Usuário: Antonio Rabelo                "
echo "     Senha:   rabeloce                      "
echo ""
echo "     Pressione Ctrl+C para encerrar         "
echo "============================================"
echo ""

# Manter script rodando
wait $BACKEND_PID $FRONTEND_PID