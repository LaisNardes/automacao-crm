from flask import Flask, render_template, request, jsonify
from processador_items import obter_itens_filtrados, processar_lista_itens
import threading
from automacao_crm import processar_resultados_json
import json

app = Flask(__name__)

automacao_log = []
automacao_em_andamento = False
automacao_concluida = False

RESULTADOS_JSON_PATH = 'resultados.json' 

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/processar', methods=['POST'])
def processar():
    codigo_veiculo = request.form.get('codigo')
    if not codigo_veiculo:
        return jsonify({'error': 'Código del vehículo no proporcionado'})

    try:
        itens_com_oem, itens_sem_oem = obter_itens_filtrados(codigo_veiculo)
        return jsonify({
            'success': True,
            'message': 'Artículos cargados correctamente.',
            'itens_com_oem': itens_com_oem,
            'itens_sem_oem': itens_sem_oem
        })
    except Exception as e:
        return jsonify({'error': f'Error al cargar artículos: {str(e)}'})

@app.route('/processar_itens_editados', methods=['POST'])
def processar_itens_editados():
    data = request.get_json()
    itens_editados = data.get('itens_editados', [])
    itens_com_oem = data.get('itens_com_oem', [])

    if not itens_editados and not itens_com_oem:
        return jsonify({'error': 'Ningún artículo para procesar recibido'})

    todos_itens = itens_editados + itens_com_oem

    try:
        resultado = processar_lista_itens(todos_itens)
        return jsonify({
            'success': True,
            'message': 'Procesamiento concluido! Archivo resultados.json generado.',
            'sucesso': resultado['sucesso'],
            'erro': resultado['erro'],
            'total_sucesso': len(resultado['sucesso']),
            'total_erro': len(resultado['erro']),
            'pode_automatizar': len(resultado['sucesso']) > 0
        })
    except Exception as e:
        return jsonify({'error': f'Error en el procesamiento: {str(e)}'})

@app.route('/atualizar-json', methods=['POST'])
def atualizar_json():
    data = request.get_json()
    itens_atualizados = data.get('itens', [])

    if not isinstance(itens_atualizados, list):
        return jsonify({'error': 'Formato inválido de los artículos'})

    try:
        with open(RESULTADOS_JSON_PATH, 'w', encoding='utf-8') as f:
            json.dump(itens_atualizados, f, ensure_ascii=False, indent=4)
        return jsonify({'success': True, 'message': 'JSON actualizado correctamente.'})
    except Exception as e:
        return jsonify({'error': f'Error al guardar JSON: {str(e)}'})

@app.route('/iniciar-automacao', methods=['POST'])
def iniciar_automacao():
    global automacao_em_andamento, automacao_concluida, automacao_log

    if automacao_em_andamento:
        return jsonify({'error': 'Ya existe una automatización en curso'})

    try:
        automacao_log.clear()
        automacao_em_andamento = True
        automacao_concluida = False

        def executar_automacao():
            global automacao_em_andamento, automacao_concluida, automacao_log
            try:
                sucesso, log = processar_resultados_json()
                automacao_log = log.split('\n')
                automacao_concluida = True
            except Exception as e:
                automacao_log.append(f"Error en la automatización: {str(e)}")
            finally:
                automacao_em_andamento = False

        thread = threading.Thread(target=executar_automacao)
        thread.daemon = True
        thread.start()

        return jsonify({'success': True, 'message': 'Automatización iniciada en segundo plano. Espera la conclusión.'})
    except Exception as e:
        automacao_em_andamento = False
        return jsonify({'error': f'Error al iniciar automatización: {str(e)}'})

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