import os
from sqlalchemy import create_engine, Column, String, Integer, inspect
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.environ.get("DATABASE_URL")

if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Se não houver URL, ele avisa no log em vez de falhar silenciosamente
if not DATABASE_URL:
    print("AVISO: DATABASE_URL não encontrada. A tabela NÃO será criada no Render.")
    engine = create_engine("sqlite:///local.db")
else:
    print("CONECTANDO AO BANCO DE DADOS...")
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
    produtos = db.query(Produto).order_by(Produto.id.desc()).all()
    # Incluímos o ID aqui para o botão de lixeira saber quem ele é
    lista = [{"id": p.id, "nome": p.nome, "desc": p.desc, "preco": p.preco, "imagem": p.imagem} for p in produtos]
    db.close()
    return lista

def salvar_novo_produto(nome, desc, preco, imagem):
    db = SessionLocal()
    novo_p = Produto(nome=nome, desc=desc, preco=preco, imagem=imagem)
    db.add(novo_p)
    db.commit()
    db.close()

def deletar_produto_db(produto_id):
    db = SessionLocal()
    try:
        # Busca direta pela chave primária (muito mais rápido e seguro)
        produto = db.query(Produto).filter(Produto.id == produto_id).first()
        
        if produto:
            db.delete(produto)
            db.commit()
            print(f"SUCESSO: Produto ID {produto_id} deletado.")
    except Exception as e:
        db.rollback()
        print(f"ERRO: {e}")
    finally:
        db.close()
