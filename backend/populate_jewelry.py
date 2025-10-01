#!/usr/bin/env python3
"""
Script para popular o banco de dados com joias baseado nas imagens disponíveis
e informações do sistema antigo.
"""
import os
import re
import sys
from main import app, db
from src.models.jewelry import Jewelry
from src.models.pattern import Pattern

def extract_jewelry_ids_from_images():
    """Extrai IDs únicos de joias das imagens disponíveis"""
    images_dir = '../frontend/public/images/joias'
    if not os.path.exists(images_dir):
        print(f"❌ Diretório de imagens não encontrado: {images_dir}")
        return []
    
    jewelry_ids = set()
    pattern = r'joias_foto_(\d+)_\d+\.png'
    
    for filename in os.listdir(images_dir):
        match = re.match(pattern, filename)
        if match:
            jewelry_id = int(match.group(1))
            jewelry_ids.add(jewelry_id)
    
    return sorted(jewelry_ids)

def create_default_patterns():
    """Cria padrões/categorias padrão para as joias"""
    patterns_data = [
        {'name': 'Anéis', 'description': 'Anéis diversos'},
        {'name': 'Colares', 'description': 'Colares e correntes'},
        {'name': 'Brincos', 'description': 'Brincos diversos'},
        {'name': 'Pulseiras', 'description': 'Pulseiras e braceletes'},
        {'name': 'Pingentes', 'description': 'Pingentes diversos'},
        {'name': 'Conjuntos', 'description': 'Conjuntos de joias'},
        {'name': 'Alianças', 'description': 'Alianças de casamento'},
        {'name': 'Diversos', 'description': 'Outros tipos de joias'}
    ]
    
    created_patterns = []
    for pattern_data in patterns_data:
        existing = Pattern.query.filter_by(nome=pattern_data['name']).first()
        if not existing:
            # Ajustar para o modelo Pattern correto
            pattern_obj = {
                'idpa': len(Pattern.query.all()) + 1,  # ID sequencial
                'nome': pattern_data['name'],
                'tipo': pattern_data['name'].lower(),
                'noticia': pattern_data['description'],
                'colecao': 'Padrão'
            }
            pattern = Pattern(**pattern_obj)
            db.session.add(pattern)
            created_patterns.append(pattern_data['name'])
    
    db.session.commit()
    return created_patterns

def determine_jewelry_category(jewelry_id):
    """Determina a categoria da joia baseado no ID (heurística simples)"""
    # Heurística baseada no ID para categorizar
    remainder = jewelry_id % 8
    categories = ['Anéis', 'Colares', 'Brincos', 'Pulseiras', 'Pingentes', 'Conjuntos', 'Alianças', 'Diversos']
    return categories[remainder]

def generate_jewelry_description(jewelry_id, category):
    """Gera descrição básica para a joia"""
    descriptions = {
        'Anéis': [f'Anel modelo {jewelry_id}', f'Anel exclusivo {jewelry_id}', f'Anel premium {jewelry_id}'],
        'Colares': [f'Colar modelo {jewelry_id}', f'Colar elegante {jewelry_id}', f'Corrente {jewelry_id}'],
        'Brincos': [f'Brinco par {jewelry_id}', f'Brincos modelo {jewelry_id}', f'Brincos exclusivos {jewelry_id}'],
        'Pulseiras': [f'Pulseira modelo {jewelry_id}', f'Bracelete {jewelry_id}', f'Pulseira exclusiva {jewelry_id}'],
        'Pingentes': [f'Pingente modelo {jewelry_id}', f'Pingente exclusivo {jewelry_id}', f'Medalha {jewelry_id}'],
        'Conjuntos': [f'Conjunto modelo {jewelry_id}', f'Kit joias {jewelry_id}', f'Conjunto exclusivo {jewelry_id}'],
        'Alianças': [f'Aliança modelo {jewelry_id}', f'Par de alianças {jewelry_id}', f'Aliança exclusiva {jewelry_id}'],
        'Diversos': [f'Joia modelo {jewelry_id}', f'Peça especial {jewelry_id}', f'Joia exclusiva {jewelry_id}']
    }
    
    options = descriptions.get(category, descriptions['Diversos'])
    return options[jewelry_id % len(options)]

def populate_jewelry_database():
    """Popula o banco com joias baseado nas imagens disponíveis"""
    print("🔍 Extraindo IDs das joias das imagens...")
    jewelry_ids = extract_jewelry_ids_from_images()
    print(f"✅ Encontrados {len(jewelry_ids)} IDs únicos de joias")
    
    if not jewelry_ids:
        print("❌ Nenhuma imagem de joia encontrada!")
        return False
    
    print("📁 Criando categorias padrão...")
    created_patterns = create_default_patterns()
    if created_patterns:
        print(f"✅ Categorias criadas: {', '.join(created_patterns)}")
    
    # Buscar padrões criados
    patterns = Pattern.query.all()
    pattern_dict = {p.nome: p for p in patterns}
    
    print("💎 Populando banco com joias...")
    jewelry_created = 0
    jewelry_updated = 0
    
    for jewelry_id in jewelry_ids:
        # Verificar se joia já existe
        existing = Jewelry.query.filter_by(idj=jewelry_id).first()
        
        if existing:
            # Atualizar apenas se não tem foto
            if not existing.foto:
                existing.foto = f'joias_foto_{jewelry_id}_0.png'
                jewelry_updated += 1
            continue
        
        # Determinar categoria e padrão
        category = determine_jewelry_category(jewelry_id)
        pattern = pattern_dict.get(category)
        
        # Criar nova joia
        jewelry = Jewelry(
            idj=jewelry_id,
            idpa=pattern.id if pattern else None,
            foto=f'joias_foto_{jewelry_id}_0.png',
            descricao=generate_jewelry_description(jewelry_id, category),
            noticia=f'Joia {category.lower()} modelo {jewelry_id}',
            escondido=False,
            precomat=150.00 + (jewelry_id % 500),  # Preço base variável
            precoped=50.00 + (jewelry_id % 200),   # Preço pedras variável
            precotem=30.00 + (jewelry_id % 100),   # Preço trabalho variável
            preco0=0.0,
            preco1=0.0,
            preco2=0.0,
            lucro1=1.3,  # 30% de lucro
            lucro2=1.5,  # 50% de lucro
            qmin=1.0,
            precoweb=None,
            webexport=True,
            exportiert='N'
        )
        
        db.session.add(jewelry)
        jewelry_created += 1
        
        # Commit a cada 100 joias para evitar problemas de memória
        if jewelry_created % 100 == 0:
            db.session.commit()
            print(f"💎 {jewelry_created} joias criadas...")
    
    # Commit final
    db.session.commit()
    
    print(f"✅ Processo concluído!")
    print(f"   📝 Joias criadas: {jewelry_created}")
    print(f"   🔄 Joias atualizadas: {jewelry_updated}")
    print(f"   📊 Total de joias no banco: {Jewelry.query.count()}")
    
    return True

if __name__ == '__main__':
    with app.app_context():
        print("🚀 Iniciando população do banco de joias...")
        success = populate_jewelry_database()
        
        if success:
            print("✅ Banco de joias populado com sucesso!")
        else:
            print("❌ Falha ao popular banco de joias!")
            sys.exit(1)