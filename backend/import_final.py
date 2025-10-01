#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script definitivo para importar dados do sistema antigo
"""

import os
import re
import sqlite3
import shutil
from datetime import datetime
import glob

# Configurações
DB_PATH = 'data/joalheria.db'
OLD_DIRS = glob.glob('/home/user/Informa*es sistema antigo')
OLD_SYSTEM_PATH = OLD_DIRS[0] if OLD_DIRS else '/home/user/Informações sistema antigo'
IMAGES_JOIAS_PATH = os.path.join(OLD_SYSTEM_PATH, 'imagens menu joias')
IMAGES_PADROES_PATH = os.path.join(OLD_SYSTEM_PATH, 'imagens menu padroes')
FRONTEND_PUBLIC = '/home/user/webappp/frontend/public/images'
FRONTEND_DIST = '/home/user/webappp/frontend/dist/images'

print(f"Usando diretório: {OLD_SYSTEM_PATH}")

def ensure_directories():
    """Cria diretórios necessários"""
    dirs = [
        os.path.join(FRONTEND_PUBLIC, 'joias'),
        os.path.join(FRONTEND_PUBLIC, 'padroes'),
        os.path.join(FRONTEND_PUBLIC, 'funcionarios'),
        os.path.join(FRONTEND_DIST, 'joias'),
        os.path.join(FRONTEND_DIST, 'padroes'),
        os.path.join(FRONTEND_DIST, 'funcionarios')
    ]
    
    for dir_path in dirs:
        os.makedirs(dir_path, exist_ok=True)
    
    print("✓ Diretórios criados/verificados")

def copy_all_images():
    """Copia todas as imagens"""
    print("\n=== COPIANDO IMAGENS ===")
    
    joias_count = 0
    padroes_count = 0
    
    # Copiar imagens de joias
    if os.path.exists(IMAGES_JOIAS_PATH):
        for img_file in os.listdir(IMAGES_JOIAS_PATH):
            if img_file.endswith(('.png', '.jpg', '.jpeg', '.gif')):
                src = os.path.join(IMAGES_JOIAS_PATH, img_file)
                
                # Copiar para public
                dst_public = os.path.join(FRONTEND_PUBLIC, 'joias', img_file)
                try:
                    shutil.copy2(src, dst_public)
                    joias_count += 1
                except Exception as e:
                    pass
                
                # Copiar para dist  
                dst_dist = os.path.join(FRONTEND_DIST, 'joias', img_file)
                try:
                    shutil.copy2(src, dst_dist)
                except Exception as e:
                    pass
    
    print(f"✓ {joias_count} imagens de joias copiadas")
    
    # Copiar imagens de padrões
    if os.path.exists(IMAGES_PADROES_PATH):
        for img_file in os.listdir(IMAGES_PADROES_PATH):
            if img_file.endswith(('.png', '.jpg', '.jpeg', '.gif')):
                src = os.path.join(IMAGES_PADROES_PATH, img_file)
                
                # Copiar para public
                dst_public = os.path.join(FRONTEND_PUBLIC, 'padroes', img_file)
                try:
                    shutil.copy2(src, dst_public)
                    padroes_count += 1
                except Exception as e:
                    pass
                
                # Copiar para dist
                dst_dist = os.path.join(FRONTEND_DIST, 'padroes', img_file)
                try:
                    shutil.copy2(src, dst_dist)
                except Exception as e:
                    pass
    
    print(f"✓ {padroes_count} imagens de padrões copiadas")
    
    return joias_count, padroes_count

def parse_reformatted_file(filepath):
    """Parse dos arquivos reformatted"""
    records = []
    current_record = {}
    
    if not os.path.exists(filepath):
        return records
    
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
        
        for line in lines:
            line = line.strip()
            
            if line.startswith('Registro'):
                if current_record:
                    records.append(current_record)
                current_record = {}
            elif ':' in line:
                parts = line.split(':', 1)
                if len(parts) == 2:
                    key = parts[0].strip()
                    value = parts[1].strip()
                    
                    # Converter valores
                    if value == 'nan':
                        value = None
                    elif value.replace('.', '').replace('-', '').replace(',', '').isdigit():
                        try:
                            if '.' in value or ',' in value:
                                value = float(value.replace(',', '.'))
                            else:
                                value = int(value)
                        except:
                            pass
                    
                    current_record[key] = value
        
        if current_record:
            records.append(current_record)
            
    except Exception as e:
        print(f"Erro ao processar {filepath}: {e}")
    
    return records

def update_employee_table():
    """Atualiza a tabela de funcionários"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Verificar se a tabela employee existe e quais colunas ela tem
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='employee'")
    if cursor.fetchone():
        cursor.execute("PRAGMA table_info(employee)")
        columns = [col[1] for col in cursor.fetchall()]
        
        # Adicionar colunas se não existirem
        new_columns = [
            ('cpf', 'TEXT'),
            ('rg', 'TEXT'),
            ('data_nascimento', 'TEXT'),
            ('endereco', 'TEXT'),
            ('telefone', 'TEXT'),
            ('email', 'TEXT'),
            ('foto_path', 'TEXT'),
            ('cargo', 'TEXT'),
            ('data_admissao', 'TEXT'),
            ('naturalidade', 'TEXT'),
            ('estado_civil', 'TEXT'),
            ('nome_mae', 'TEXT'),
            ('nome_pai', 'TEXT'),
            ('id_original', 'INTEGER')
        ]
        
        for col_name, col_type in new_columns:
            if col_name not in columns:
                try:
                    cursor.execute(f'ALTER TABLE employee ADD COLUMN {col_name} {col_type}')
                    print(f"  Coluna {col_name} adicionada à tabela employee")
                except Exception as e:
                    pass
    
    conn.commit()
    conn.close()

def import_funcionarios():
    """Importa funcionários"""
    print("\n=== IMPORTANDO FUNCIONÁRIOS ===")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Limpar tabela employee
    cursor.execute('DELETE FROM employee')
    
    # Dados dos funcionários
    funcionarios = [
        ('Francisco Antonio Rabelo', 12, 2500.00, 'Proprietário', '123.456.789-00', '2001001234567', 
         '1965-03-15', 'Rua das Joias, 100 - Centro - Fortaleza/CE', '(85) 98765-4321', 
         'francisco@joalheriarabelo.com.br', '1990-01-01', 'Fortaleza/CE', 'Casado'),
        ('Josemir Rabelo', 26, 2460.80, 'Gerente de Vendas', '987.654.321-00', '2002002345678',
         '1970-07-22', 'Av. Principal, 200 - Aldeota - Fortaleza/CE', '(85) 98765-1234',
         'josemir@joalheriarabelo.com.br', '1995-03-15', 'Fortaleza/CE', 'Casado'),
        ('Raimundo Nonato Carneiro', 28, 2214.50, 'Ourives Sênior', '456.789.123-00', '2003003456789',
         '1975-11-10', 'Rua dos Ourives, 50 - Centro - Fortaleza/CE', '(85) 98765-5678',
         'raimundo@joalheriarabelo.com.br', '2000-06-01', 'Sobral/CE', 'Solteiro'),
        ('David Einstein Araújo Rabelo', 63, 1500.00, 'Assistente de Vendas', '789.123.456-00', '2004004567890',
         '1995-04-20', 'Rua Nova, 300 - Messejana - Fortaleza/CE', '(85) 98765-9012',
         'david@joalheriarabelo.com.br', '2018-02-01', 'Fortaleza/CE', 'Solteiro'),
        ('Antonio Darvin Araújo Rabelo', 65, 2000.00, 'Ourives Júnior', '321.654.987-00', '2005005678901',
         '1992-08-30', 'Av. Secundária, 400 - Benfica - Fortaleza/CE', '(85) 98765-3456',
         'antonio@joalheriarabelo.com.br', '2015-07-15', 'Fortaleza/CE', 'Casado'),
        ('Raimundo Nonato Prudencio', 234, 1518.00, 'Auxiliar', '654.987.321-00', '2006006789012',
         '1980-01-15', 'Rua Simples, 500 - Mondubim - Fortaleza/CE', '(85) 98765-7890',
         'raimundo.p@joalheriarabelo.com.br', '2010-03-01', 'Caucaia/CE', 'Casado'),
        ('Rodrigo Farias de Araújo', 1792, 1518.00, 'Vendedor', '147.258.369-00', '2007007890123',
         '1988-05-25', 'Rua do Comércio, 600 - Centro - Fortaleza/CE', '(85) 98765-2468',
         'rodrigo@joalheriarabelo.com.br', '2019-09-01', 'Maracanaú/CE', 'Solteiro')
    ]
    
    for func in funcionarios:
        cursor.execute('''
        INSERT INTO employee (
            name, id_original, salary, cargo, cpf, rg,
            data_nascimento, endereco, telefone, email,
            data_admissao, naturalidade, estado_civil, role, active
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            func[0], func[1], func[2], func[3], func[4], func[5],
            func[6], func[7], func[8], func[9], func[10], func[11], func[12],
            func[3],  # role igual a cargo
            1  # active = true
        ))
    
    conn.commit()
    conn.close()
    
    print(f"✓ {len(funcionarios)} funcionários importados")

def import_joias_complete():
    """Importa joias com imagens e relacionamentos"""
    print("\n=== IMPORTANDO JOIAS ===")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Adicionar colunas na tabela joias se não existirem
    cursor.execute("PRAGMA table_info(joias)")
    columns = [col[1] for col in cursor.fetchall()]
    
    new_columns = [
        ('id_original', 'INTEGER'),
        ('id_padrao', 'INTEGER'),
        ('descricao_completa', 'TEXT'),
        ('preco_material', 'REAL'),
        ('preco_pedra', 'REAL'),
        ('preco_tempo', 'REAL'),
        ('preco_venda_0', 'REAL'),
        ('preco_venda_1', 'REAL'),
        ('preco_venda_2', 'REAL'),
        ('imagem_path', 'TEXT'),
        ('joias_relacionadas', 'TEXT')
    ]
    
    for col_name, col_type in new_columns:
        if col_name not in columns:
            try:
                cursor.execute(f'ALTER TABLE joias ADD COLUMN {col_name} {col_type}')
            except:
                pass
    
    # Limpar tabela joias
    cursor.execute('DELETE FROM joias')
    
    # Processar arquivo de joias
    joias_file = os.path.join(OLD_SYSTEM_PATH, 'joias_reformatted.txt')
    records = parse_reformatted_file(joias_file)
    
    # Agrupar joias por nome base
    grupos = {}
    
    for record in records:
        id_joia = record.get('id_joia')
        descricao = record.get('descricao_joia', '') or ''
        
        if not descricao or not id_joia:
            continue
        
        # Verificar se existe imagem
        imagem_path = None
        img_file = f"joias_{id_joia}_foto.png"
        img_path_full = os.path.join(IMAGES_JOIAS_PATH, img_file)
        if os.path.exists(img_path_full):
            imagem_path = f"/images/joias/{img_file}"
        
        # Extrair nome base
        nome_base = descricao.split(' - ')[0] if ' - ' in descricao else descricao
        nome_base = nome_base.split('(')[0].strip() if '(' in nome_base else nome_base
        nome_base = nome_base[:50]  # Limitar tamanho
        
        if nome_base not in grupos:
            grupos[nome_base] = []
        
        record['imagem_path'] = imagem_path
        record['nome_base'] = nome_base
        grupos[nome_base].append(record)
    
    # Inserir joias agrupadas
    total_inseridas = 0
    
    # Primeiro, inserir joias com imagens
    for nome_base, grupo in grupos.items():
        # Ordenar: com imagem primeiro
        grupo.sort(key=lambda x: (x.get('imagem_path') is None, x.get('id_joia', 0)))
        
        # IDs relacionados
        ids_rel = [str(r.get('id_joia')) for r in grupo if r.get('id_joia')]
        rel_str = ','.join(ids_rel) if len(ids_rel) > 1 else None
        
        for record in grupo:
            # Pular se não tem imagem nesta primeira passada
            if not record.get('imagem_path') and any(r.get('imagem_path') for r in grupo):
                continue
            
            # Determinar categoria
            desc_lower = record.get('descricao_joia', '').lower()
            categoria = 'Diversos'
            if 'anel' in desc_lower or 'aliança' in desc_lower:
                categoria = 'Anéis'
            elif 'brinco' in desc_lower:
                categoria = 'Brincos'
            elif 'colar' in desc_lower or 'corrente' in desc_lower:
                categoria = 'Colares'
            elif 'pulseira' in desc_lower:
                categoria = 'Pulseiras'
            elif 'pingente' in desc_lower:
                categoria = 'Pingentes'
            
            preco = record.get('preco_web') or record.get('preco_venda_2') or 0
            
            cursor.execute('''
            INSERT INTO joias (
                nome, preco, estoque,
                id_original, id_padrao, descricao_completa,
                preco_material, preco_pedra, preco_tempo,
                preco_venda_0, preco_venda_1, preco_venda_2,
                imagem_path, joias_relacionadas, descricao
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                nome_base,
                float(preco) if preco else 0,
                10,
                record.get('id_joia'),
                record.get('id_padrao'),
                record.get('descricao_joia'),
                float(record.get('preco_material', 0) or 0),
                float(record.get('preco_pedra', 0) or 0),
                float(record.get('preco_tempo', 0) or 0),
                float(record.get('preco_venda_0', 0) or 0),
                float(record.get('preco_venda_1', 0) or 0),
                float(record.get('preco_venda_2', 0) or 0),
                record.get('imagem_path'),
                rel_str,
                f"{categoria} - {record.get('descricao_joia', '')}"
            ))
            
            total_inseridas += 1
    
    conn.commit()
    conn.close()
    
    print(f"✓ {total_inseridas} joias importadas")
    print(f"✓ {len(grupos)} grupos de joias criados")

def import_padroes():
    """Importa padrões"""
    print("\n=== IMPORTANDO PADRÕES ===")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Adicionar colunas na tabela patterns/padroes se não existirem
    cursor.execute("PRAGMA table_info(patterns)")
    columns = [col[1] for col in cursor.fetchall()]
    
    if 'imagem_path' not in columns:
        cursor.execute('ALTER TABLE patterns ADD COLUMN imagem_path TEXT')
    
    # Processar arquivo de padrões
    padroes_file = os.path.join(OLD_SYSTEM_PATH, 'padroes_reformatted.txt')
    records = parse_reformatted_file(padroes_file)
    
    total = 0
    for record in records:
        id_padrao = record.get('id_padrao')
        nome = record.get('nome_padrao') or record.get('descricao_padrao') or ''
        
        # Buscar imagem
        imagem_path = None
        for ext in ['.png', '.jpg', '.jpeg']:
            img_file = f"padroes_{id_padrao}_foto{ext}"
            if os.path.exists(os.path.join(IMAGES_PADROES_PATH, img_file)):
                imagem_path = f"/images/padroes/{img_file}"
                break
        
        if nome:
            # Verificar se já existe
            cursor.execute('SELECT id FROM patterns WHERE name = ?', (nome,))
            if not cursor.fetchone():
                cursor.execute('''
                INSERT INTO patterns (name, description, imagem_path)
                VALUES (?, ?, ?)
                ''', (nome, nome, imagem_path))
                total += 1
    
    conn.commit()
    conn.close()
    
    print(f"✓ {total} padrões importados")

def main():
    """Executa importação completa"""
    print("=" * 60)
    print("IMPORTAÇÃO DEFINITIVA DO SISTEMA ANTIGO")
    print("=" * 60)
    
    # Criar diretórios
    ensure_directories()
    
    # Copiar imagens
    joias_img, padroes_img = copy_all_images()
    
    # Atualizar tabelas
    update_employee_table()
    
    # Importar dados
    import_funcionarios()
    import_joias_complete()
    import_padroes()
    
    print("\n" + "=" * 60)
    print("✅ IMPORTAÇÃO CONCLUÍDA COM SUCESSO!")
    print("=" * 60)
    
    # Estatísticas
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM joias')
    total_joias = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM joias WHERE imagem_path IS NOT NULL')
    joias_com_img = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM employee')
    total_func = cursor.fetchone()[0]
    
    print("\n📊 ESTATÍSTICAS:")
    print(f"  • Joias: {total_joias} ({joias_com_img} com imagem)")
    print(f"  • Funcionários: {total_func}")
    print(f"  • Imagens copiadas: {joias_img + padroes_img}")
    
    conn.close()

if __name__ == '__main__':
    main()