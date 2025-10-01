#!/usr/bin/env python3
"""
Script para migrar clientes do arquivo estático para o banco de dados
"""

import sqlite3
import json
import os
import sys
from datetime import datetime

def load_clients_from_js_file():
    """Carrega clientes do arquivo JavaScript estático"""
    js_file_path = '../frontend/src/data/clientesData.js'
    
    if not os.path.exists(js_file_path):
        print(f"Arquivo {js_file_path} não encontrado!")
        return []
    
    with open(js_file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extrair o array JSON do arquivo JavaScript
    start_marker = 'const clientesIniciais = ['
    end_marker = '];\n\nexport default clientesIniciais;'
    
    start_idx = content.find(start_marker)
    if start_idx == -1:
        print("Marcador de início não encontrado!")
        return []
    
    start_idx += len(start_marker) - 1  # Incluir o '['
    
    end_idx = content.find(end_marker)
    if end_idx == -1:
        print("Marcador de fim não encontrado!")
        return []
    
    json_content = content[start_idx:end_idx + 1]  # Incluir o ']'
    
    try:
        clients = json.loads(json_content)
        print(f"Carregados {len(clients)} clientes do arquivo estático")
        return clients
    except json.JSONDecodeError as e:
        print(f"Erro ao decodificar JSON: {e}")
        return []

def migrate_clients_to_database():
    """Migra clientes para o banco de dados"""
    
    # Conectar ao banco de dados
    db_path = 'data/joalheria.db'
    if not os.path.exists(db_path):
        print(f"Banco de dados {db_path} não encontrado!")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Verificar se a tabela customers existe e sua estrutura
    cursor.execute("PRAGMA table_info(customers)")
    columns = cursor.fetchall()
    print(f"Estrutura da tabela customers: {columns}")
    
    if not columns:
        print("Tabela customers não existe! Criando...")
        cursor.execute('''
            CREATE TABLE customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT,
                phone TEXT,
                cpf TEXT,
                address TEXT,
                city TEXT,
                state TEXT,
                zip_code TEXT,
                birth_date DATE,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
    
    # Carregar clientes do arquivo estático
    clients = load_clients_from_js_file()
    if not clients:
        print("Nenhum cliente encontrado para migrar!")
        return False
    
    # Limpar tabela customers existente
    cursor.execute("DELETE FROM customers")
    print("Tabela customers limpa")
    
    # Inserir clientes
    migrated_count = 0
    for client in clients:
        try:
            # Combinar nome e sobrenome
            full_name = f"{client.get('nome', '')} {client.get('sobrenome', '')}".strip()
            if not full_name:
                full_name = "Cliente sem nome"
            
            cursor.execute('''
                INSERT INTO customers (
                    name, email, phone, address, birth_date, notes
                ) VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                full_name,
                client.get('email', ''),
                client.get('celular', ''),
                client.get('endereco_completo', ''),
                client.get('data_aniversario', None) if client.get('data_aniversario') else None,
                client.get('noticias', '')
            ))
            migrated_count += 1
        except Exception as e:
            print(f"Erro ao inserir cliente {client.get('nome', 'UNKNOWN')}: {e}")
    
    # Confirmar transação
    conn.commit()
    
    # Verificar resultado
    cursor.execute("SELECT COUNT(*) FROM customers")
    total_in_db = cursor.fetchone()[0]
    
    conn.close()
    
    print(f"Migração concluída!")
    print(f"Clientes migrados: {migrated_count}")
    print(f"Total no banco: {total_in_db}")
    
    return True

if __name__ == "__main__":
    print("=== MIGRAÇÃO DE CLIENTES ===")
    print("Migrando clientes do arquivo estático para o banco de dados...")
    
    if migrate_clients_to_database():
        print("✅ Migração concluída com sucesso!")
    else:
        print("❌ Falha na migração!")
        sys.exit(1)
