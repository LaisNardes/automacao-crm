import pandas as pd
import os

caminho_arquivo = os.path.join(os.path.dirname(__file__), "listaMario.xlsx")
tabela = pd.read_excel(caminho_arquivo)
