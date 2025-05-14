import base64
import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import re

def gerar_url_busca(url_base, termo_pesquisa):
    termo_b64 = base64.b64encode(termo_pesquisa.replace(" ", "*").encode('utf-8')).decode('utf-8')
    url = re.sub(r'(txbu=)[^&]*', r'\1' + termo_b64, url_base)
    url = re.sub(r'(tebu=)[^&]*', r'\1' + termo_b64, url)
    return url

def filtrar_por_media_ou_menor(produtos, tolerancia=0.3):
    precos = [p['preco'] for p in produtos]
    media = sum(precos) / len(precos)
    # Verifica se algum preço está fora da faixa de tolerância
    fora = [p for p in produtos if abs(p['preco'] - media) / media > tolerancia]
    if fora:
        # Retorna apenas o produto mais próximo da média
        mais_proximo = min(produtos, key=lambda p: abs(p['preco'] - media))
        print("\nValor médio selecionado devido à diferença significativa:")
        print(json.dumps(mais_proximo, ensure_ascii=False, indent=2))
        return [mais_proximo]
    else:
        # Retorna apenas o menor preço
        menor = min(produtos, key=lambda p: p['preco'])
        print("\nMenor valor selecionado (sem diferença significativa):")
        print(json.dumps(menor, ensure_ascii=False, indent=2))
        return [menor]

def buscar_produtos(termo_pesquisa):
    url_base = "https://ecooparts.com/recambios-automovil-segunda-mano/?pag=pro&busval=fGZhcm8qaXpxdWVyZG98bmluZ3Vub3xwcm9kdWN0b3wtMXwwfDB8MHwwfHwwfDB8MHww&filval=&panu=MQ==&tebu=ZmFybyppenF1ZXJkbw==&ord=bmluZ3Vubw==&valo=LTE=&ubic=&toen=c3pic2t1Nm4wZ2F1dmd1cjVmb2Nr&veid=MA==&qregx=MzA=&tmin=MQ==&ttseu=&txbu=ZmFybyBpenF1ZXJkbw==&ivevh=&ivevhmat=&ivevhsel=&ivevhcsver=&ivevhse=&oem=&vin="
    url = gerar_url_busca(url_base, termo_pesquisa)
    print("URL gerada:", url)

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")

    driver = webdriver.Chrome(options=chrome_options)

    try:
        driver.get(url)
        wait = WebDriverWait(driver, 20)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".products-list__item")))
        time.sleep(2)

        soup = BeautifulSoup(driver.page_source, "html.parser")
        produtos = []
        items = soup.select('.products-list__item')
        for item in items:
            nome_tag = item.select_one('.product-card__name a')
            nome = nome_tag.get_text(strip=True) if nome_tag else None

            preco_tag = item.select_one('.product-card__prices .product-card__price')
            if preco_tag:
                preco_str = preco_tag.get_text(strip=True).replace('€', '').replace('.', '').replace(',', '.')
                try:
                    preco = float(preco_str)
                except ValueError:
                    preco = None
            else:
                preco = None

            if nome and preco is not None:
                produtos.append({'nome': nome, 'preco': preco})

        produtos_ordenados = sorted(produtos, key=lambda x: x['preco'])[:4]

        # Aplica a filtragem pela média ou menor preço
        produtos_filtrados = filtrar_por_media_ou_menor(produtos_ordenados)

        return json.dumps(produtos_filtrados, ensure_ascii=False, indent=2)

    finally:
        driver.quit()

if __name__ == "__main__":
    termo = "faro izquierdo"
    resultado = buscar_produtos(termo)
    print("\nResultado finalaaaaa:")
    print(resultado)