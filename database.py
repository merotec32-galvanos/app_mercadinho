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
    try:
        # Busca o produto ignorando espaços em branco extras
        produto = db.query(Produto).filter(
            Produto.nome == nome.strip(), 
            Produto.preco == preco.strip()
        ).first()
        
        if produto:
            db.delete(produto)
            db.commit()
            print(f"SUCESSO: {nome} deletado do banco real.")
        else:
            print(f"AVISO: Produto {nome} com preço {preco} não encontrado.")
    except Exception as e:
        db.rollback()
        print(f"ERRO AO DELETAR: {e}")
    finally:
        db.close()
