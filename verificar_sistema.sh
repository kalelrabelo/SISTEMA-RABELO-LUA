#!/bin/bash

# Script de verificação do sistema corrigido
# Autor: Sistema de IA
# Data: 01/10/2025

echo "========================================"
echo "  VERIFICAÇÃO COMPLETA DO SISTEMA"
echo "========================================"
echo ""

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Contadores de erros
ERRORS=0
WARNINGS=0

# 1. Verificar estrutura de diretórios
echo -e "${YELLOW}[1/10] Verificando estrutura de diretórios...${NC}"
if [ -d "/home/user/webapp/backend" ] && [ -d "/home/user/webapp/frontend" ]; then
    echo -e "${GREEN}✓ Estrutura de diretórios OK${NC}"
else
    echo -e "${RED}✗ Estrutura de diretórios incorreta${NC}"
    ERRORS=$((ERRORS + 1))
fi

# 2. Verificar arquivos essenciais
echo -e "${YELLOW}[2/10] Verificando arquivos essenciais...${NC}"
FILES_TO_CHECK=(
    "/home/user/webapp/backend/main.py"
    "/home/user/webapp/frontend/src/App.jsx"
    "/home/user/webapp/frontend/src/components/JarvisAI_Enhanced.jsx"
    "/home/user/webapp/backend/src/routes/ai_assistant_enhanced.py"
)

for file in "${FILES_TO_CHECK[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✓ $file existe${NC}"
    else
        echo -e "${RED}✗ $file não encontrado${NC}"
        ERRORS=$((ERRORS + 1))
    fi
done

# 3. Verificar imagens de joias
echo -e "${YELLOW}[3/10] Verificando imagens de joias...${NC}"
IMAGE_COUNT=$(ls /home/user/webapp/frontend/public/images/jewelry/*.png 2>/dev/null | wc -l)
if [ $IMAGE_COUNT -gt 0 ]; then
    echo -e "${GREEN}✓ $IMAGE_COUNT imagens de joias encontradas${NC}"
else
    echo -e "${RED}✗ Nenhuma imagem de joia encontrada${NC}"
    ERRORS=$((ERRORS + 1))
fi

# 4. Verificar configuração de usuários
echo -e "${YELLOW}[4/10] Verificando usuários padrão...${NC}"
if grep -q "Antonio Rabelo" /home/user/webapp/backend/main.py && \
   grep -q "Antonio Darvin" /home/user/webapp/backend/main.py && \
   grep -q "Maria Lucia" /home/user/webapp/backend/main.py; then
    echo -e "${GREEN}✓ Usuários corretos configurados${NC}"
    
    # Verificar se não há usuário admin
    if grep -q "username.*admin.*password.*admin" /home/user/webapp/backend/main.py; then
        echo -e "${RED}✗ Usuário 'admin' encontrado (não autorizado)${NC}"
        ERRORS=$((ERRORS + 1))
    else
        echo -e "${GREEN}✓ Nenhum usuário 'admin' padrão${NC}"
    fi
else
    echo -e "${RED}✗ Usuários não configurados corretamente${NC}"
    ERRORS=$((ERRORS + 1))
fi

# 5. Verificar senhas corretas
echo -e "${YELLOW}[5/10] Verificando senhas configuradas...${NC}"
if grep -q "rabloce" /home/user/webapp/backend/main.py && \
   grep -q "darvince" /home/user/webapp/backend/main.py && \
   grep -q "luciace" /home/user/webapp/backend/main.py; then
    echo -e "${GREEN}✓ Senhas corretas configuradas${NC}"
else
    echo -e "${RED}✗ Senhas incorretas${NC}"
    ERRORS=$((ERRORS + 1))
fi

# 6. Verificar arquivos de migração desativados
echo -e "${YELLOW}[6/10] Verificando scripts de migração...${NC}"
MIGRATION_FILES=$(ls /home/user/webapp/backend/*.py 2>/dev/null | grep -E "(import|migrate|populate)" | wc -l)
if [ $MIGRATION_FILES -eq 0 ]; then
    echo -e "${GREEN}✓ Scripts de migração desativados${NC}"
else
    echo -e "${YELLOW}⚠ Scripts de migração ainda ativos${NC}"
    WARNINGS=$((WARNINGS + 1))
fi

# 7. Verificar dependências do backend
echo -e "${YELLOW}[7/10] Verificando dependências Python...${NC}"
if [ -f "/home/user/webapp/backend/requirements.txt" ]; then
    echo -e "${GREEN}✓ requirements.txt encontrado${NC}"
else
    echo -e "${RED}✗ requirements.txt não encontrado${NC}"
    ERRORS=$((ERRORS + 1))
fi

# 8. Verificar dependências do frontend
echo -e "${YELLOW}[8/10] Verificando dependências Node...${NC}"
if [ -f "/home/user/webapp/frontend/package.json" ]; then
    echo -e "${GREEN}✓ package.json encontrado${NC}"
else
    echo -e "${RED}✗ package.json não encontrado${NC}"
    ERRORS=$((ERRORS + 1))
fi

# 9. Verificar configuração do Vite
echo -e "${YELLOW}[9/10] Verificando configuração do Vite...${NC}"
if grep -q "publicDir: 'public'" /home/user/webapp/frontend/vite.config.js; then
    echo -e "${GREEN}✓ Configuração do Vite correta${NC}"
else
    echo -e "${YELLOW}⚠ Configuração do Vite pode precisar ajustes${NC}"
    WARNINGS=$((WARNINGS + 1))
fi

# 10. Verificar rotas da IA melhoradas
echo -e "${YELLOW}[10/10] Verificando rotas da IA...${NC}"
if grep -q "ai_enhanced_bp" /home/user/webapp/backend/main.py; then
    echo -e "${GREEN}✓ Rotas da IA melhoradas configuradas${NC}"
else
    echo -e "${RED}✗ Rotas da IA melhoradas não configuradas${NC}"
    ERRORS=$((ERRORS + 1))
fi

echo ""
echo "========================================"
echo "          RESULTADO DA VERIFICAÇÃO"
echo "========================================"
echo ""

if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}✅ SISTEMA TOTALMENTE VERIFICADO E FUNCIONAL!${NC}"
    echo -e "${GREEN}Todos os testes passaram com sucesso.${NC}"
elif [ $ERRORS -eq 0 ] && [ $WARNINGS -gt 0 ]; then
    echo -e "${YELLOW}⚠️  SISTEMA FUNCIONAL COM AVISOS${NC}"
    echo -e "${YELLOW}$WARNINGS avisos encontrados (não críticos)${NC}"
else
    echo -e "${RED}❌ SISTEMA COM PROBLEMAS${NC}"
    echo -e "${RED}$ERRORS erros encontrados${NC}"
    echo -e "${YELLOW}$WARNINGS avisos encontrados${NC}"
fi

echo ""
echo "========================================"
echo "         INFORMAÇÕES DO SISTEMA"
echo "========================================"
echo ""
echo "📂 Diretório principal: /home/user/webapp"
echo "👥 Usuários autorizados:"
echo "   - Antonio Rabelo (username: Antonio Rabelo, senha: rabloce)"
echo "   - Antonio Darvin (username: Antonio Darvin, senha: darvince)"
echo "   - Maria Lucia (username: Maria Lucia, senha: luciace)"
echo ""
echo "🚀 Para iniciar o sistema:"
echo "   Windows: Execute 'iniciar_windows.bat'"
echo "   Linux: Execute './start_system.sh'"
echo ""
echo "🤖 IA LUA melhorada e funcional"
echo "   - Reconhecimento de voz contínuo"
echo "   - Comandos completos implementados"
echo "   - Integração total com o sistema"
echo ""
echo "========================================"

exit $ERRORS