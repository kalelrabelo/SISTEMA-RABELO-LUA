#!/usr/bin/env python3
"""
Script para migrar dados de estoque do sistema antigo para o novo
"""

import sqlite3
import os
import sys
from datetime import datetime

def parse_estoque_file():
    """Carrega dados de estoque do arquivo reformatado"""
    file_path = '/home/ubuntu/upload/stoque_reformatted.txt'
    
    if not os.path.exists(file_path):
        print(f"Arquivo {file_path} não encontrado!")
        return []
    
    stock_movements = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Dividir por registros
    records = content.split('Registro ')
    
    for record in records[1:]:  # Pular o primeiro que está vazio
        lines = record.strip().split('\n')
        movement = {}
        
        for line in lines[1:]:  # Pular a linha do número do registro
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()
                
                # Converter valores
                if value == 'nan':
                    value = None
                elif key in ['ids', 'id', 'quantidade', 'pessoastoque', 'pessoafora', 'empresa']:
                    try:
                        value = int(float(value)) if value else None
                    except:
                        value = None
                elif key == 'idj':
                    try:
                        value = int(float(value)) if value else None
                    except:
                        value = None
                elif key == 'data':
                    try:
                        # Converter data do formato MM/DD/YY HH:MM:SS para YYYY-MM-DD HH:MM:SS
                        if value and value != 'nan':
                            # Formato: 01/23/25 08:02:24
                            date_part, time_part = value.split(' ')
                            month, day, year = date_part.split('/')
                            # Assumir que anos 00-30 são 2000-2030, 31-99 são 1931-1999
                            year = int(year)
                            if year <= 30:
                                year += 2000
                            else:
                                year += 1900
                            value = f"{year:04d}-{int(month):02d}-{int(day):02d} {time_part}"
                    except:
                        value = None
                
                movement[key] = value
        
        if movement.get('ids'):
            stock_movements.append(movement)
    
    print(f"Carregados {len(stock_movements)} registros de estoque do arquivo")
    return stock_movements

def migrate_estoque_to_database():
    """Migra dados de estoque para o banco de dados"""
    
    # Conectar ao banco de dados
    db_path = 'data/joalheria.db'
    if not os.path.exists(db_path):
        print(f"Banco de dados {db_path} não encontrado!")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Verificar se a tabela inventory existe
    cursor.execute("PRAGMA table_info(inventory)")
    columns = cursor.fetchall()
    
    if not columns:
        print("Tabela inventory não existe! Criando...")
        cursor.execute('''
            CREATE TABLE inventory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_type TEXT NOT NULL,
                item_id INTEGER,
                quantity INTEGER DEFAULT 0,
                movement_type TEXT,
                date DATETIME,
                notes TEXT,
                employee_id INTEGER,
                location TEXT DEFAULT 'stoque',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
    
    # Carregar dados do arquivo
    movements = parse_estoque_file()
    if not movements:
        print("Nenhuma movimentação de estoque encontrada para migrar!")
        return False
    
    # Limpar tabela inventory existente
    cursor.execute("DELETE FROM inventory")
    print("Tabela inventory limpa")
    
    # Inserir movimentações de estoque
    migrated_count = 0
    for movement in movements:
        try:
            # Determinar tipo de item baseado no campo 'tipo'
            tipo = movement.get('tipo', '')
            item_type = 'unknown'
            item_id = movement.get('id')
            
            if tipo == 'j':  # Joia
                item_type = 'joia'
                item_id = movement.get('idj') or movement.get('id')
            elif tipo == 'm':  # Material
                item_type = 'material'
            elif tipo == 'p':  # Pedra
                item_type = 'pedra'
            
            # Determinar tipo de movimentação
            lugar = movement.get('lugar', '')
            if lugar == 'stoque':
                movement_type = 'entrada'
            else:
                movement_type = 'saida'
            
            # Verificar se o funcionário existe
            employee_id = movement.get('pessoastoque')
            if employee_id:
                cursor.execute("SELECT id FROM customers WHERE id = ?", (employee_id,))
                if not cursor.fetchone():
                    employee_id = None
            
            # Criar notas
            notes = f"Migrado do sistema antigo - ID original: {movement.get('ids')}"
            if movement.get('noticia'):
                notes += f" - {movement.get('noticia')}"
            
            cursor.execute('''
                INSERT INTO inventory (
                    item_type, item_id, quantity, movement_type, date, 
                    notes, employee_id, location
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                item_type,
                item_id,
                movement.get('quantidade', 1),
                movement_type,
                movement.get('data'),
                notes[:255],  # Limitar tamanho
                employee_id,
                movement.get('lugar', 'stoque')
            ))
            migrated_count += 1
        except Exception as e:
            print(f"Erro ao inserir movimentação ID {movement.get('ids', 'UNKNOWN')}: {e}")
    
    # Confirmar transação
    conn.commit()
    
    # Verificar resultado
    cursor.execute("SELECT COUNT(*) FROM inventory")
    total_in_db = cursor.fetchone()[0]
    
    conn.close()
    
    print(f"Migração de estoque concluída!")
    print(f"Movimentações migradas: {migrated_count}")
    print(f"Total no banco: {total_in_db}")
    
    return True

if __name__ == "__main__":
    print("=== MIGRAÇÃO DE ESTOQUE ===")
    print("Migrando dados de estoque do arquivo reformatado para o banco de dados...")
    
    if migrate_estoque_to_database():
        print("✅ Migração de estoque concluída com sucesso!")
    else:
        print("❌ Falha na migração de estoque!")
        sys.exit(1)
