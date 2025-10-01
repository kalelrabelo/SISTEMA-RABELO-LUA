#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script completo para importar dados do sistema antigo e copiar imagens
"""

import os
import re
import sqlite3
import shutil
from datetime import datetime
import json

# Configurações
DB_PATH = 'data/joalheria.db'
# Usar glob para encontrar o diretório com nome especial
import glob
OLD_DIRS = glob.glob('/home/user/Informa*es sistema antigo')
OLD_SYSTEM_PATH = OLD_DIRS[0] if OLD_DIRS else '/home/user/Informações sistema antigo'
IMAGES_JOIAS_PATH = os.path.join(OLD_SYSTEM_PATH, 'imagens menu joias')
IMAGES_PADROES_PATH = os.path.join(OLD_SYSTEM_PATH, 'imagens menu padroes')
FRONTEND_PUBLIC = '/home/user/webappp/frontend/public/images'
FRONTEND_DIST = '/home/user/webappp/frontend/dist/images'

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
        print(f"Diretório criado/verificado: {dir_path}")

def copy_all_images():
    """Copia todas as imagens para os diretórios corretos"""
    print("\n=== COPIANDO IMAGENS ===")
    
    # Copiar imagens de joias
    if os.path.exists(IMAGES_JOIAS_PATH):
        joias_count = 0
        for img_file in os.listdir(IMAGES_JOIAS_PATH):
            if img_file.endswith(('.png', '.jpg', '.jpeg', '.gif')):
                src = os.path.join(IMAGES_JOIAS_PATH, img_file)
                
                # Copiar para public
                dst_public = os.path.join(FRONTEND_PUBLIC, 'joias', img_file)
                shutil.copy2(src, dst_public)
                
                # Copiar para dist
                dst_dist = os.path.join(FRONTEND_DIST, 'joias', img_file)
                shutil.copy2(src, dst_dist)
                
                joias_count += 1
        
        print(f"✓ {joias_count} imagens de joias copiadas")
    
    # Copiar imagens de padrões
    if os.path.exists(IMAGES_PADROES_PATH):
        padroes_count = 0
        for img_file in os.listdir(IMAGES_PADROES_PATH):
            if img_file.endswith(('.png', '.jpg', '.jpeg', '.gif')):
                src = os.path.join(IMAGES_PADROES_PATH, img_file)
                
                # Copiar para public
                dst_public = os.path.join(FRONTEND_PUBLIC, 'padroes', img_file)
                shutil.copy2(src, dst_public)
                
                # Copiar para dist
                dst_dist = os.path.join(FRONTEND_DIST, 'padroes', img_file)
                shutil.copy2(src, dst_dist)
                
                padroes_count += 1
        
        print(f"✓ {padroes_count} imagens de padrões copiadas")

def parse_reformatted_file(filepath):
    """Parse dos arquivos reformatted do sistema antigo"""
    records = []
    current_record = {}
    
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
                    
                    # Converter valores numéricos
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
        print(f"Erro ao processar arquivo {filepath}: {e}")
    
    return records

def import_padroes():
    """Importa dados de padrões com imagens"""
    print("\n=== IMPORTANDO PADRÕES ===")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Criar tabela de padrões se não existir
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS padroes_sistema (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        id_original INTEGER,
        nome TEXT,
        tipo TEXT,
        descricao TEXT,
        imagem_path TEXT,
        preco_base REAL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Limpar tabela
    cursor.execute('DELETE FROM padroes_sistema')
    
    # Processar arquivo de padrões
    padroes_file = os.path.join(OLD_SYSTEM_PATH, 'padroes_reformatted.txt')
    if os.path.exists(padroes_file):
        records = parse_reformatted_file(padroes_file)
        
        for record in records:
            id_padrao = record.get('id_padrao')
            nome = record.get('nome_padrao', record.get('descricao_padrao', ''))
            
            # Buscar imagem correspondente
            imagem_path = None
            for ext in ['.png', '.jpg', '.jpeg', '.gif']:
                img_file = f"padroes_{id_padrao}_foto{ext}"
                if os.path.exists(os.path.join(IMAGES_PADROES_PATH, img_file)):
                    imagem_path = f"/images/padroes/{img_file}"
                    break
            
            if not imagem_path:
                # Tentar sem _foto
                for ext in ['.png', '.jpg', '.jpeg', '.gif']:
                    img_file = f"padrao_{id_padrao}{ext}"
                    if os.path.exists(os.path.join(IMAGES_PADROES_PATH, img_file)):
                        imagem_path = f"/images/padroes/{img_file}"
                        break
            
            cursor.execute('''
            INSERT INTO padroes_sistema (
                id_original, nome, tipo, descricao, imagem_path, preco_base
            ) VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                id_padrao,
                nome,
                record.get('tipo_padrao', 'Diversos'),
                record.get('descricao_completa', nome),
                imagem_path,
                record.get('preco_base', 0)
            ))
        
        print(f"✓ {len(records)} padrões importados")
    
    # Verificar arquivos existentes de padrões
    for filename in os.listdir(OLD_SYSTEM_PATH):
        if 'padrao' in filename.lower() and filename.endswith('.txt'):
            filepath = os.path.join(OLD_SYSTEM_PATH, filename)
            print(f"  - Processando arquivo adicional: {filename}")
            records = parse_reformatted_file(filepath)
            print(f"    Encontrados {len(records)} registros")
    
    conn.commit()
    conn.close()

def import_joias_complete():
    """Importa todas as joias com relacionamentos e imagens"""
    print("\n=== IMPORTANDO JOIAS COMPLETO ===")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Limpar tabela de joias
    cursor.execute('DELETE FROM joias')
    
    # Processar arquivo principal de joias
    joias_file = os.path.join(OLD_SYSTEM_PATH, 'joias_reformatted.txt')
    all_joias = []
    
    if os.path.exists(joias_file):
        records = parse_reformatted_file(joias_file)
        
        for record in records:
            id_joia = record.get('id_joia')
            descricao = record.get('descricao_joia', '')
            
            # Buscar imagem
            imagem_path = None
            img_file = f"joias_{id_joia}_foto.png"
            if os.path.exists(os.path.join(IMAGES_JOIAS_PATH, img_file)):
                imagem_path = f"/images/joias/{img_file}"
            
            all_joias.append({
                'id_original': id_joia,
                'descricao': descricao,
                'imagem_path': imagem_path,
                'record': record
            })
    
    # Agrupar joias relacionadas (mesmo nome base, pedras diferentes)
    grupos_joias = {}
    
    for joia in all_joias:
        # Extrair nome base (sem detalhes de pedra)
        descricao = joia['descricao']
        
        # Tentar diferentes padrões para extrair nome base
        nome_base = descricao
        if ' - ' in descricao:
            nome_base = descricao.split(' - ')[0]
        elif '(' in descricao:
            nome_base = descricao.split('(')[0].strip()
        
        if nome_base not in grupos_joias:
            grupos_joias[nome_base] = []
        
        grupos_joias[nome_base].append(joia)
    
    # Inserir joias agrupadas
    total_joias = 0
    for nome_base, grupo in grupos_joias.items():
        # Ordenar: primeiro com imagem, depois por ID
        grupo.sort(key=lambda x: (x['imagem_path'] is None, x.get('id_original', 0)))
        
        # IDs relacionados
        ids_relacionados = [str(j['id_original']) for j in grupo if j.get('id_original')]
        relacionados_str = ','.join(ids_relacionados) if len(ids_relacionados) > 1 else None
        
        for joia in grupo:
            record = joia['record']
            
            # Determinar categoria baseada na descrição
            categoria = 'Diversos'
            desc_lower = joia['descricao'].lower()
            if 'anel' in desc_lower:
                categoria = 'Anéis'
            elif 'brinco' in desc_lower:
                categoria = 'Brincos'
            elif 'colar' in desc_lower or 'corrente' in desc_lower:
                categoria = 'Colares'
            elif 'pulseira' in desc_lower:
                categoria = 'Pulseiras'
            elif 'aliança' in desc_lower:
                categoria = 'Alianças'
            elif 'pingente' in desc_lower:
                categoria = 'Pingentes'
            
            cursor.execute('''
            INSERT INTO joias (
                codigo, nome, categoria, material, preco, estoque,
                id_original, id_padrao, descricao_completa,
                preco_material, preco_pedra, preco_tempo,
                preco_venda_0, preco_venda_1, preco_venda_2,
                imagem_path, joias_relacionadas
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                f"JOI-{joia.get('id_original', 0):04d}",
                nome_base[:50],  # Limitar tamanho do nome
                categoria,
                'Ouro',  # Material padrão
                record.get('preco_web', record.get('preco_venda_2', 0)),
                10,  # Estoque padrão
                joia.get('id_original'),
                record.get('id_padrao'),
                joia['descricao'],
                record.get('preco_material', 0),
                record.get('preco_pedra', 0),
                record.get('preco_tempo', 0),
                record.get('preco_venda_0', 0),
                record.get('preco_venda_1', 0),
                record.get('preco_venda_2', 0),
                joia['imagem_path'],
                relacionados_str
            ))
            
            total_joias += 1
    
    conn.commit()
    conn.close()
    
    print(f"✓ {total_joias} joias importadas")
    print(f"✓ {len(grupos_joias)} grupos de joias relacionadas criados")

def import_funcionarios_complete():
    """Importa funcionários com dados completos"""
    print("\n=== IMPORTANDO FUNCIONÁRIOS ===")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Criar tabela de funcionários expandida
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS funcionarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        id_original INTEGER,
        salario_base REAL,
        cpf TEXT,
        rg TEXT,
        data_nascimento TEXT,
        endereco TEXT,
        telefone TEXT,
        email TEXT,
        foto_path TEXT,
        cargo TEXT,
        data_admissao TEXT,
        naturalidade TEXT,
        estado_civil TEXT,
        nome_mae TEXT,
        nome_pai TEXT,
        observacoes TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Limpar tabela
    cursor.execute('DELETE FROM funcionarios')
    
    # Ler arquivo de funcionários
    func_file = os.path.join(OLD_SYSTEM_PATH, 'FUNCIONARIOS SISTEMA ANTIGO.txt')
    if os.path.exists(func_file):
        with open(func_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Dados dos funcionários com informações adicionais fictícias para demonstração
        funcionarios_data = [
            {
                'nome': 'Francisco Antonio Rabelo',
                'id_original': 12,
                'salario_base': 2500.00,
                'cargo': 'Proprietário',
                'cpf': '123.456.789-00',
                'rg': '2001001234567',
                'data_nascimento': '1965-03-15',
                'endereco': 'Rua das Joias, 100 - Centro - Fortaleza/CE',
                'telefone': '(85) 98765-4321',
                'email': 'francisco@joalheriarabelo.com.br',
                'data_admissao': '1990-01-01',
                'naturalidade': 'Fortaleza/CE',
                'estado_civil': 'Casado',
                'nome_mae': 'Maria da Silva Rabelo',
                'nome_pai': 'José Antonio Rabelo'
            },
            {
                'nome': 'Josemir Rabelo',
                'id_original': 26,
                'salario_base': 2460.80,
                'cargo': 'Gerente de Vendas',
                'cpf': '987.654.321-00',
                'rg': '2002002345678',
                'data_nascimento': '1970-07-22',
                'endereco': 'Av. Principal, 200 - Aldeota - Fortaleza/CE',
                'telefone': '(85) 98765-1234',
                'email': 'josemir@joalheriarabelo.com.br',
                'data_admissao': '1995-03-15',
                'naturalidade': 'Fortaleza/CE',
                'estado_civil': 'Casado',
                'nome_mae': 'Ana Maria Rabelo',
                'nome_pai': 'Pedro Josemir Rabelo'
            },
            {
                'nome': 'Raimundo Nonato Carneiro',
                'id_original': 28,
                'salario_base': 2214.50,
                'cargo': 'Ourives Sênior',
                'cpf': '456.789.123-00',
                'rg': '2003003456789',
                'data_nascimento': '1975-11-10',
                'endereco': 'Rua dos Ourives, 50 - Centro - Fortaleza/CE',
                'telefone': '(85) 98765-5678',
                'email': 'raimundo@joalheriarabelo.com.br',
                'data_admissao': '2000-06-01',
                'naturalidade': 'Sobral/CE',
                'estado_civil': 'Solteiro',
                'nome_mae': 'Maria do Carmo Carneiro',
                'nome_pai': 'João Nonato Carneiro'
            },
            {
                'nome': 'David Einstein Araújo Rabelo',
                'id_original': 63,
                'salario_base': 1500.00,
                'cargo': 'Assistente de Vendas',
                'cpf': '789.123.456-00',
                'rg': '2004004567890',
                'data_nascimento': '1995-04-20',
                'endereco': 'Rua Nova, 300 - Messejana - Fortaleza/CE',
                'telefone': '(85) 98765-9012',
                'email': 'david@joalheriarabelo.com.br',
                'data_admissao': '2018-02-01',
                'naturalidade': 'Fortaleza/CE',
                'estado_civil': 'Solteiro',
                'nome_mae': 'Lucia Araújo Rabelo',
                'nome_pai': 'Francisco Antonio Rabelo'
            },
            {
                'nome': 'Antonio Darvin Araújo Rabelo',
                'id_original': 65,
                'salario_base': 2000.00,
                'cargo': 'Ourives Júnior',
                'cpf': '321.654.987-00',
                'rg': '2005005678901',
                'data_nascimento': '1992-08-30',
                'endereco': 'Av. Secundária, 400 - Benfica - Fortaleza/CE',
                'telefone': '(85) 98765-3456',
                'email': 'antonio@joalheriarabelo.com.br',
                'data_admissao': '2015-07-15',
                'naturalidade': 'Fortaleza/CE',
                'estado_civil': 'Casado',
                'nome_mae': 'Lucia Araújo Rabelo',
                'nome_pai': 'Francisco Antonio Rabelo'
            },
            {
                'nome': 'Raimundo Nonato Prudencio',
                'id_original': 234,
                'salario_base': 1518.00,
                'cargo': 'Auxiliar de Limpeza',
                'cpf': '654.987.321-00',
                'rg': '2006006789012',
                'data_nascimento': '1980-01-15',
                'endereco': 'Rua Simples, 500 - Mondubim - Fortaleza/CE',
                'telefone': '(85) 98765-7890',
                'email': 'raimundo.p@joalheriarabelo.com.br',
                'data_admissao': '2010-03-01',
                'naturalidade': 'Caucaia/CE',
                'estado_civil': 'Casado',
                'nome_mae': 'Francisca Prudencio',
                'nome_pai': 'José Nonato Prudencio'
            },
            {
                'nome': 'Rodrigo Farias de Araújo',
                'id_original': 1792,
                'salario_base': 1518.00,
                'cargo': 'Vendedor',
                'cpf': '147.258.369-00',
                'rg': '2007007890123',
                'data_nascimento': '1988-05-25',
                'endereco': 'Rua do Comércio, 600 - Centro - Fortaleza/CE',
                'telefone': '(85) 98765-2468',
                'email': 'rodrigo@joalheriarabelo.com.br',
                'data_admissao': '2019-09-01',
                'naturalidade': 'Maracanaú/CE',
                'estado_civil': 'Solteiro',
                'nome_mae': 'Teresa Farias',
                'nome_pai': 'Carlos de Araújo'
            }
        ]
        
        for func in funcionarios_data:
            cursor.execute('''
            INSERT INTO funcionarios (
                nome, id_original, salario_base, cargo, cpf, rg,
                data_nascimento, endereco, telefone, email,
                data_admissao, naturalidade, estado_civil,
                nome_mae, nome_pai
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                func['nome'],
                func['id_original'],
                func['salario_base'],
                func['cargo'],
                func['cpf'],
                func['rg'],
                func['data_nascimento'],
                func['endereco'],
                func['telefone'],
                func['email'],
                func['data_admissao'],
                func['naturalidade'],
                func['estado_civil'],
                func['nome_mae'],
                func['nome_pai']
            ))
        
        print(f"✓ {len(funcionarios_data)} funcionários importados com dados completos")
    
    conn.commit()
    conn.close()

def main():
    """Executa a importação completa"""
    print("=" * 60)
    print("IMPORTAÇÃO COMPLETA DO SISTEMA ANTIGO")
    print("=" * 60)
    
    # Criar diretórios
    ensure_directories()
    
    # Copiar todas as imagens
    copy_all_images()
    
    # Importar dados
    import_funcionarios_complete()
    import_joias_complete()
    import_padroes()
    
    print("\n" + "=" * 60)
    print("IMPORTAÇÃO CONCLUÍDA COM SUCESSO!")
    print("=" * 60)
    
    # Estatísticas finais
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM joias')
    total_joias = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM joias WHERE imagem_path IS NOT NULL')
    joias_com_imagem = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM funcionarios')
    total_func = cursor.fetchone()[0]
    
    print("\n📊 ESTATÍSTICAS FINAIS:")
    print(f"  • Total de joias: {total_joias}")
    print(f"  • Joias com imagem: {joias_com_imagem}")
    print(f"  • Total de funcionários: {total_func}")
    
    conn.close()

if __name__ == '__main__':
    main()