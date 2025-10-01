#!/usr/bin/env python3
"""
Script para migrar dados de folha de pagamento do sistema antigo para o novo
"""

import sqlite3
import os
import sys

def parse_pagamentos_file():
    """Carrega dados de pagamentos do arquivo reformatado"""
    file_path = '/home/ubuntu/upload/pagamentos_reformatted.txt'
    
    if not os.path.exists(file_path):
        print(f"Arquivo {file_path} não encontrado!")
        return []
    
    payments = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Dividir por registros
    records = content.split('Registro ')
    
    for record in records[1:]:  # Pular o primeiro que está vazio
        lines = record.strip().split('\n')
        payment = {}
        
        for line in lines[1:]:  # Pular a linha do número do registro
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()
                
                # Converter valores
                if value == 'nan':
                    value = None
                elif key in ['idpag', 'idc', 'mes', 'ano', 'minextras']:
                    try:
                        value = int(float(value)) if value else None
                    except:
                        value = None
                elif key in ['producao', 'bonus', 'salariofamilia', 'descvales', 'inss', 'faltas', 'outrasv', 'horaextrap', 'salariobasep']:
                    try:
                        value = float(value) if value else 0.0
                    except:
                        value = 0.0
                
                payment[key] = value
        
        if payment.get('idpag'):
            payments.append(payment)
    
    print(f"Carregados {len(payments)} registros de pagamentos do arquivo")
    return payments

def migrate_pagamentos_to_database():
    """Migra dados de folha de pagamento para o banco de dados"""
    
    # Conectar ao banco de dados
    db_path = 'data/joalheria.db'
    if not os.path.exists(db_path):
        print(f"Banco de dados {db_path} não encontrado!")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Carregar dados do arquivo
    payments = parse_pagamentos_file()
    if not payments:
        print("Nenhum pagamento encontrado para migrar!")
        return False
    
    # Limpar tabela payroll existente
    cursor.execute("DELETE FROM payroll")
    print("Tabela payroll limpa")
    
    # Inserir pagamentos
    migrated_count = 0
    for payment in payments:
        try:
            idc = payment.get('idc')
            mes = payment.get('mes')
            ano = payment.get('ano')
            salario_base = payment.get('salariobasep', 0.0)
            desc_vales = payment.get('descvales', 0.0)
            
            # Verificar se o funcionário existe na tabela customers
            employee_id = None
            if idc:
                cursor.execute("SELECT id FROM customers WHERE id = ?", (idc,))
                result = cursor.fetchone()
                if result:
                    employee_id = idc
                else:
                    # Se não existir, pular este registro
                    print(f"Funcionário com ID {idc} não encontrado na tabela customers")
                    continue
            
            # Calcular salário líquido
            # Salário líquido = salário base - descontos de vales - faltas + horas extras + bônus
            producao = payment.get('producao', 0.0)
            bonus = payment.get('bonus', 0.0)
            faltas = payment.get('faltas', 0.0)
            horas_extra = payment.get('horaextrap', 0.0) * payment.get('minextras', 0) / 60.0  # Converter minutos para horas
            outras_v = payment.get('outrasv', 0.0)
            
            salario_liquido = salario_base + producao + bonus + horas_extra + outras_v - desc_vales - faltas
            
            cursor.execute('''
                INSERT INTO payroll (
                    employee_id, month, year, base_salary, total_vales, net_salary
                ) VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                employee_id,
                mes,
                ano,
                salario_base,
                desc_vales,
                salario_liquido
            ))
            migrated_count += 1
        except Exception as e:
            print(f"Erro ao inserir pagamento ID {payment.get('idpag', 'UNKNOWN')}: {e}")
    
    # Confirmar transação
    conn.commit()
    
    # Verificar resultado
    cursor.execute("SELECT COUNT(*) FROM payroll")
    total_in_db = cursor.fetchone()[0]
    
    conn.close()
    
    print(f"Migração de folha de pagamento concluída!")
    print(f"Pagamentos migrados: {migrated_count}")
    print(f"Total no banco: {total_in_db}")
    
    return True

if __name__ == "__main__":
    print("=== MIGRAÇÃO DE FOLHA DE PAGAMENTO ===")
    print("Migrando dados de folha de pagamento do arquivo reformatado para o banco de dados...")
    
    if migrate_pagamentos_to_database():
        print("✅ Migração de folha de pagamento concluída com sucesso!")
    else:
        print("❌ Falha na migração de folha de pagamento!")
        sys.exit(1)
