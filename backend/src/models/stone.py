from src.models.user import db

class Stone(db.Model):
    __tablename__ = 'stone'
    
    id = db.Column(db.Integer, primary_key=True)
    idpe = db.Column(db.Integer, unique=True, nullable=False)  # ID original do sistema antigo
    idpeimp = db.Column(db.Float)
    foto = db.Column(db.String(255))
    tipo_pedra = db.Column(db.String(100))  # redondo, oval, rústico, etc.
    lapidacao_pedra = db.Column(db.String(100))  # cabochão, natural, etc.
    material_pedra = db.Column(db.String(100))  # sodalita, amazonita, quartzo, etc.
    cor_pedra = db.Column(db.String(100))
    comprimento_pedra = db.Column(db.Float, default=0.0)  # em mm
    largura_pedra = db.Column(db.Float, default=0.0)      # em mm
    altura_pedra = db.Column(db.Float, default=0.0)       # em mm
    peso_pedra = db.Column(db.Float, default=0.0)
    preco_pedra = db.Column(db.Float, default=0.0)
    noticia = db.Column(db.Text)
    status_estoque = db.Column(db.String(100))
    qmin = db.Column(db.Float, default=0.0)
    nasjoias = db.Column(db.Integer, default=0)  # Quantidade em joias
    webexport = db.Column(db.Boolean, default=False)
    exportiert = db.Column(db.String(50))
    
    # Campos de compatibilidade com sistema antigo
    tipo = db.Column(db.String(100))  # redondo, oval, rústico, etc.
    lapidacao = db.Column(db.String(100))  # cabochão, natural, etc.
    material = db.Column(db.String(100))  # sodalita, amazonita, quartzo, etc.
    cor = db.Column(db.String(100))
    comprimento = db.Column(db.Float, default=0.0)  # em mm
    largura = db.Column(db.Float, default=0.0)      # em mm
    altura = db.Column(db.Float, default=0.0)       # em mm
    peso = db.Column(db.Float, default=0.0)
    tempo = db.Column(db.Float, default=0.0)        # Tempo de processamento
    preco = db.Column(db.Float, default=0.0)
    ststoque = db.Column(db.String(100))
    
    def __repr__(self):
        return f'<Stone {self.idpe}: {self.material} {self.cor}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'idpe': self.idpe,
            'idpeimp': self.idpeimp,
            'foto': self.foto,
            'tipo': self.tipo,
            'lapidacao': self.lapidacao,
            'material': self.material,
            'cor': self.cor,
            'comprimento': self.comprimento,
            'largura': self.largura,
            'altura': self.altura,
            'peso': self.peso,
            'tempo': self.tempo,
            'preco': self.preco,
            'noticia': self.noticia,
            'ststoque': self.ststoque,
            'qmin': self.qmin,
            'nasjoias': self.nasjoias,
            'webexport': self.webexport,
            'exportiert': self.exportiert
        }
    
    @property
    def dimensoes_formatadas(self):
        """Retorna as dimensões formatadas"""
        dimensoes = []
        if self.comprimento and self.comprimento > 0:
            dimensoes.append(f"{self.comprimento}")
        if self.largura and self.largura > 0:
            dimensoes.append(f"{self.largura}")
        if self.altura and self.altura > 0:
            dimensoes.append(f"{self.altura}")
        
        return " x ".join(dimensoes) + " mm" if dimensoes else "N/A"
    
    @property
    def descricao_completa(self):
        """Retorna uma descrição completa da pedra"""
        partes = []
        if self.material:
            partes.append(self.material.title())
        if self.cor:
            partes.append(self.cor.title())
        if self.lapidacao:
            partes.append(f"({self.lapidacao})")
        if self.tipo:
            partes.append(f"- {self.tipo}")
        
        return " ".join(partes) if partes else f"Pedra {self.idpe}"


    
    def __repr__(self):
        material = self.material_pedra or self.material or 'Unknown'
        cor = self.cor_pedra or self.cor or 'Unknown'
        return f'<Stone {self.idpe}: {material} {cor}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'idpe': self.idpe,
            'idpeimp': self.idpeimp,
            'foto': self.foto,
            'tipo_pedra': self.tipo_pedra,
            'lapidacao_pedra': self.lapidacao_pedra,
            'material_pedra': self.material_pedra,
            'cor_pedra': self.cor_pedra,
            'comprimento_pedra': self.comprimento_pedra,
            'largura_pedra': self.largura_pedra,
            'altura_pedra': self.altura_pedra,
            'peso_pedra': self.peso_pedra,
            'preco_pedra': self.preco_pedra,
            'noticia': self.noticia,
            'status_estoque': self.status_estoque,
            'qmin': self.qmin,
            'nasjoias': self.nasjoias,
            'webexport': self.webexport,
            'exportiert': self.exportiert,
            # Campos de compatibilidade
            'tipo': self.tipo,
            'lapidacao': self.lapidacao,
            'material': self.material,
            'cor': self.cor,
            'comprimento': self.comprimento,
            'largura': self.largura,
            'altura': self.altura,
            'peso': self.peso,
            'tempo': self.tempo,
            'preco': self.preco,
            'ststoque': self.ststoque
        }
    
    @property
    def dimensoes_formatadas(self):
        """Retorna as dimensões formatadas"""
        comp = self.comprimento_pedra or self.comprimento or 0
        larg = self.largura_pedra or self.largura or 0
        alt = self.altura_pedra or self.altura or 0
        
        dimensoes = []
        if comp and comp > 0:
            dimensoes.append(f"{comp}")
        if larg and larg > 0:
            dimensoes.append(f"{larg}")
        if alt and alt > 0:
            dimensoes.append(f"{alt}")
        
        return " x ".join(dimensoes) + " mm" if dimensoes else "N/A"
    
    @property
    def descricao_completa(self):
        """Retorna uma descrição completa da pedra"""
        material = self.material_pedra or self.material
        cor = self.cor_pedra or self.cor
        lapidacao = self.lapidacao_pedra or self.lapidacao
        tipo = self.tipo_pedra or self.tipo
        
        partes = []
        if material:
            partes.append(material.title())
        if cor:
            partes.append(cor.title())
        if lapidacao:
            partes.append(f"({lapidacao})")
        if tipo:
            partes.append(f"- {tipo}")
        
        return " ".join(partes) if partes else f"Pedra {self.idpe}"

