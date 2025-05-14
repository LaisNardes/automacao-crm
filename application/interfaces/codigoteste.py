# crm_script.py
import pyautogui
import time
import os
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.edge.service import Service as EdgeService
from webdriver_manager.microsoft import EdgeChromiumDriverManager
import json

# Importa o script de web scraping
import web_scraper

# Tempo para abrir o CRM
time.sleep(5)

# --- CONFIGURAÇÕES GERAIS ---
pyautogui.PAUSE = 0.5

# Clicar no campo Almacenada
pyautogui.click(x=1029, y=610)

# Clicar no campo buscar en todo
pyautogui.click(x=610, y=605)

# Entraria a condição de colar o nome do item ou o OEM vindo do resultado da pesquisa
termo_busca = "9635254180"  # Termo de busca
pyautogui.write(termo_busca)
pyautogui.press("enter")

time.sleep(1)
pyautogui.doubleClick(x=781, y=761)
time.sleep(2)
pyautogui.doubleClick(x=904, y=970)
pyautogui.press("backspace")

time.sleep(1)
# Puxar o resultado de preço do web scraping
resultado = web_scraper.buscar_produtos(termo_busca)

# Colar o resultado de preço no campo do CRM
if resultado is not None:
    try:
        # Converte a string JSON para um objeto Python
        data = json.loads(resultado)
        # Extrai o valor do preço do primeiro item da lista
        preco = data[0]['preco']
        # Escreve apenas o valor do preço
        pyautogui.write(str(preco))
    except (json.JSONDecodeError, KeyError, IndexError) as e:
        print(f"Erro ao processar o resultado: {e}")
else:
    print("Nenhum preço encontrado.")

pyautogui.press("esc")

pyautogui.press("enter")