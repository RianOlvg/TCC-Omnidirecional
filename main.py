import machine
from time import sleep
import time
import network
import socket
import json
import os
import socket
import urequests

# Definição dos pinos utilizados
pinos = [15, 13, 12, 2, 14, 4, 27, 5]
encoderApin = 39
encoderBpin = 36
encoderCpin = 34
encoderDpin = 35

# Contadores para os encoders
counter_A = 0
counter_B = 0
counter_C = 0
counter_D = 0

# Configuração dos pinos de leitura dos encoders
def configura_leitura_velocidade_geral():
    PinoEncoderA = machine.Pin(39, machine.Pin.IN, machine.Pin.PULL_DOWN)
    PinoEncoderB = machine.Pin(36, machine.Pin.IN, machine.Pin.PULL_DOWN)
    PinoEncoderC = machine.Pin(34, machine.Pin.IN, machine.Pin.PULL_DOWN)
    PinoEncoderD = machine.Pin(35, machine.Pin.IN, machine.Pin.PULL_DOWN)

    PinoEncoderA.irq(trigger=machine.Pin.IRQ_RISING, handler=pulse_interrupt_A)
    PinoEncoderB.irq(trigger=machine.Pin.IRQ_RISING, handler=pulse_interrupt_B)
    PinoEncoderC.irq(trigger=machine.Pin.IRQ_RISING, handler=pulse_interrupt_C)
    PinoEncoderD.irq(trigger=machine.Pin.IRQ_RISING, handler=pulse_interrupt_D)

# Função para leitura das velocidades dos motores a partir dos encoders
def leitura_velocidade_geral():
    global counter_A, counter_B, counter_C, counter_D

    counter_A = 0
    counter_B = 0
    counter_C = 0
    counter_D = 0

    configura_leitura_velocidade_geral()
    time.sleep(1)

    leituras_vel = {"velMotorA": counter_A * 6,
                    "velMotorB": counter_B * 6,
                    "velMotorC": counter_C * 6,
                    "velMotorD": counter_D * 6}

    return leituras_vel

# Funções de interrupção para os encoders
def pulse_interrupt_A(s):
    global counter_A
    counter_A += 1

def pulse_interrupt_B(s):
    global counter_B
    counter_B += 1

def pulse_interrupt_C(s):
    global counter_C
    counter_C += 1

def pulse_interrupt_D(s):
    global counter_D
    counter_D += 1

# Função para conexão com a rede Wi-Fi
def connect_to_wifi(ssid, password):
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        print("Conectando à rede Wi-Fi...")
        sta_if.active(True)
        while not sta_if.isconnected():
            try:
                print("Tentando se conectar ao Wi-Fi...")
                sta_if.connect(ssid, password)
                while not sta_if.isconnected():
                    pass
            except OSError as e:
                if "Wifi Internal Error" in str(e):
                    print("Erro de conexão Wi-Fi. Tentando novamente...")
                else:
                    raise  # Se não for um erro de conexão Wi-Fi, propague a exceção
            pass

    print("Conectado à rede Wi-Fi:", sta_if.ifconfig())

# Classe representando um motor
class motor():
    def __init__(self, pin1, pin2):
        self.pin_1 = pin1
        self.pin_2 = pin2
        self.pino1 = machine.PWM(machine.Pin(self.pin_1))
        self.pino2 = machine.PWM(machine.Pin(self.pin_2))
        self.pino1.duty(0)
        self.pino2.duty(0)
        self.pwmPin1 = 0
        self.pwmPin2 = 0
        self.pulso = 0

    def rotaciona(self, sentido="horario", duty=1020):
        if sentido == "anti-horario":
            self.pino1.duty(duty)
            self.pino2.duty(0)
        if sentido == "horario":
            self.pino2.duty(duty)
            self.pino1.duty(0)

    def parada(self):
        self.pino2.duty(0)
        self.pino1.duty(0)
        
            
class carrinho():
    
    def __init__(self, motora, motorb, motorc, motord):
        self.motorA = motora
        self.motorB = motorb
        self.motorC = motorc
        self.motorD = motord
        
    def avanca(self):
        # Move todos os motores para a frente (sentido horário)
        self.motorA.rotaciona("horario")
        self.motorB.rotaciona("horario")
        self.motorC.rotaciona("horario")
        self.motorD.rotaciona("horario")
        
    def recua(self):
        # Move todos os motores para trás (sentido anti-horário)
        self.motorA.rotaciona("anti-horario")
        self.motorB.rotaciona("anti-horario")
        self.motorC.rotaciona("anti-horario")
        self.motorD.rotaciona("anti-horario")
         
    def parada_geral(self):
        # Para todos os motores
        self.motorA.parada()
        self.motorB.parada()
        self.motorC.parada()
        self.motorD.parada()
        
    def direita(self):
        # Move o carrinho para a direita
        self.motorA.rotaciona("horario")
        self.motorB.rotaciona("anti-horario")
        self.motorC.rotaciona("horario")
        self.motorD.rotaciona("anti-horário")
    
    def esquerda(self):
        # Move o carrinho para a esquerda
        self.motorA.rotaciona("anti-horario")
        self.motorB.rotaciona("horario")
        self.motorC.rotaciona("anti-horario")
        self.motorD.rotaciona("horario")
        
    def anda135graus(self):
        # Move os motores A e C para frente (sentido horário)
        self.motorA.rotaciona("horario")
        self.motorC.rotaciona("horario")
        
    def anda45graus(self):
        # Move os motores B e D para frente (sentido horário)
        self.motorB.rotaciona("horario")
        self.motorD.rotaciona("horario")
    
    def anda315graus(self):
        # Move os motores A e C para trás (sentido anti-horário)
        self.motorA.rotaciona("anti-horario")
        self.motorC.rotaciona("anti-horário")
        
    def anda225graus(self):
        # Move os motores B e D para trás (sentido anti-horário)
        self.motorB.rotaciona("anti-horario")
        self.motorD.rotaciona("anti-horário")
    
    def octogono(self, tempo=1, tempo_stop=0.5):
        # Realiza uma sequência específica de movimentos formando um octógono
        self.esquerda()
        time.sleep(tempo)
        self.parada_geral()
        time.sleep(tempo_stop)
        self.anda45graus()
        time.sleep(tempo)
        self.parada_geral()
        time.sleep(tempo_stop)
        self.avanca()
        time.sleep(tempo)
        self.parada_geral()
        time.sleep(tempo_stop)
        self.anda135graus()
        time.sleep(tempo)
        self.parada_geral()
        time.sleep(tempo_stop)
        self.direita()
        time.sleep(tempo)
        self.parada_geral()
        time.sleep(tempo_stop)
        self.anda225graus()
        time.sleep(tempo)
        self.parada_geral()
        time.sleep(tempo_stop)
        self.recua()
        time.sleep(tempo)
        self.parada_geral()
        time.sleep(tempo_stop)
        self.anda315graus()
        time.sleep(tempo)
        self.parada_geral()
        time.sleep(tempo_stop)
        
    def rotateHorario(self):
        # Rotaciona os motores no sentido anti-horário
        self.motorA.rotaciona("anti-horario")
        self.motorB.rotaciona("anti-horario")
        self.motorC.rotaciona("horario")
        self.motorD.rotaciona("horario")
        
    def rotateAntiHorario(self):
        # Rotaciona os motores no sentido horário
        self.motorA.rotaciona("horario")
        self.motorB.rotaciona("horario")
        self.motorC.rotaciona("anti-horario")
        self.motorD.rotaciona("anti-horario")
        
    def ligaPares(self, dutyAC, dutyBD, tempoStop=1, tempoRun=1):
        # Liga pares de motores com diferentes velocidades e sentidos
        sentidoAC = "horario" if dutyAC >= 0 else "anti-horario"
        sentidoBD = "horario" if dutyBD >= 0 else "anti-horario"
        
        # Garante que as velocidades não ultrapassem o limite
        dutyAC = abs(dutyAC)
        dutyBD = abs(dutyBD)
        
        self.motorA.rotaciona(sentidoAC, dutyAC)
        self.motorC.rotaciona(sentidoAC, dutyAC)
        self.motorB.rotaciona(sentidoBD, dutyBD)
        
        # Ajusta a velocidade do motor D para evitar ultrapassar o limite máximo
        dutyMotorD = dutyBD + 100
        if dutyMotorD > 1023:
            dutyMotorD = 1023
        self.motorD.rotaciona(sentidoBD, dutyMotorD)
        
        # Aguarda o tempo de execução especificado
        time.sleep(tempoRun)
        
        # Para todos os motores após o tempo de execução
        self.parada_geral()
        
        # Aguarda o tempo de parada especificado
        time.sleep(tempoStop)
        
        
    def hexadecagono(self, tempoStop=0.1, tempoRun=0.5):
    # 23 graus
    self.ligaPares(997, -750, tempoStop, tempoRun)
    # 45 graus
    self.ligaPares(1023, 0, tempoStop, tempoRun)
    # 68 graus
    self.ligaPares(1023, 750, tempoStop, tempoRun)
    # 90 graus
    self.ligaPares(1023, 1023, tempoStop, tempoRun - 0.2)
    # 157 graus
    self.ligaPares(-710, 986, tempoStop, tempoRun)
    # 135 graus
    self.ligaPares(0, 1020, tempoStop, tempoRun)
    # 112 graus
    self.ligaPares(780, 1020, tempoStop, tempoRun)
    # 180 graus
    self.esquerda()
    time.sleep(tempoRun)
    self.parada_geral()
    time.sleep(tempoStop)
    # 203 graus
    self.ligaPares(-986, 780, tempoStop, tempoRun)
    # 225 graus
    self.ligaPares(-1020, 0, tempoStop, tempoRun)
    # 248 graus
    self.ligaPares(-997, -750, tempoStop, tempoRun)
    # 270 graus
    self.ligaPares(-1020, -1020, tempoStop, tempoRun)
    # 292 graus
    self.ligaPares(-750, -997, tempoStop, tempoRun)
    # 315 graus
    self.ligaPares(0, -1023, tempoStop, tempoRun)
    # 337 graus
    self.ligaPares(700, -990, tempoStop, tempoRun)
    # 0 graus
    self.direita()
    time.sleep(tempoRun)
    self.parada_geral()
    time.sleep(tempoStop + 10)

# Inicialização dos motores e do carrinho
motorA = motor(pinos[1], pinos[0])
motorB = motor(pinos[3], pinos[2])
motorC = motor(pinos[4], pinos[5])
motorD = motor(pinos[7], pinos[6])

carro = carrinho(motorA, motorB, motorC, motorD)
carro.parada_geral()  # Garante que o carrinho está parado inicialmente
sleep(1)  # Pausa de 1 segundo para inicialização

# Conexão com a rede Wi-Fi
connect_to_wifi("moto g(7) play 9282", "")

# Loop principal
while True:
    # Faz uma requisição POST para o servidor local que recebe comandos manuais
    response = urequests.post("http://192.168.188.212:8080/manual")
    
    # Executa a ação correspondente ao comando recebido
    if response.text == "parado":
        carro.parada_geral()
    elif response.text == "avança":
        carro.avanca()
    elif response.text == "recua":
        carro.recua()
    elif response.text == "direita":
        carro.direita()
    elif response.text == "esquerda":
        carro.esquerda()
    elif response.text == "45 graus":
        carro.anda45graus()
    elif response.text == "135 graus":
        carro.anda135graus()
    elif response.text == "225 graus":
        carro.anda225graus()
    elif response.text == "315 graus":
        carro.anda315graus()
    elif response.text == "anti horario":
        carro.rotateAntiHorario()
    elif response.text == "horario":
        carro.rotateHorario()
    elif response.text == "octogono":
        carro.octogono()
    elif response.text == "hexadecagono":
        # Ação correspondente ao comando hexadecagono (não implementado no código fornecido)
        pass

  
  
      
  
      
  

  

  
    
    
    








