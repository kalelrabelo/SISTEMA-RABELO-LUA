#!/usr/bin/env python3
"""
Script para migrar dados de custos do sistema antigo para o novo
"""

import sqlite3
import os
import sys
from datetime import datetime

def parse_custos_file():
    """Carrega dados de custos do arquivo reformatado"""
    file_path = '/home/ubuntu/upload/custos_reformatted.txt'
    
    if not os.path.exists(file_path):
        print(f"Arquivo {file_path} não encontrado!")
        return []
    
    costs = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Dividir por registros
    records = content.split('Registro ')
    
    for record in records[1:]:  # Pular o primeiro que está vazio
        lines = record.strip().split('\n')
        cost = {}
        
        for line in lines[1:]:  # Pular a linha do número do registro
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()
                
                # Converter valores
                if value == 'nan':
                    value = None
                elif key in ['idcalc', 'ano', 'mes', 'empregados', 'HorasPorSemana', 'RSporHora']:
                    try:
                        value = int(float(value)) if value else None
                    except:
                        value = None
                
                cost[key] = value
        
        if cost.get('idcalc'):
            costs.append(cost)
    
    print(f"Carregados {len(costs)} registros de custos do arquivo")
    return costs

def migrate_custos_to_database():
    """Migra dados de custos para o banco de dados"""
    
    # Conectar ao banco de dados
    db_path = 'data/joalheria.db'
    if not os.path.exists(db_path):
        print(f"Banco de dados {db_path} não encontrado!")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Carregar dados do arquivo
    costs = parse_custos_file()
    if not costs:
        print("Nenhum custo encontrado para migrar!")
        return False
    
    # Limpar tabela cost existente
    cursor.execute("DELETE FROM cost")
    print("Tabela cost limpa")
    
    # Inserir custos
    migrated_count = 0
    for cost in costs:
        try:
            # Calcular custo total mensal
            empregados = cost.get('empregados', 0) or 0
            horas_semana = cost.get('HorasPorSemana', 0) or 0
            rs_por_hora = cost.get('RSporHora', 0) or 0
            
            # Calcular custo mensal (4.33 semanas por mês em média)
            custo_mensal = empregados * horas_semana * rs_por_hora * 4.33
            
            # Criar data do primeiro dia do mês
            ano = cost.get('ano', 2024)
            mes = cost.get('mes', 1)
            data = f"{ano}-{mes:02d}-01"
            
            # Criar descrição
            description = f"Custo de mão de obra - {empregados} empregados, {horas_semana}h/semana, R${rs_por_hora}/hora"
            
            cursor.execute('''
                INSERT INTO cost (
                    category, description, amount, date, notes
                ) VALUES (?, ?, ?, ?, ?)
            ''', (
                'mao_de_obra',
                description,
                custo_mensal,
                data,
                f"Dados migrados do sistema antigo - ID original: {cost.get('idcalc')}"
            ))
            migrated_count += 1
        except Exception as e:
            print(f"Erro ao inserir custo ID {cost.get('idcalc', 'UNKNOWN')}: {e}")
    
    # Confirmar transação
    conn.commit()
    
    # Verificar resultado
    cursor.execute("SELECT COUNT(*) FROM cost")
    total_in_db = cursor.fetchone()[0]
    
    conn.close()
    
    print(f"Migração de custos concluída!")
    print(f"Custos migrados: {migrated_count}")
    print(f"Total no banco: {total_in_db}")
    
    return True

if __name__ == "__main__":
    print("=== MIGRAÇÃO DE CUSTOS ===")
    print("Migrando dados de custos do arquivo reformatado para o banco de dados...")
    
    if migrate_custos_to_database():
        print("✅ Migração de custos concluída com sucesso!")
    else:
        print("❌ Falha na migração de custos!")
        sys.exit(1)
