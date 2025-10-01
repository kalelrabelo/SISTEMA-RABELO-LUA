#!/usr/bin/env python3
"""
Script para migrar pedras do arquivo reformatado para o banco de dados
"""

import sqlite3
import os
import sys
import re
from datetime import datetime

def parse_stones_file():
    """Carrega pedras do arquivo reformatado"""
    file_path = '/home/ubuntu/upload/pedras_reformatted.txt'
    
    if not os.path.exists(file_path):
        print(f"Arquivo {file_path} não encontrado!")
        return []
    
    stones = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Dividir por registros
    records = content.split('Registro ')
    
    for record in records[1:]:  # Pular o primeiro que está vazio
        lines = record.strip().split('\n')
        stone = {}
        
        for line in lines[1:]:  # Pular a linha do número do registro
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()
                
                # Converter valores
                if value == 'nan':
                    value = None
                elif key in ['idpe', 'nasjoias']:
                    try:
                        value = int(float(value)) if value else None
                    except:
                        value = None
                elif key in ['comprimento_pedra', 'largura_pedra', 'altura_pedra', 'peso_pedra', 'preco_pedra', 'qmin']:
                    try:
                        value = float(value) if value else 0.0
                    except:
                        value = 0.0
                
                stone[key] = value
        
        if stone.get('idpe'):
            stones.append(stone)
    
    print(f"Carregados {len(stones)} pedras do arquivo")
    return stones

def migrate_stones_to_database():
    """Migra pedras para o banco de dados"""
    
    # Conectar ao banco de dados
    db_path = 'data/joalheria.db'
    if not os.path.exists(db_path):
        print(f"Banco de dados {db_path} não encontrado!")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Verificar se a tabela stones existe
    cursor.execute("PRAGMA table_info(stones)")
    columns = cursor.fetchall()
    
    if not columns:
        print("Tabela stones não existe! Criando...")
        cursor.execute('''
            CREATE TABLE stones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                type TEXT,
                color TEXT,
                price_per_carat REAL DEFAULT 0.0,
                stock_quantity REAL DEFAULT 0.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
    
    # Carregar pedras do arquivo
    stones = parse_stones_file()
    if not stones:
        print("Nenhuma pedra encontrada para migrar!")
        return False
    
    # Limpar tabela stones existente
    cursor.execute("DELETE FROM stones")
    print("Tabela stones limpa")
    
    # Inserir pedras
    migrated_count = 0
    for stone in stones:
        try:
            # Criar nome combinando material e tipo
            name = f"{stone.get('material_pedra', '')} {stone.get('tipo_pedra', '')}".strip()
            if not name:
                name = f"Pedra {stone.get('cor_pedra', 'sem cor')}"
            
            cursor.execute('''
                INSERT INTO stones (
                    name, type, color, price_per_carat, stock_quantity
                ) VALUES (?, ?, ?, ?, ?)
            ''', (
                name,
                stone.get('tipo_pedra', ''),
                stone.get('cor_pedra', ''),
                stone.get('preco_pedra', 0.0),
                stone.get('qmin', 1.0)
            ))
            migrated_count += 1
        except Exception as e:
            print(f"Erro ao inserir pedra {stone.get('material_pedra', 'UNKNOWN')}: {e}")
    
    # Confirmar transação
    conn.commit()
    
    # Verificar resultado
    cursor.execute("SELECT COUNT(*) FROM stones")
    total_in_db = cursor.fetchone()[0]
    
    conn.close()
    
    print(f"Migração de pedras concluída!")
    print(f"Pedras migradas: {migrated_count}")
    print(f"Total no banco: {total_in_db}")
    
    return True

if __name__ == "__main__":
    print("=== MIGRAÇÃO DE PEDRAS ===")
    print("Migrando pedras do arquivo reformatado para o banco de dados...")
    
    if migrate_stones_to_database():
        print("✅ Migração de pedras concluída com sucesso!")
    else:
        print("❌ Falha na migração de pedras!")
        sys.exit(1)
