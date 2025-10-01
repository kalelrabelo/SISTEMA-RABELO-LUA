#!/bin/bash

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}============================================================${NC}"
echo -e "${GREEN}      SISTEMA JOALHERIA ANTONIO RABELO - INICIANDO${NC}"
echo -e "${GREEN}============================================================${NC}"
echo

# Função para verificar comando
check_command() {
    if command -v $1 &> /dev/null; then
        echo -e "${GREEN}✓${NC} $2 encontrado!"
        return 0
    else
        echo -e "${RED}✗${NC} $2 não está instalado."
        return 1
    fi
}

# Verificar dependências
echo -e "${YELLOW}[1/6] Verificando dependências...${NC}"
check_command python3 "Python 3" || exit 1
check_command node "Node.js" || exit 1
check_command npm "npm" || exit 1
check_command pm2 "PM2" || {
    echo -e "${YELLOW}Instalando PM2...${NC}"
    npm install -g pm2
}

# Configurar backend
echo -e "${YELLOW}[2/6] Configurando backend...${NC}"
cd backend

# Criar ambiente virtual se não existir
if [ ! -d "venv" ]; then
    echo "  Criando ambiente virtual Python..."
    python3 -m venv venv
fi

# Ativar ambiente virtual e instalar dependências
echo "  Ativando ambiente virtual..."
source venv/bin/activate

echo "  Instalando dependências do backend..."
pip install -r requirements.txt --quiet

# Criar pasta data se não existir
if [ ! -d "data" ]; then
    echo "  Criando pasta data..."
    mkdir -p data
fi

# Voltar para raiz
cd ..

# Configurar frontend
echo -e "${YELLOW}[3/6] Configurando frontend...${NC}"
cd frontend

if [ ! -d "node_modules" ]; then
    echo "  Instalando dependências do frontend..."
    echo "  Isso pode demorar alguns minutos na primeira vez..."
    npm install --legacy-peer-deps
else
    echo "  Dependências do frontend já instaladas!"
fi

# Voltar para raiz
cd ..

# Criar pasta de logs
echo -e "${YELLOW}[4/6] Criando pasta de logs...${NC}"
mkdir -p logs

# Parar processos existentes
echo -e "${YELLOW}[5/6] Limpando processos anteriores...${NC}"
pm2 delete all 2>/dev/null || true

# Iniciar serviços com PM2
echo -e "${YELLOW}[6/6] Iniciando serviços...${NC}"
pm2 start ecosystem.config.cjs

# Aguardar serviços iniciarem
echo "  Aguardando serviços iniciarem..."
sleep 5

# Verificar status
pm2 status

# Mensagem final
echo
echo -e "${GREEN}============================================================${NC}"
echo -e "${GREEN}      SISTEMA JOALHERIA ANTONIO RABELO - ATIVO${NC}"
echo -e "${GREEN}============================================================${NC}"
echo
echo -e "  ${YELLOW}BACKEND:${NC}  http://localhost:5000"
echo -e "  ${YELLOW}FRONTEND:${NC} http://localhost:5173"
echo
echo -e "${GREEN}============================================================${NC}"
echo -e "${GREEN}                   CREDENCIAIS DE ACESSO${NC}"
echo -e "${GREEN}============================================================${NC}"
echo
echo "  Antonio Rabelo (Proprietário):"
echo "    Usuário: Antonio Rabelo"
echo "    Senha:   rabeloce"
echo
echo "  Darvin Rabelo:"
echo "    Usuário: Darvin Rabelo"
echo "    Senha:   darvince"
echo
echo "  Maria Lúcia:"
echo "    Usuário: Maria Lucia"
echo "    Senha:   luciace"
echo
echo -e "${GREEN}============================================================${NC}"
echo
echo -e "${YELLOW}Comandos úteis:${NC}"
echo "  pm2 status        - Ver status dos serviços"
echo "  pm2 logs          - Ver logs em tempo real"
echo "  pm2 restart all   - Reiniciar todos os serviços"
echo "  pm2 stop all      - Parar todos os serviços"
echo "  pm2 delete all    - Remover todos os serviços"
echo
echo -e "${GREEN}Sistema pronto! Acesse http://localhost:5173${NC}"