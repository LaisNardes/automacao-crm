import json
import time
import os
import pyautogui
from web_scraper import buscar_produtos

def executar_automacao_para_item(item, log_list=None):
    """Executa a automação para um único item do JSON"""
    def log(msg):
        if log_list is not None:
            log_list.append(msg)
        print(msg)

    log(f"\n{'='*50}")
    log(f"Processando item: {item['Código']} - {item['Descripción']}")
    log(f"{'='*50}")

    # Tempo para preparar a tela do CRM
    time.sleep(2)

    # --- CONFIGURAÇÕES GERAIS ---
    pyautogui.PAUSE = 0.5

    # Clicar no campo Almacenada
    log("Clicando no campo Almacenada...")
    pyautogui.click(x=1029, y=610)

    # Clicar no campo buscar en todo
    log("Clicando no campo buscar en todo...")
    pyautogui.click(x=610, y=605)

    # Usar o código do item como termo de busca
    termo_busca = item['Código']
    log(f"Buscando pelo código: {termo_busca}")
    pyautogui.write(str(termo_busca))
    pyautogui.press("enter")

    # Aguardar carregamento dos resultados
    log("Aguardando carregamento dos resultados...")
    time.sleep(1)

    # Clicar no resultado
    log("Clicando no resultado...")
    pyautogui.doubleClick(x=781, y=761)

    # Aguardar abertura do item
    time.sleep(2)

    # Clicar no campo de preço
    log("Clicando no campo de preço...")
    pyautogui.doubleClick(x=904, y=970)

    # Limpar o campo
    pyautogui.press("backspace")
    time.sleep(1)

    # Verificar se já temos o resultado do scraping no item
    if 'resultado_scraping' in item and item['resultado_scraping']:
        try:
            # Usar o preço já obtido no processamento anterior
            preco = item['resultado_scraping'][0]['preco']
            log(f"Inserindo preço: {preco}")
            pyautogui.write(str(preco))
        except (KeyError, IndexError) as e:
            log(f"Erro ao obter preço do item: {e}")
            # Tentar buscar novamente se não conseguir usar o preço existente
            if item['OEM'] and item['OEM'] != 'nan':
                termo_busca = item['OEM']
            else:
                termo_busca = f"{item['Descripción']} {item['Marca']} {item['Modelo_Limpo']}"

            log(f"Buscando preço para: {termo_busca}")
            resultado = buscar_produtos(termo_busca)

            if resultado:
                try:
                    data = json.loads(resultado)
                    if data and len(data) > 0:
                        preco = data[0]['preco']
                        log(f"Inserindo preço encontrado: {preco}")
                        pyautogui.write(str(preco))
                    else:
                        log("Nenhum preço encontrado na nova busca.")
                except Exception as e:
                    log(f"Erro ao processar resultado da nova busca: {e}")
    else:
        log("Item não possui resultado de scraping. Buscando...")
        # Buscar o preço usando o OEM ou descrição + marca + modelo
        if item['OEM'] and item['OEM'] != 'nan':
            termo_busca = item['OEM']
        else:
            termo_busca = f"{item['Descripción']} {item['Marca']} {item['Modelo_Limpo']}"

        log(f"Buscando preço para: {termo_busca}")
        resultado = buscar_produtos(termo_busca)

        if resultado:
            try:
                data = json.loads(resultado)
                if data and len(data) > 0:
                    preco = data[0]['preco']
                    log(f"Inserindo preço encontrado: {preco}")
                    pyautogui.write(str(preco))
                else:
                    log("Nenhum preço encontrado.")
            except Exception as e:
                log(f"Erro ao processar resultado: {e}")

    # Finalizar a edição
    log("Finalizando edição...")
    pyautogui.press("esc")
    time.sleep(0.5)
    pyautogui.press("enter")

    # Aguardar 5 segundos antes do próximo item
    log(f"Item {item['Código']} processado com sucesso!")
    log(f"{'='*50}")
    log(f"Aguardando 5 segundos antes do próximo item...")
    time.sleep(5)  # Aumentado para 5 segundos conforme solicitado

def processar_resultados_json(arquivo='resultados.json'):
    """Processa todos os itens do arquivo resultados.json"""
    # Lista para armazenar o log
    log_list = []

    def log(msg):
        log_list.append(msg)
        print(msg)

    # Verificar se o arquivo existe
    if not os.path.exists(arquivo):
        log(f"Arquivo {arquivo} não encontrado!")
        return False, "\n".join(log_list)

    try:
        # Ler o arquivo JSON
        with open(arquivo, 'r', encoding='utf-8') as f:
            dados = json.load(f)

        if not dados or len(dados) == 0:
            log(f"Arquivo {arquivo} está vazio!")
            return False, "\n".join(log_list)

        log(f"Encontrados {len(dados)} itens para processar.")

        # Aviso para o usuário preparar o CRM, sem necessidade de input
        log("\nPREPARE O CRM NA TELA CORRETA. A automação iniciará em 10 segundos...")
        time.sleep(10)  # Dá tempo para o usuário preparar a tela

        # Executar a automação para cada item automaticamente
        for i, item in enumerate(dados, 1):
            log(f"\nProcessando item {i}/{len(dados)}")
            executar_automacao_para_item(item, log_list)
            # Não há mais input entre os itens

        log("\nAutomação concluída para todos os itens processados!")

        # Salvar o log em um arquivo
        with open("log_automacao.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(log_list))

        return True, "\n".join(log_list)

    except json.JSONDecodeError:
        log(f"Erro ao ler o arquivo {arquivo}. Formato JSON inválido.")
        return False, "\n".join(log_list)
    except Exception as e:
        log(f"Erro inesperado: {e}")
        return False, "\n".join(log_list)

if __name__ == "__main__":
    sucesso, log = processar_resultados_json()
    print(f"Automação finalizada com sucesso: {sucesso}")