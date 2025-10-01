#!/usr/bin/env python3
import sqlite3
import re
from datetime import datetime

def parse_date(date_str):
    """Converter data do formato MM/dd/yy HH:mm:ss para formato ISO"""
    if not date_str or date_str == 'nan':
        return None
    try:
        # Formato: 01/23/25 08:02:24
        dt = datetime.strptime(date_str, '%m/%d/%y %H:%M:%S')
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    except:
        return None

def migrate_inventory():
    # Conectar ao banco de dados
    conn = sqlite3.connect('data/joalheria.db')
    cursor = conn.cursor()
    
    # Ler arquivo de estoque
    with open('/home/ubuntu/upload/stoque_reformatted.txt', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Dividir em registros
    registros = content.split('\n\nRegistro ')
    
    migrated_count = 0
    
    for i, registro in enumerate(registros[1:], 1):  # Pular o primeiro elemento vazio
        try:
            lines = registro.strip().split('\n')
            data = {}
            
            # Extrair dados do registro
            for line in lines[1:]:  # Pular a linha do número do registro
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    if value == 'nan':
                        value = None
                    elif key in ['ids', 'id', 'idj']:
                        try:
                            value = int(float(value)) if value else None
                        except:
                            value = None
                    elif key == 'quantidade':
                        try:
                            value = float(value) if value else 0
                        except:
                            value = 0
                    
                    data[key] = value
            
            # Converter data
            data_formatada = parse_date(data.get('data'))
            
            # Determinar material_id baseado no tipo e id
            material_id = 1  # Default
            if data.get('tipo') == 'j' and data.get('idj'):
                # Para joias, usar o idj como referência
                material_id = data.get('idj', 1)
            elif data.get('id'):
                material_id = data.get('id', 1)
            
            # Inserir na tabela inventory
            cursor.execute("""
                INSERT INTO inventory (
                    material_id, quantity_available, quantity_reserved, unit,
                    minimum_stock, cost_per_unit, last_updated, notes,
                    ids, tipo, item_id, data, quantidade, noticia, idj
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                material_id,
                data.get('quantidade', 0),  # quantity_available
                0,  # quantity_reserved
                'unidade',  # unit
                0,  # minimum_stock
                0,  # cost_per_unit
                data_formatada or datetime.now().strftime('%Y-%m-%d %H:%M:%S'),  # last_updated
                data.get('noticia'),  # notes
                data.get('ids'),  # ids
                data.get('tipo'),  # tipo
                data.get('id'),  # item_id
                data.get('data'),  # data original
                data.get('quantidade', 0),  # quantidade
                data.get('noticia'),  # noticia
                data.get('idj')  # idj
            ))
            
            migrated_count += 1
            
            if migrated_count % 100 == 0:
                print(f"Migrados {migrated_count} registros de estoque...")
                
        except Exception as e:
            print(f"Erro ao migrar registro {i}: {e}")
            continue
    
    conn.commit()
    
    # Verificar total migrado
    cursor.execute("SELECT COUNT(*) FROM inventory WHERE ids IS NOT NULL")
    total_migrated = cursor.fetchone()[0]
    
    conn.close()
    
    print(f"Migração de estoque concluída!")
    print(f"Registros migrados: {migrated_count}")
    print(f"Total no banco: {total_migrated}")
    print("✅ Migração de estoque concluída com sucesso!")

if __name__ == "__main__":
    migrate_inventory()
