import pyautogui
import time
import os
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.edge.service import Service as EdgeService
from webdriver_manager.microsoft import EdgeChromiumDriverManager

# Tempo para abrir o CRM 
time.sleep(5) 

# --- CONFIGURAÇÕES GERAIS ---
pyautogui.PAUSE = 0.5

#clicar no campo Almacenada
pyautogui.click(x=1029, y=610) 

#clicar no campo buscar en todo
pyautogui.click(x=610, y=605)


#entraria a condiçao de colar o nome do item ou o OEM vindo do resultado da pesquisa
pyautogui.write("9635254180") 

#duplo click no produto selecionado
pyautogui.doubleClick(x=781, y=761)

#clicar no campo de preco
pyautogui.doubleClick(x=905, y=970)
#colar o resultado de preço puxando o resultado do que veio do webscrapping

#clicar em fechar ou salvar
pyautogui.press("esc")
#clicar no prompt aceitar
pyautogui.press("enter")