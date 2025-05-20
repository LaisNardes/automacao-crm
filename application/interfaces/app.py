from flask import Flask, render_template, request, jsonify
from processador_items import processar_items_veiculo
import threading
import time
import os

app = Flask(__name__)

# Variável global para armazenar o log da automação em andamento
automacao_log = []
automacao_em_andamento = False
automacao_concluida = False

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/processar', methods=['POST'])
def processar():
    codigo_veiculo = request.form.get('codigo')
    if not codigo_veiculo:
        return jsonify({'error': 'Código do veículo não fornecido'})

    try:
        resultado = processar_items_veiculo(codigo_veiculo)
        if resultado is None:
            return jsonify({'error': 'Erro no processamento: Nenhum resultado encontrado'})

        return jsonify({
            'success': True,
            'message': f'Processamento concluído! Arquivo resultados.json gerado.',
            'sucesso': resultado['sucesso'],
            'erro': resultado['erro'],
            'total_sucesso': len(resultado['sucesso']),
            'total_erro': len(resultado['erro']),
            'pode_automatizar': len(resultado['sucesso']) > 0
        })
    except Exception as e:
        return jsonify({
            'error': f'Erro no processamento: {str(e)}'
        })

@app.route('/iniciar-automacao', methods=['POST'])
def iniciar_automacao():
    global automacao_em_andamento, automacao_concluida, automacao_log

    if automacao_em_andamento:
        return jsonify({
            'error': 'Já existe uma automação em andamento'
        })

    try:
        # Limpar logs anteriores
        automacao_log = []
        automacao_em_andamento = True
        automacao_concluida = False

        # Importar a função de automação
        from automacao_crm import processar_resultados_json

        # Executar em um thread separado
        def executar_automacao():
            global automacao_em_andamento, automacao_concluida, automacao_log
            try:
                sucesso, log = processar_resultados_json()
                automacao_log = log.split('\n')
                automacao_concluida = True
            except Exception as e:
                automacao_log.append(f"Erro na automação: {str(e)}")
            finally:
                automacao_em_andamento = False

        thread = threading.Thread(target=executar_automacao)
        thread.daemon = True
        thread.start()

        return jsonify({
            'success': True,
            'message': 'Automação iniciada em segundo plano. Aguarde a conclusão.'
        })
    except Exception as e:
        automacao_em_andamento = False
        return jsonify({
            'error': f'Erro ao iniciar automação: {str(e)}'
        })

@app.route('/status-automacao', methods=['GET'])
def status_automacao():
    global automacao_em_andamento, automacao_concluida, automacao_log

    return jsonify({
        'em_andamento': automacao_em_andamento,
        'concluida': automacao_concluida,
        'log': automacao_log
    })

if __name__ == '__main__':
    app.run(debug=True)