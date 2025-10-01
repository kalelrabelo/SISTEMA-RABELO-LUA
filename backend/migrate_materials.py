#!/usr/bin/env python3
"""
Script para migrar materiais do arquivo reformatado para o banco de dados
"""

import sqlite3
import os
import sys
import re
from datetime import datetime

def parse_materials_file():
    """Carrega materiais do arquivo reformatado"""
    file_path = '/home/ubuntu/upload/materiais_reformatted.txt'
    
    if not os.path.exists(file_path):
        print(f"Arquivo {file_path} não encontrado!")
        return []
    
    materials = []
    current_material = {}
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Dividir por registros
    records = content.split('Registro ')
    
    for record in records[1:]:  # Pular o primeiro que está vazio
        lines = record.strip().split('\n')
        material = {}
        
        for line in lines[1:]:  # Pular a linha do número do registro
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()
                
                # Converter valores
                if value == 'nan':
                    value = None
                elif key in ['idmat', 'foto', 'quantidade_minima']:
                    try:
                        value = int(float(value)) if value else None
                    except:
                        value = None
                elif key == 'preco_por_dimensao':
                    try:
                        value = float(value) if value else 0.0
                    except:
                        value = 0.0
                
                material[key] = value
        
        if material.get('idmat'):
            materials.append(material)
    
    print(f"Carregados {len(materials)} materiais do arquivo")
    return materials

def migrate_materials_to_database():
    """Migra materiais para o banco de dados"""
    
    # Conectar ao banco de dados
    db_path = 'data/joalheria.db'
    if not os.path.exists(db_path):
        print(f"Banco de dados {db_path} não encontrado!")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Verificar se a tabela materials existe
    cursor.execute("PRAGMA table_info(materials)")
    columns = cursor.fetchall()
    
    if not columns:
        print("Tabela materials não existe! Criando...")
        cursor.execute('''
            CREATE TABLE materials (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                type TEXT,
                price_per_gram REAL DEFAULT 0.0,
                stock_quantity REAL DEFAULT 0.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
    
    # Carregar materiais do arquivo
    materials = parse_materials_file()
    if not materials:
        print("Nenhum material encontrado para migrar!")
        return False
    
    # Limpar tabela materials existente
    cursor.execute("DELETE FROM materials")
    print("Tabela materials limpa")
    
    # Inserir materiais
    migrated_count = 0
    for material in materials:
        try:
            cursor.execute('''
                INSERT INTO materials (
                    name, type, price_per_gram, stock_quantity
                ) VALUES (?, ?, ?, ?)
            ''', (
                material.get('nome_material', ''),
                material.get('tipo_material', ''),
                material.get('preco_por_dimensao', 0.0),
                material.get('quantidade_minima', 0.0)
            ))
            migrated_count += 1
        except Exception as e:
            print(f"Erro ao inserir material {material.get('nome_material', 'UNKNOWN')}: {e}")
    
    # Confirmar transação
    conn.commit()
    
    # Verificar resultado
    cursor.execute("SELECT COUNT(*) FROM materials")
    total_in_db = cursor.fetchone()[0]
    
    conn.close()
    
    print(f"Migração de materiais concluída!")
    print(f"Materiais migrados: {migrated_count}")
    print(f"Total no banco: {total_in_db}")
    
    return True

if __name__ == "__main__":
    print("=== MIGRAÇÃO DE MATERIAIS ===")
    print("Migrando materiais do arquivo reformatado para o banco de dados...")
    
    if migrate_materials_to_database():
        print("✅ Migração de materiais concluída com sucesso!")
    else:
        print("❌ Falha na migração de materiais!")
        sys.exit(1)
