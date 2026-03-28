import subprocess
import sys
import os

# Nome do seu arquivo de servidor (ajuste se for outro nome)
NOME_ARQUIVO = "servidor.py" 

print(f"--- Iniciando Depurador para {NOME_ARQUIVO} ---")

try:
    # Executa o seu servidor como um processo separado
    # Isso garante que o erro do Flet não feche este terminal
    resultado = subprocess.run(
        [sys.executable, NOME_ARQUIVO],
        check=True,
        text=True
    )
except subprocess.CalledProcessError as e:
    print("\n" + "!"*60)
    print("ERRO CRÍTICO ENCONTRADO NO SEU CÓDIGO FLET:")
    print("!"*60 + "\n")
    # O erro detalhado aparecerá aqui no terminal
except Exception as e:
    print(f"Erro ao tentar executar o arquivo: {e}")

print("\n" + "="*60)
print("O PROCESSO FOI ENCERRADO.")
print("Analise o erro acima antes de fechar.")
print("="*60)

# O segredo para a janela não fechar:
input("\nPressione ENTER para sair...")