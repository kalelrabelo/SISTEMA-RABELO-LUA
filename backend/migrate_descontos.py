#!/usr/bin/env python3
"""
Script para migrar dados de descontos do sistema antigo para o novo
"""

import sqlite3
import os
import sys

def parse_descontos_file():
    """Carrega dados de descontos do arquivo reformatado"""
    file_path = '/home/ubuntu/upload/descontos_reformatted.txt'
    
    if not os.path.exists(file_path):
        print(f"Arquivo {file_path} não encontrado!")
        return []
    
    discounts = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Dividir por registros
    records = content.split('Registro ')
    
    for record in records[1:]:  # Pular o primeiro que está vazio
        lines = record.strip().split('\n')
        discount = {}
        
        for line in lines[1:]:  # Pular a linha do número do registro
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()
                
                # Converter valores
                if value == 'nan':
                    value = None
                elif key == 'iddesc':
                    try:
                        value = int(float(value)) if value else None
                    except:
                        value = None
                elif key in ['soma', 'desconto']:
                    try:
                        value = float(value) if value else 0.0
                    except:
                        value = 0.0
                
                discount[key] = value
        
        if discount.get('iddesc'):
            discounts.append(discount)
    
    print(f"Carregados {len(discounts)} registros de descontos do arquivo")
    return discounts

def migrate_descontos_to_database():
    """Migra dados de descontos para o banco de dados"""
    
    # Conectar ao banco de dados
    db_path = 'data/joalheria.db'
    if not os.path.exists(db_path):
        print(f"Banco de dados {db_path} não encontrado!")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Carregar dados do arquivo
    discounts = parse_descontos_file()
    if not discounts:
        print("Nenhum desconto encontrado para migrar!")
        return False
    
    # Limpar tabela discount_table existente
    cursor.execute("DELETE FROM discount_table")
    print("Tabela discount_table limpa")
    
    # Inserir descontos
    migrated_count = 0
    for discount in discounts:
        try:
            soma = discount.get('soma', 0.0)
            desconto_decimal = discount.get('desconto', 0.0)
            
            # Converter desconto decimal para percentual
            desconto_percentual = desconto_decimal * 100
            
            cursor.execute('''
                INSERT INTO discount_table (
                    soma, desconto
                ) VALUES (?, ?)
            ''', (
                soma,
                desconto_percentual  # Armazenar como percentual
            ))
            migrated_count += 1
        except Exception as e:
            print(f"Erro ao inserir desconto ID {discount.get('iddesc', 'UNKNOWN')}: {e}")
    
    # Confirmar transação
    conn.commit()
    
    # Verificar resultado
    cursor.execute("SELECT COUNT(*) FROM discount_table")
    total_in_db = cursor.fetchone()[0]
    
    conn.close()
    
    print(f"Migração de descontos concluída!")
    print(f"Descontos migrados: {migrated_count}")
    print(f"Total no banco: {total_in_db}")
    
    return True

if __name__ == "__main__":
    print("=== MIGRAÇÃO DE DESCONTOS ===")
    print("Migrando dados de descontos do arquivo reformatado para o banco de dados...")
    
    if migrate_descontos_to_database():
        print("✅ Migração de descontos concluída com sucesso!")
    else:
        print("❌ Falha na migração de descontos!")
        sys.exit(1)
