#!/usr/bin/env python3
import os
import sys
from pathlib import Path
import bcrypt

# Adicionar o diretório atual ao path
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

from src.models.user import db, User
from main import app

def create_default_users():
    """Criar usuários padrão do sistema"""
    
    with app.app_context():
        # Criar tabelas se não existirem
        db.create_all()
        
        # Usuários padrão
        users_data = [
            {
                'username': 'rabeloce',
                'email': 'antonio@rabelo.com',
                'password': 'rabeloce',
                'is_admin': True
            },
            {
                'username': 'darvince',
                'email': 'darvin@rabelo.com', 
                'password': 'darvince',
                'is_admin': True
            },
            {
                'username': 'luciace',
                'email': 'lucia@rabelo.com',
                'password': 'luciace',
                'is_admin': True
            },
            {
                'username': 'admin',
                'email': 'admin@rabelo.com',
                'password': 'admin',
                'is_admin': True
            }
        ]
        
        for user_data in users_data:
            # Verificar se usuário já existe
            existing_user = User.query.filter_by(username=user_data['username']).first()
            
            if not existing_user:
                # Criptografar senha
                hashed_password = bcrypt.hashpw(
                    user_data['password'].encode('utf-8'), 
                    bcrypt.gensalt()
                )
                
                # Criar novo usuário
                new_user = User(
                    username=user_data['username'],
                    email=user_data['email'],
                    password_hash=hashed_password.decode('utf-8'),
                    is_admin=user_data['is_admin']
                )
                
                db.session.add(new_user)
                print(f"✅ Usuário criado: {user_data['username']}")
            else:
                print(f"⚠️  Usuário já existe: {user_data['username']}")
        
        # Salvar alterações
        db.session.commit()
        print("\n🎉 Usuários criados com sucesso!")
        
        # Listar usuários
        print("\n📋 Usuários disponíveis:")
        all_users = User.query.all()
        for user in all_users:
            print(f"   - {user.username} ({user.email}) - Admin: {user.is_admin}")

if __name__ == '__main__':
    print("🔧 Criando usuários padrão...")
    create_default_users()