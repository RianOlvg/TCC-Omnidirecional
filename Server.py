from flask import Flask, jsonify, request
import pandas as pd
import keyboard

# Variáveis globais
global duty_cicle
global ligado
global dados_velocidade
count = 0
dados_velocidade = {"velocidade Motor A": [],
                    "velocidade Motor B": [],
                    "velocidade Motor C": [],
                    "velocidade Motor D": [],
                    "duty": [],
}
ligado = 1
duty_cicle = 650
comando = "parado"

teclas = set()

# Função que trata as teclas pressionadas
def teclas_pressionadas(e):
    global comando
    if e.event_type == keyboard.KEY_DOWN:
        teclas.add(e.name)
    # Verifica as teclas pressionadas
    if 'w' in teclas:
        comando = "avança"
    if 's' in teclas:
        comando = "recua"
    if 'd' in teclas:
        comando = "direita"
    if 'a' in teclas:
        comando = "esquerda"
    if 'e' in teclas:
        comando = "135 graus"
    if 'z' in teclas:
        comando = "315 graus"
    if 'x' in teclas:
        comando = "225 graus"
    if 'q' in teclas:
        comando = "45 graus"
    if "j" in teclas:
        comando = "anti horario"
    if "h" in teclas:
        comando = "horario"
    if "o" in teclas:
        comando = "octogono"
    if "H" in teclas:
        comando = "hexadecagono"
    if teclas.__len__() == 0:
        comando = "parado"
    if e.event_type == keyboard.KEY_UP:
        teclas.discard(e.name)
    if not teclas:
        comando = "parado"
    print(comando)

keyboard.hook(teclas_pressionadas)

# Inicialização do servidor Flask
app = Flask(__name__)

# Rota principal
@app.route('/', methods=['POST'])
def index():
    return "Bem-vindo Dispositivo MicroPython"

# Rota para teste
@app.route('/teste', methods=['POST'])
def teste_request():
    global duty_cicle
    global dados_velocidade
    global count

    data_run = request.get_json(force=True)
    count += 1
    dados_velocidade["velocidade Motor A"].append(data_run["velMotorA"])
    dados_velocidade["velocidade Motor B"].append(data_run["velMotorB"])
    dados_velocidade["velocidade Motor C"].append(data_run["velMotorC"])
    dados_velocidade["velocidade Motor D"].append(data_run["velMotorD"])
    dados_velocidade["duty"].append(duty_cicle)

    if count >= 10:
        count = 0
        duty_cicle += 10

    if duty_cicle >= 1020:
        duty_cicle = 0
        dataframeVelocidade = pd.DataFrame(dados_velocidade)
        dataframeVelocidade.to_excel("")  # Caminho do arquivo Excel

    return jsonify({"duty": duty_cicle, "ligado": 1})

# Rota para comandos manuais
@app.route('/manual', methods=['POST'])
def manual_commands():
    return comando

# Executa o servidor Flask
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)


    

   