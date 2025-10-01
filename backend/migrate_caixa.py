#!/usr/bin/env python3
"""
Script para migrar dados de caixa do sistema antigo para o novo
"""

import sqlite3
import os
import sys
from datetime import datetime
import re

def parse_caixa_file():
    """Carrega dados de caixa do arquivo reformatado"""
    file_path = '/home/ubuntu/upload/caixa_reformatted.txt'
    
    if not os.path.exists(file_path):
        print(f"Arquivo {file_path} não encontrado!")
        return []
    
    transactions = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Dividir por registros
    records = content.split('Registro ')
    
    for record in records[1:]:  # Pular o primeiro que está vazio
        lines = record.strip().split('\n')
        transaction = {}
        
        for line in lines[1:]:  # Pular a linha do número do registro
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()
                
                # Converter valores
                if value == 'nan':
                    value = None
                elif key in ['ID', 'mes', 'ano', 'idc']:
                    try:
                        value = int(float(value)) if value else None
                    except:
                        value = None
                elif key in ['valor1', 'valor2', 'imposto', 'imposto2', 'imposto3', 'caixa']:
                    try:
                        value = float(value) if value else 0.0
                    except:
                        value = 0.0
                elif key == 'data':
                    try:
                        # Converter data do formato MM/DD/YY para YYYY-MM-DD
                        if value and value != 'nan':
                            # Formato: 08/04/05 00:00:00
                            date_part = value.split(' ')[0]
                            month, day, year = date_part.split('/')
                            # Assumir que anos 00-30 são 2000-2030, 31-99 são 1931-1999
                            year = int(year)
                            if year <= 30:
                                year += 2000
                            else:
                                year += 1900
                            value = f"{year:04d}-{int(month):02d}-{int(day):02d}"
                    except:
                        value = None
                
                transaction[key] = value
        
        if transaction.get('ID'):
            transactions.append(transaction)
    
    print(f"Carregados {len(transactions)} registros de caixa do arquivo")
    return transactions

def migrate_caixa_to_database():
    """Migra dados de caixa para o banco de dados"""
    
    # Conectar ao banco de dados
    db_path = 'data/joalheria.db'
    if not os.path.exists(db_path):
        print(f"Banco de dados {db_path} não encontrado!")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Carregar dados do arquivo
    transactions = parse_caixa_file()
    if not transactions:
        print("Nenhuma transação encontrada para migrar!")
        return False
    
    # Limpar tabela caixa_transaction existente
    cursor.execute("DELETE FROM caixa_transaction")
    print("Tabela caixa_transaction limpa")
    
    # Inserir transações
    migrated_count = 0
    for transaction in transactions:
        try:
            # Determinar tipo baseado no valor
            amount = transaction.get('valor1', 0.0)
            if amount > 0:
                trans_type = 'entrada'
            else:
                trans_type = 'saida'
                amount = abs(amount)  # Converter para positivo
            
            # Mapear idc para employee_id se existir
            employee_id = None
            idc = transaction.get('idc')
            if idc:
                # Verificar se o idc existe na tabela customers
                cursor.execute("SELECT id FROM customers WHERE id = ?", (idc,))
                if cursor.fetchone():
                    employee_id = idc
            
            # Criar descrição completa
            description = transaction.get('descricao', '')
            grupo1 = transaction.get('grupo1', '')
            grupo2 = transaction.get('grupo2', '')
            nome = transaction.get('nome', '')
            
            full_description = f"{description}"
            if grupo1:
                full_description += f" ({grupo1}"
                if grupo2:
                    full_description += f"/{grupo2}"
                full_description += ")"
            if nome:
                full_description += f" - {nome}"
            
            cursor.execute('''
                INSERT INTO caixa_transaction (
                    type, amount, date, description, employee_id
                ) VALUES (?, ?, ?, ?, ?)
            ''', (
                trans_type,
                amount,
                transaction.get('data'),
                full_description[:255],  # Limitar tamanho
                employee_id
            ))
            migrated_count += 1
        except Exception as e:
            print(f"Erro ao inserir transação ID {transaction.get('ID', 'UNKNOWN')}: {e}")
    
    # Confirmar transação
    conn.commit()
    
    # Verificar resultado
    cursor.execute("SELECT COUNT(*) FROM caixa_transaction")
    total_in_db = cursor.fetchone()[0]
    
    conn.close()
    
    print(f"Migração de caixa concluída!")
    print(f"Transações migradas: {migrated_count}")
    print(f"Total no banco: {total_in_db}")
    
    return True

if __name__ == "__main__":
    print("=== MIGRAÇÃO DE CAIXA ===")
    print("Migrando dados de caixa do arquivo reformatado para o banco de dados...")
    
    if migrate_caixa_to_database():
        print("✅ Migração de caixa concluída com sucesso!")
    else:
        print("❌ Falha na migração de caixa!")
        sys.exit(1)
