import json
import os.path
from time import sleep
import sys, os
from util import Log
from servicos import ThreadColetaDados, SensorThread
from modelos import DadosColetados
from configuracao import Config
from servidor import WebServiceThread
from time import sleep
from threading import Thread
import RPi.GPIO as GPIO

class Controle():

    
    def __init__(self):
        self._criar_db()
        self._is_rodando_app = False
        self._thread_coleta = None
        self._thread_web = None
        self._sensor_thread = None
        self._config = Config() 
        self._web_service = None

    def start(self):
        try:
            self._inicia_coleta()
            self._inicia_web_service()
            self._inicia_thread_sensores()
            self._thread_check_ignicao()
            self._thread_check_stop()
        except KeyboardInterrupt:
            print('saindo...')

    def stop(self):
        Log.info('Parando Geo Sensor')
        self._loop_verifica_ignicao = False
        self._parar_web_service()
        self._parar_thread_sensores()
        self._parar_coleta()
        sleep(60)
        #sys.exit()
        os.system('sudo shutdown -h now')        


    def _inicia_coleta(self):

        if self._thread_coleta != None:
            self._parar_coleta()

        self._thread_coleta = ThreadColetaDados(self._config)
        self._thread_coleta.start()
        self.cont_rodando_serv = True
        
        Log.info('Thread monitoramento iniciada')

    def _parar_coleta(self):
        self._thread_coleta.parar()
        self._thread_coleta = None
        Log.info('Thread monitoramento parada')

    def _inicia_web_service(self):

        if self._web_service != None:
            self._parar_web_service()

        self._web_service = WebServiceThread(self._config.host, self._config.porta)
        self._web_service.start()

        Log.info('iniciar web service')

    def _parar_web_service(self):
        self._web_service.stop_server()
        self._web_service = None
        Log.info('Web service parado')

    def _inicia_thread_sensores(self):

        if self._sensor_thread != None:
            self._parar_thread_sensores()

        self._sensor_thread = SensorThread(self._config)
        self._sensor_thread.start()

    def _parar_thread_sensores(self):
        if self._sensor_thread != None:
            self._sensor_thread.parar()
            self._sensor_thread = None     



    def _criar_db(self):
        dados = DadosColetados()

        if not os.path.isfile(dados.nome_db()):
            Log.info('Criando base de dados')
            dados.create_table()

        Log.info('Banco de dados criado')

    #verifica se a ignicao esta ligada
    # sim -> liga a coleta do GPS
    # não -> desliga a coleta do GPS
    def _verifica_ignicao(self):

        #self._thread_coleta = ThreadColetaDados(self._config)
        #self._thread_coleta.start()
        
        self._loop_verifica_ignicao = True

        while self._loop_verifica_ignicao:
            

            is_ignicao = self._sensor_thread.is_ignicao()
            
            if is_ignicao:
                    if self._thread_coleta == None:
                        self._inicia_coleta()
            else:
                if self._thread_coleta != None:
                    self._thread_coleta.is_ignicao(True)
                    sleep(45)
                    self._parar_coleta()
                    GPIO.cleanup()

                    self._inicia_thread_sensores()

            sleep(10)
            


    def _thread_check_ignicao(self):
        thread = Thread(target=self._verifica_ignicao, args=())
        thread.start()

    
    def _verifica_desligamento(self):

        while True:
            desliga = self._config.deligar_geo_sensor()
            
            if desliga:
                self.stop()
            sleep(20)

    def _thread_check_stop(self):
        thread = Thread(target=self._verifica_desligamento, args=())
        thread.start()


    def cont_rodando_serv(self):

        return self._is_rodando_app





