import json
import os

ARQUIVO_DADOS = "estoque_mercadinho.json"

def carregar_dados():
    if os.path.exists(ARQUIVO_DADOS):
        with open(ARQUIVO_DADOS, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def salvar_dados(lista):
    with open(ARQUIVO_DADOS, "w", encoding="utf-8") as f:
        json.dump(lista, f, indent=4, ensure_ascii=False)
