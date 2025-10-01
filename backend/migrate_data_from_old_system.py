#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import sqlite3
import json
import shutil
from pathlib import Path
from datetime import datetime

# Configurações
OLD_DATA_PATH = "/home/user/Informa#U00e7#U00f5es sistema antigo"
DATABASE_PATH = "/home/user/webapp/backend/data/joalheria.db"
BACKUP_PATH = "/home/user/webapp/backend/data/joalheria_backup_{}.db".format(
    datetime.now().strftime("%Y%m%d_%H%M%S")
)
IMAGES_SOURCE = os.path.join(OLD_DATA_PATH, "imagens menu joias")
IMAGES_DEST = "/home/user/webapp/frontend/public/images/jewelry"

def backup_database():
    """Criar backup do banco antes da migração"""
    try:
        if os.path.exists(DATABASE_PATH):
            shutil.copy2(DATABASE_PATH, BACKUP_PATH)
            print(f"✅ Backup criado: {BACKUP_PATH}")
            return True
    except Exception as e:
        print(f"❌ Erro ao criar backup: {e}")
        return False

def parse_reformatted_file(filepath, delimiter='|'):
    """Parse de arquivo reformatted do sistema antigo"""
    data = []
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
            
            if len(lines) < 2:
                return []
            
            # Primeira linha são os headers
            headers = [h.strip() for h in lines[0].split(delimiter)]
            
            # Processar dados
            for line in lines[1:]:
                values = [v.strip() for v in line.split(delimiter)]
                if len(values) == len(headers):
                    row = dict(zip(headers, values))
                    data.append(row)
                    
    except Exception as e:
        print(f"⚠️ Erro ao ler {filepath}: {e}")
    
    return data

def migrate_materials():
    """Migrar materiais"""
    print("\n📦 Migrando materiais...")
    file_path = os.path.join(OLD_DATA_PATH, "materiais_reformatted.txt")
    
    if not os.path.exists(file_path):
        print("⚠️ Arquivo materiais_reformatted.txt não encontrado")
        return
    
    materials = parse_reformatted_file(file_path)
    
    if not materials:
        print("⚠️ Nenhum material encontrado no arquivo")
        return
    
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Criar tabela se não existir
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS materials (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            type TEXT,
            price_per_gram REAL,
            stock_quantity REAL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    count = 0
    for mat in materials:
        try:
            name = mat.get('nome', mat.get('material', 'Unknown'))
            if name and name != 'Unknown':
                cursor.execute('''
                    INSERT OR IGNORE INTO materials (name, type, price_per_gram)
                    VALUES (?, ?, ?)
                ''', (name, mat.get('tipo', 'Metal'), 0.0))
                count += 1
        except Exception as e:
            print(f"   ⚠️ Erro ao inserir material: {e}")
    
    conn.commit()
    conn.close()
    print(f"   ✅ {count} materiais migrados")

def migrate_stones():
    """Migrar pedras"""
    print("\n💎 Migrando pedras...")
    file_path = os.path.join(OLD_DATA_PATH, "pedras_reformatted.txt")
    
    if not os.path.exists(file_path):
        print("⚠️ Arquivo pedras_reformatted.txt não encontrado")
        return
    
    stones = parse_reformatted_file(file_path)
    
    if not stones:
        print("⚠️ Nenhuma pedra encontrada no arquivo")
        return
    
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Criar tabela se não existir
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS stones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            type TEXT,
            color TEXT,
            price_per_carat REAL,
            stock_quantity REAL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    count = 0
    for stone in stones:
        try:
            name = stone.get('nome', stone.get('pedra', 'Unknown'))
            if name and name != 'Unknown':
                cursor.execute('''
                    INSERT OR IGNORE INTO stones (name, type, color, price_per_carat)
                    VALUES (?, ?, ?, ?)
                ''', (name, stone.get('tipo', 'Preciosa'), stone.get('cor', ''), 0.0))
                count += 1
        except Exception as e:
            print(f"   ⚠️ Erro ao inserir pedra: {e}")
    
    conn.commit()
    conn.close()
    print(f"   ✅ {count} pedras migradas")

def migrate_patterns():
    """Migrar padrões"""
    print("\n🎨 Migrando padrões...")
    file_path = os.path.join(OLD_DATA_PATH, "padroes_reformatted.txt")
    
    if not os.path.exists(file_path):
        print("⚠️ Arquivo padroes_reformatted.txt não encontrado")
        return
    
    patterns = parse_reformatted_file(file_path)
    
    if not patterns:
        print("⚠️ Nenhum padrão encontrado no arquivo")
        return
    
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Criar tabela se não existir
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS patterns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            category TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    count = 0
    for pattern in patterns:
        try:
            name = pattern.get('nome', pattern.get('padrao', 'Unknown'))
            if name and name != 'Unknown':
                cursor.execute('''
                    INSERT OR IGNORE INTO patterns (name, description, category)
                    VALUES (?, ?, ?)
                ''', (name, pattern.get('descricao', ''), pattern.get('categoria', 'Geral')))
                count += 1
        except Exception as e:
            print(f"   ⚠️ Erro ao inserir padrão: {e}")
    
    conn.commit()
    conn.close()
    print(f"   ✅ {count} padrões migrados")

def migrate_jewelry():
    """Migrar joias"""
    print("\n💍 Migrando joias...")
    file_path = os.path.join(OLD_DATA_PATH, "joias_reformatted.txt")
    
    if not os.path.exists(file_path):
        print("⚠️ Arquivo joias_reformatted.txt não encontrado")
        return
    
    jewelry = parse_reformatted_file(file_path)
    
    if not jewelry:
        print("⚠️ Nenhuma joia encontrada no arquivo")
        return
    
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Garantir que tabela jewelry existe com estrutura correta
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS jewelry (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            code TEXT UNIQUE,
            category TEXT,
            subcategory TEXT,
            material TEXT,
            weight REAL DEFAULT 0,
            size TEXT,
            stone TEXT,
            price REAL DEFAULT 0,
            cost REAL DEFAULT 0,
            stock_quantity INTEGER DEFAULT 0,
            image_url TEXT,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    count = 0
    for item in jewelry[:500]:  # Limitar a 500 items inicialmente
        try:
            # Extrair dados
            name = item.get('nome', item.get('descricao', 'Joia'))
            code = item.get('codigo', item.get('id', f'J{count:05d}'))
            category = item.get('categoria', item.get('tipo', 'Geral'))
            material_info = item.get('material', '')
            stone_info = item.get('pedra', '')
            size_info = item.get('tamanho', item.get('medida', ''))
            
            # Calcular preço (simplificado)
            try:
                price = float(item.get('preco', item.get('valor', '0')).replace(',', '.'))
            except:
                price = 100.0  # Preço padrão
            
            # Imagem
            image_url = f"/images/jewelry/{code}.jpg" if code else None
            
            cursor.execute('''
                INSERT OR REPLACE INTO jewelry 
                (name, code, category, material, stone, size, price, cost, stock_quantity, image_url, description)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                name, code, category, material_info, stone_info, size_info,
                price, price * 0.6, 10, image_url, 
                f"{name} - {category}"
            ))
            count += 1
            
        except Exception as e:
            print(f"   ⚠️ Erro ao inserir joia: {e}")
    
    conn.commit()
    conn.close()
    print(f"   ✅ {count} joias migradas")

def copy_images():
    """Copiar imagens das joias"""
    print("\n🖼️ Copiando imagens...")
    
    # Criar diretório de destino
    os.makedirs(IMAGES_DEST, exist_ok=True)
    
    if not os.path.exists(IMAGES_SOURCE):
        print(f"⚠️ Pasta de imagens não encontrada: {IMAGES_SOURCE}")
        return
    
    count = 0
    for file in os.listdir(IMAGES_SOURCE):
        if file.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
            try:
                src = os.path.join(IMAGES_SOURCE, file)
                dst = os.path.join(IMAGES_DEST, file)
                shutil.copy2(src, dst)
                count += 1
            except Exception as e:
                print(f"   ⚠️ Erro ao copiar {file}: {e}")
    
    print(f"   ✅ {count} imagens copiadas")

def migrate_clients():
    """Migrar clientes"""
    print("\n👥 Migrando clientes...")
    file_path = os.path.join(OLD_DATA_PATH, "clientes_reformatted.txt")
    
    if not os.path.exists(file_path):
        print("⚠️ Arquivo clientes_reformatted.txt não encontrado")
        return
    
    clients = parse_reformatted_file(file_path)
    
    if not clients:
        print("⚠️ Nenhum cliente encontrado no arquivo")
        return
    
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Criar tabela customers se não existir
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT,
            phone TEXT,
            cpf TEXT UNIQUE,
            address TEXT,
            city TEXT,
            state TEXT,
            zip_code TEXT,
            birth_date DATE,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    count = 0
    for client in clients[:1000]:  # Limitar a 1000 clientes
        try:
            name = client.get('nome', client.get('cliente', ''))
            if name:
                cursor.execute('''
                    INSERT OR IGNORE INTO customers 
                    (name, email, phone, cpf, address, city)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    name,
                    client.get('email', ''),
                    client.get('telefone', client.get('tel', '')),
                    client.get('cpf', client.get('documento', '')),
                    client.get('endereco', client.get('rua', '')),
                    client.get('cidade', 'Não informada')
                ))
                count += 1
        except Exception as e:
            print(f"   ⚠️ Erro ao inserir cliente: {e}")
    
    conn.commit()
    conn.close()
    print(f"   ✅ {count} clientes migrados")

def verify_migration():
    """Verificar dados migrados"""
    print("\n🔍 Verificando migração...")
    
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    tables = {
        'jewelry': 'joias',
        'materials': 'materiais',
        'stones': 'pedras',
        'patterns': 'padrões',
        'customers': 'clientes'
    }
    
    for table, name in tables.items():
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"   📊 {name}: {count} registros")
        except:
            print(f"   ⚠️ Tabela {table} não encontrada")
    
    conn.close()

def main():
    """Função principal de migração"""
    print("=" * 60)
    print("    MIGRAÇÃO DE DADOS - SISTEMA ANTIGO JOALHERIA")
    print("=" * 60)
    
    # Fazer backup
    if not backup_database():
        resp = input("\n⚠️ Continuar sem backup? (s/n): ")
        if resp.lower() != 's':
            return
    
    # Migrar dados
    migrate_materials()
    migrate_stones()
    migrate_patterns()
    migrate_jewelry()
    migrate_clients()
    copy_images()
    
    # Verificar
    verify_migration()
    
    print("\n" + "=" * 60)
    print("✅ MIGRAÇÃO CONCLUÍDA!")
    print("=" * 60)

if __name__ == "__main__":
    main()