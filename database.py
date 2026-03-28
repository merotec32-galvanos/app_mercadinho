from sqlalchemy import create_engine, Column, String, Integer, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = os.environ.get("DATABASE_URL")

if DATABASE_URL is None:
    # Se ainda estiver vazio, este print aparecerá nos logs do Render para te avisar
    print("ERRO: DATABASE_URL não encontrada. Verifique o vínculo do Environment Group!")
    # URL temporária apenas para o deploy não travar
    DATABASE_URL = "sqlite:///fallback.db" 
else:
    # Correção de prefixo para compatibilidade com SQLAlchemy moderno
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Produto(Base):
    __tablename__ = "produtos"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String)
    desc = Column(String)
    preco = Column(String)
    imagem = Column(String)

# Cria as tabelas se não existirem
Base.metadata.create_all(bind=engine)

def carregar_dados():
    db = SessionLocal()
    # Converte os objetos do banco para o formato de dicionário que seu código já usa
    produtos = db.query(Produto).order_by(Produto.id.desc()).all()
    lista = [{"nome": p.nome, "desc": p.desc, "preco": p.preco, "imagem": p.imagem} for p in produtos]
    db.close()
    return lista

def salvar_novo_produto(nome, desc, preco, imagem):
    db = SessionLocal()
    novo_p = Produto(nome=nome, desc=desc, preco=preco, imagem=imagem)
    db.add(novo_p)
    db.commit()
    db.close()

def deletar_produto_db(nome, preco):
    db = SessionLocal()
    produto = db.query(Produto).filter(Produto.nome == nome, Produto.preco == preco).first()
    if produto:
        db.delete(produto)
        db.commit()
    db.close()
