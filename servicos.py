import serial
from datetime import timedelta
from datetime import datetime
import time
from threading import Thread
from util import Log
import RPi.GPIO as GPIO

from modelos import DadosColetados
from configuracao import Config as config



class ThreadColetaDados(Thread):

    def __init__(self, config):
        Thread.__init__(self)
        self.monitor = Monitor(config)


    def run(self):
        self.monitor.executar()

    def parar(self):
        self.monitor.parar()

    def is_ignicao(self, ignicao):
        self.monitor.is_desligado(ignicao)
    

class Monitor():

    def __init__(self, config):

        self._loop_execucao = True
        self._config = config
        #self._INPUT_PIN = 16
        self._medidores_fluxo = self._config_fluxo(config.medidores_fluxo)
        self._gps = Monitor_gps(config.gps)
        self._tempo_config = config.tempo_captura()
        self._is_desligado = False

    def is_desligado(self, ignicao):
        self._is_desligado = ignicao


    def _config_fluxo(self, monitores_fluxo):
        #GPIO.setmode(GPIO.BOARD)
        lista = []
        for monitor in monitores_fluxo:
            #print('Monitor GPIO: '+str(monitor.gpio))
            fluxo = Monitor_fluxo()
            GPIO.setup(monitor.gpio, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.add_event_detect(monitor.gpio,
                                  GPIO.RISING,
                                  callback=fluxo.pulseCallback,
                                  bouncetime=20)
            lista.append(fluxo)

        #print('tamanho lista fluxo: %s' % len(lista))
        return lista



    def executar(self):
        dados_coletados = None

        tempo_captura = datetime.now() + timedelta(0, self._tempo_config)
        _ignicao_veiculo = True
        while self._loop_execucao:
            
            dados = self._gps.executar()
            #print('dados gps: '+str(dados))
            agora = datetime.now() 
            if agora > tempo_captura and dados != None:
                dados_coletados = DadosColetados()
                dados_coletados.latitude, dados_coletados.longitude, dados_coletados.velocidade, dados_coletados.direcao, dados_coletados.data_hora = dados
                dados_coletados.ignicao_veiculo = _ignicao_veiculo
                
                fluxo1 = self._medidores_fluxo[0]    
                str_fluxo = str(fluxo1.taxa_fluxo()) + ' L/min'
                dados_coletados.fluxo1 = str_fluxo
                ##print('Fluxo 1'+ str(str_fluxo))

                fluxo2 = self._medidores_fluxo[1]
                str_fluxo = str(fluxo2.taxa_fluxo()) + ' L/min'
                dados_coletados.fluxo2 = str_fluxo
                ##print('Fluxo 2: '+str_fluxo)

                if self._is_desligado:
                    dados_coletados.desligamento = True
                    self._loop_execucao = False
                
                dados_coletados.save()
                    
                tempo_captura = datetime.now() +  timedelta(0, self._tempo_config)
                _ignicao_veiculo = False

                
                

    def parar(self):
        self._loop_execucao = False

    def iniciar(self):
        self._loop_execucao = True

class Monitor_gps():

    def __init__(self, gps):
        self._serialPort = serial.Serial(gps.porta, gps.baud, timeout=gps.timeout)                
        self._existe_dados = False
        self._dados_gps = None

    def executar(self):
        try:
            linha_serial = self._serialPort.readline()
            linha_rmc = linha_serial.decode('ascii')
            #print('linha: '+linha_rmc)
            
            gp = linha_rmc[0:6]
            try:        
                if gp == '$GPRMC':
                    self._dados_gps = self._tratar_dados(linha_rmc)
                    #print('RMC: '+linha_rmc)
            except IndexError:
                Log.info('Não a dados do GPS')
            
        except UnicodeDecodeError:
            Log.info('Erro no encode do GPS')

        return self._dados_gps


    def _tratar_dados(self, linha):
        
        dados = None
        
        dados_gps = linha.split(",")
        hora    = dados_gps[1]
        dia     = dados_gps[9]
        knot    = dados_gps[7]
        lat     = dados_gps[3]
        lon     = dados_gps[5]
        direcao = dados_gps[8]

        data_hora = datetime(int('20'+dia[4:6]), int(dia[2:4]), int(dia[0:2]), 
                                int(hora[0:2]), int(hora[2:4]), int(hora[4:6]))
        
        if lat[0] == '0':
            latitude = '-' + lat[1:]
        else:
            latitude = '-' + lat

        if lon[0] == '0':
            longitude = '-' + lon[1:]
        else:
            longitude = '-' + lon


        ###Transformar knot em km/h##
        
        k = float(knot)

        metros_segundos = float(k * 0.5)
        km_hora =round(float(metros_segundos * 3.6),2)
        str_km_hora = str(km_hora) + ' km/h'

        ###---------------------------------###

        
        #print('latitude: '+latitude)
        #print('longitude: '+longitude)
        #print('knot: '+knot)
        #print('km_hora: '+str(km_hora))
                
        
        if latitude != '' and longitude != '': 
            dados = (latitude, longitude, str_km_hora, direcao, data_hora)
            self._existe_dados = True
       
        #print('Dados: '+str(dados))

        return dados    
    

class Monitor_fluxo():

    def __init__(self):
        self._taxa_fluxo = 0.0
        self._ultimo_tempo = datetime.now()

    def pulseCallback(self, p):
        
        tempo_corrente = datetime.now()
        diferenca = (tempo_corrente - self._ultimo_tempo).total_seconds()

        frequencia = 1. / diferenca
        self._taxa_fluxo = (frequencia / 7.5)

        self._ultimo_tempo = tempo_corrente

    
    def taxa_fluxo(self):
        
        if (datetime.now() - self._ultimo_tempo).total_seconds() > 1:
            self._taxa_fluxo = 0.0
            


        return round(self._taxa_fluxo,2)


class SensorThread(Thread):

    def __init__(self, config):
        Thread.__init__(self)
        self._config = config
        self._loop = True
        self._ligado = True
        self._sensores = Sensores(self._config)

    def run(self):
        while self._loop:
            print('ignicao: '+str(self._sensores.is_ignicao()))
            if self._sensores.is_ignicao == 0:
                self._ligado = False
            else:
                self._ligado = True
            time.sleep(self._config.loop_checagem)

    def parar(self):
        self._loop = False

    def is_ignicao(self):
        return self._ligado

    def descarregar_capacitor(self):
        self._sensores.descarga_capacitor()

    def desligar_placa(self):
        self._sensores.desliga_placa()
        


class Sensores():
    
    def __init__(self, config):
        
        self._config = config
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(config.sensor_ignicao, GPIO.IN)
        GPIO.setup(config.capacitor, GPIO.OUT)
        GPIO.setup(config.desliga_placa, GPIO.OUT)



    def is_ignicao(self):
        return GPIO.input(self._config.sensor_ignicao)

    def descarga_capacitor(self):
        GPIO.output(self._config.capacitor, GPIO.HIGH)

    def desliga_placa(self):
        GPIO.output(self._config.desliga_placa, GPIO.HIGH)
    


        

