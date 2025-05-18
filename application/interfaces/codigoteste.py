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

# Entraria a condição de colar o Código que vem da lista do excel 
termo_busca = "9635254180"  
pyautogui.write(termo_busca)
pyautogui.press("enter")

time.sleep(1)
pyautogui.doubleClick(x=781, y=761)
time.sleep(2)
pyautogui.doubleClick(x=904, y=970)
pyautogui.press("backspace")

time.sleep(1)

resultado = web_scraper.buscar_produtos(termo_busca)


if resultado is not None:
    try:
        
        data = json.loads(resultado)
        
        preco = data[0]['preco']
        
        pyautogui.write(str(preco))
    except (json.JSONDecodeError, KeyError, IndexError) as e:
        print(f"Erro ao processar o resultado: {e}")
else:
    print("Nenhum preço encontrado.")

pyautogui.press("esc")

pyautogui.press("enter")