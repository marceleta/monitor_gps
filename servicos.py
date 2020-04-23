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
                linha_serial = self._serialPort.readline()
                linhas = linha_serial.decode('cp437')
                gga = linhas[0:6]
    #            print('todas as linhas: '+gga)
                if gga == '$GPGGA':
                    print('linha_gga: '+ linhas)
                    self._salvar_dados(linhas)
                    time.sleep(60)
        except:
            Log.info('Erro na leitura do GPS')


    def _salvar_dados(self, linha_gprmc):
        gga = pynmea2.parse(linha_gprmc)
        dados = DadosColetados()
        dados.latitude = gga.lat
        dados.longitude = gga.lon
        dados.data_hora = datetime.datetime.now()
        dados.save()

    def parar(self):
        self._loop_execucao = False

    def iniciar(self):
        self._loop_execucao = True

