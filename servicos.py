import serial
import pynmea2
import datetime
import time
from threading import Thread
from util import Log

from modelos import DadosColetados


class ThreadMonitor(Thread):

    def __init__(self):
        Thread.__init__(self)
        self.m = Monitor()

    def run(self):
        self.m.executar()

    @property
    def monitor(self):
        return self.m



class Monitor():
    def __init__(self):
        self._serialPort = serial.Serial("/dev/ttyAMA0","9600",timeout=0.5)                
        self._loop_execucao = True 

    def executar(self):
        self._loop_execucao = True

        try:
            while self._loop_execucao:
                
                if self._serialPort == None:
                    print('if Serial')
                    self._serialPort = serial.Serial("/dev/ttyAMA0", 9600, timeout=0.5)


                linha_serial = self._serialPort.readline()
                linhas = linha_serial.decode('cp437')
                print('linha: '+linhas)
         
                gga = linhas[0:6]
                
                if gga == '$GPRMC':
                    self._salvar_dados(linhas)
                    
                self._serialPort.close()
                self._serialPort = None
                time.sleep(10)                    
        except:
            Log.info('Erro na leitura do GPS')

    
    def _gps_esta_online(self, linha):
        gga = pynmea2.parse(linha)

        is_online = True
        latitude = gga.lat
        longitude = gga.lon

        if latitude != '' and longitude != '':
            is_online = False
            Log.info('Não a dados para ser no GPS')

        return is_online
        



    def _salvar_dados(self, linha_gprmc):
        gga = pynmea2.parse(linha_gprmc)
        dados = DadosColetados()
        dados.latitude = gga.lat
        dados.longitude = gga.lon
        
        if dados.latitude != '' and dados.longitude != '': 
            dados.data_hora = datetime.datetime.now()
            dados.save()
        else:
            Log.info('Não há dados do GPS')

    def parar(self):
        self._loop_execucao = False

    def iniciar(self):
        self._loop_execucao = True

