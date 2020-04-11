import serial
import pynmea2
import datetime
import time

from modelos import DadosColetados



class Monitoramento():
    def __init__(self):
        self._serialPort = serial.Serial("/dev/ttyAMA0","9600",timeout=0.2)
        self._loop_execucao = True 

    def executar(self):

        while self._loop_execucao:
            str = self._serialPort.readline()
            self._salvar_dados(str)
            time.sleep(60)

    def _salvar_dados(self, str):
        if str.find('GGA') > 0:
            msg = pynmea2.parse(str)
            dados = DadosColetados()
            dados.latitude = msg.lat
            dados.longitude = msg.lon
            dados.data_hora = datetime.datetime.now()
            dados.save()

    def parar(self):
        self._loop_execucao = False

