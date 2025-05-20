import pandas as pd
import json
from web_scraper import buscar_produtos
import time
import re
import os

def limpar_modelo(modelo):
    """Remove todo texto após o primeiro parêntese e retorna apenas o número do modelo."""
    return re.split(r'\s*\(', modelo)[0].strip()

def processar_items_veiculo(codigo_veiculo, iniciar_automacao=False):
    try:
        print(f"Iniciando processamento para código veículo: {codigo_veiculo}")

        # Ler o arquivo Excel
        df = pd.read_excel('listaMario.xlsx')

        # 1. Filtrar itens pelo código veículo
        df['Código vehículo'] = df['Código vehículo'].astype(str)
        filtered_df = df[df['Código vehículo'].str.contains(codigo_veiculo, na=False)]

        # 2. Verificar PVP IVA
        filtered_df['PVP IVA'] = pd.to_numeric(filtered_df['PVP IVA'], errors='coerce')
        zero_pvp = filtered_df[filtered_df['PVP IVA'] == 0]

        # 3. Preparar dados para processamento
        items_para_processar = []
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
            items_para_processar.append(item)

        print(f"\nTotal de items encontrados com código veículo {codigo_veiculo}: {len(filtered_df)}")
        print(f"Items com PVP IVA = 0: {len(items_para_processar)}")

        # 4. Processar cada item
        resultados_sucesso = []
        resultados_erro = []

        for idx, item in enumerate(items_para_processar, 1):
            print(f"\nProcessando item {idx}/{len(items_para_processar)}")
            print(f"Descripción: {item['Descripción']}")

            try:
                if item['OEM'] and item['OEM'] != 'nan':
                    # Pesquisa por OEM
                    print(f"Pesquisando por OEM: {item['OEM']}")
                    resultado = buscar_produtos(item['OEM'])
                else:
                    # Pesquisa por Marca + Modelo + Descrição
                    termo_pesquisa = f"{item['Descripción']} {item['Marca']} {item['Modelo_Limpo']} "
                    print(f"Pesquisando por Marca + Modelo + Descrição: {termo_pesquisa}")
                    resultado = buscar_produtos(termo_pesquisa)

                if resultado:
                    resultado_dict = json.loads(resultado)
                    if resultado_dict and len(resultado_dict) > 0:  # Se encontrou algum resultado
                        item['resultado_scraping'] = resultado_dict
                        resultados_sucesso.append(item)
                        print("✓ Produto encontrado e processado com sucesso")
                    else:
                        item['motivo_erro'] = "Nenhum resultado encontrado"
                        resultados_erro.append(item)
                        print("✗ Nenhum resultado encontrado")
                else:
                    item['motivo_erro'] = "Busca não retornou resultados"
                    resultados_erro.append(item)
                    print("✗ Busca não retornou resultados")

                # Aguarda um pouco entre as requisições
                time.sleep(2)

            except Exception as e:
                item['motivo_erro'] = str(e)
                resultados_erro.append(item)
                print(f"✗ Erro ao processar item: {str(e)}")

        # Salvar resultados em um arquivo JSON
        nome_arquivo = 'resultados.json'
        with open(nome_arquivo, 'w', encoding='utf-8') as f:
            json.dump(resultados_sucesso, f, ensure_ascii=False, indent=2)

        print(f"\nProcessamento concluído!")
        print(f"Total de items processados com sucesso: {len(resultados_sucesso)}")
        print(f"Total de items com erro: {len(resultados_erro)}")
        print(f"Resultados salvos em: {nome_arquivo}")

        # Iniciar automação se solicitado
        if iniciar_automacao and resultados_sucesso:
            print("\nIniciando automação de cliques...")
            try:
                # Importar o módulo de automação
                from automacao_crm import processar_resultados_json
                processar_resultados_json(nome_arquivo)
            except ImportError:
                print("Módulo de automação não encontrado. Certifique-se de que o arquivo automacao_crm.py existe.")
            except Exception as e:
                print(f"Erro ao iniciar automação: {e}")

        return {
            'sucesso': resultados_sucesso,
            'erro': resultados_erro
        }

    except Exception as e:
        print(f"Erro durante o processamento: {str(e)}")
        return None

# Permite execução direta para testes
if __name__ == "__main__":
    codigo_veiculo = input("Digite o código do veículo: ")  # Aceita input via terminal
    iniciar_auto = input("Iniciar automação após processamento? (s/n): ").lower() == 's'

    resultados = processar_items_veiculo(codigo_veiculo, iniciar_auto)
    if resultados:
        print(f"Sucesso: {len(resultados['sucesso'])} itens")
        print(f"Erro: {len(resultados['erro'])} itens")

        if not iniciar_auto and resultados['sucesso']:
            iniciar_depois = input("\nDeseja iniciar a automação agora? (s/n): ").lower() == 's'
            if iniciar_depois:
                try:
                    from automacao_crm import processar_resultados_json
                    processar_resultados_json()
                except ImportError:
                    print("Módulo de automação não encontrado.")
                except Exception as e:
                    print(f"Erro ao iniciar automação: {e}")