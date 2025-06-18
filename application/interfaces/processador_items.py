import pandas as pd
import json
from web_scraper import buscar_produtos
import time
import re

def limpar_modelo(modelo):
    """Remove texto após o primeiro parêntese e retorna o número do modelo."""
    return re.split(r'\s*\(', modelo)[0].strip()

def obter_itens_filtrados(codigo_veiculo):
    """
    Lê o Excel e retorna duas listas de itens com PVP IVA=0 e código veículo:
    - itens_com_oem: itens que possuem OEM
    - itens_sem_oem: itens que não possuem OEM
    """
    try:
        df = pd.read_excel('listaMario.xlsx')
        df['Código vehículo'] = df['Código vehículo'].astype(str)
        filtered_df = df[df['Código vehículo'].str.contains(codigo_veiculo, na=False)]
        filtered_df['PVP IVA'] = pd.to_numeric(filtered_df['PVP IVA'], errors='coerce')
        zero_pvp = filtered_df[filtered_df['PVP IVA'] == 0]

        itens_com_oem = []
        itens_sem_oem = []

        for _, row in zero_pvp.iterrows():
            item = {
                'Código': str(row['Código']),
                'Descripción': str(row['Descripción']),
                'OEM': str(row['OEM']).replace('.0', '') if pd.notna(row['OEM']) else None,
                'PVP IVA': float(row['PVP IVA']),
                'Marca': str(row['Marca']),
                'Modelo': str(row['Modelo']),
                'Modelo_Limpo': limpar_modelo(str(row['Modelo'])),
                'Código vehículo': str(row['Código vehículo']).strip()
            }
            if item['OEM'] and item['OEM'].lower() != 'nan':
                itens_com_oem.append(item)
            else:
                itens_sem_oem.append(item)

        return itens_com_oem, itens_sem_oem

    except Exception as e:
        print(f"Erro ao obter itens filtrados: {e}")
        return [], []

def processar_lista_itens(itens_para_processar):
    """
    Processa a lista de itens (faz scraping) e retorna dicionário com sucesso e erro.
    """
    resultados_sucesso = []
    resultados_erro = []

    for idx, item in enumerate(itens_para_processar, 1):
        print(f"\nProcessando item {idx}/{len(itens_para_processar)}")
        print(f"Descripción: {item['Descripción']}")

        try:
            if item.get('OEM') and item['OEM'].lower() != 'nan':
                print(f"Pesquisando por OEM: {item['OEM']}")
                resultado = buscar_produtos(item['OEM'])
            else:
                descricao_editada = item.get('Descripción', '').strip()
                termo_pesquisa = f"{descricao_editada}".strip()
                print(f"Pesquisando por Descrição editada: {termo_pesquisa}")
                resultado = buscar_produtos(termo_pesquisa)

            if resultado:
                resultado_dict = json.loads(resultado)
                if resultado_dict and len(resultado_dict) > 0:
                    primeiro_resultado = resultado_dict[0]
                    preco = primeiro_resultado.get('preco', 'Preço não encontrado')
                    link = primeiro_resultado.get('link', '')  # <-- PEGA O LINK DO RESULTADO
                    item['preco_scraping'] = preco
                    item['resultado_scraping'] = resultado_dict
                    item['link_scraping'] = link  # <-- ADICIONA O LINK AO ITEM
                    resultados_sucesso.append(item)
                    print(f"✓ Produto encontrado e processado com sucesso - Preço: {preco}")
                else:
                    item['motivo_erro'] = "Nenhum resultado encontrado"
                    resultados_erro.append(item)
                    print("✗ Nenhum resultado encontrado")
            else:
                item['motivo_erro'] = "Busca não retornou resultados"
                resultados_erro.append(item)
                print("✗ Busca não retornou resultados")

            time.sleep(2)

        except Exception as e:
            item['motivo_erro'] = str(e)
            resultados_erro.append(item)
            print(f"✗ Erro ao processar item: {str(e)}")

    # Salvar resultados em JSON
    nome_arquivo = 'resultados.json'
    with open(nome_arquivo, 'w', encoding='utf-8') as f:
        json.dump(resultados_sucesso, f, ensure_ascii=False, indent=2)

    print(f"\nProcessamento concluído!")
    print(f"Total de items processados com sucesso: {len(resultados_sucesso)}")
    print(f"Total de items com erro: {len(resultados_erro)}")
    print(f"Resultados salvos em: {nome_arquivo}")

    return {
        'sucesso': resultados_sucesso,
        'erro': resultados_erro
    }

def processar_items_veiculo(codigo_veiculo):
    """
    Função principal para compatibilidade, que obtém os itens filtrados e processa todos.
    """
    itens_com_oem, itens_sem_oem = obter_itens_filtrados(codigo_veiculo)
    todos_itens = itens_com_oem + itens_sem_oem
    return processar_lista_itens(todos_itens)

if __name__ == "__main__":
    codigo_veiculo = input("Digite o código do veículo: ")
    resultados = processar_items_veiculo(codigo_veiculo)
    if resultados:
        print(f"Sucesso: {len(resultados['sucesso'])} itens")
        print(f"Erro: {len(resultados['erro'])} itens")