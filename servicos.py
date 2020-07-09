import serial
from datetime import timedelta
from datetime import datetime
import time
from threading import Thread
from util import Log
import RPi.GPIO as GPIO

from modelos import DadosColetados



class ThreadColetaDados(Thread):

    def __init__(self, config):
        Thread.__init__(self)
        self.monitor = Monitor(config)


    def run(self):
        self.monitor.executar()

    def parar(self):
        self.monitor.parar()
    

class Monitor():

    def __init__(self, config):

        self._loop_execucao = True
        self._config = config
        #self._INPUT_PIN = 16
        self._medidores_fluxo = self._config_fluxo(config.medidores_fluxo)
        self._gps = Monitor_gps(config.gps)


    def _config_fluxo(self, monitores_fluxo):
        GPIO.setmode(GPIO.BOARD)
        lista = []
        for monitor in monitores_fluxo:
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

        tempo60s = datetime.now() + timedelta(0, 60)

        while self._loop_execucao:
            dados = self._gps.executar()
            print('dados gps: '+str(dados))
            agora = datetime.now() 
            if agora > tempo60s and dados != None:
                dados_coletados = DadosColetados()
                dados_coletados.latitude, dados_coletados.longitude, dados_coletados.velocidade = dados
                
                fluxo1 = self._medidores_fluxo[0]    
                str_fluxo = str(fluxo1.taxa_fluxo()) + ' L/min'
                dados_coletados.fluxo1 = str_fluxo
                print('Fluxo 1'+ str(str_fluxo))

                fluxo2 = self._medidores_fluxo[1]
                str_fluxo = str(fluxo2.taxa_fluxo()) + ' L/min'
                dados_coletados.fluxo2 = str_fluxo
                print('Fluxo 2: '+str_fluxo)
                
                dados_coletados.save()
                    
                tempo60s = datetime.now() +  timedelta(0,60)
                

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
            print('linha: '+linha_rmc)
            
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
        data = linha.split(",")
        dados = None
        knot = data[7]
        lat = data[3]
        lon = data[5]
        
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
            dados = (latitude, longitude, str_km_hora)
            self._existe_dados = True
       

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

