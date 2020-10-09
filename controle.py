import json
import os.path
from time import sleep
import sys
from util import Log
from servicos import ThreadColetaDados
from configuracao import Config
from servidor import WebServiceThread

class Controle():

    
    def __init__(self):
        self._criar_db()
        self._is_rodando_app = False
        self._thread_coleta = None
        self._thread_web = None
        self._config = Config() 
        self._inicia_monitor()
        self.web_service = None
        self._inicia_web_service()

    def _registar_log(self, msg):
        str = 'Comando recebido: '+ msg
        Log.info(str)


    def _criar_db(self):
        dados = DadosColetados()

        if not os.path.isfile(dados.nome_db()):
            Log.info('Criando base de dados')
            dados.create_table()

        Log.info('Banco de dados criado')

    def _inicia_monitor(self):

        if self._thread_coleta != None:
            self._config = Config()
            self._parar_monitor()

        if self._thread_web != None:
            self._thread_web.parar()


        self._thread_coleta = ThreadColetaDados(self._config)
        self._thread_coleta.start()
        self.cont_rodando_serv = True
        
        Log.info('Thread monitoramento iniciada')

    def inicia_web_service(self):

        if self._web_service == None:
            
            self._web_service = WebServiceThread(self.)

    def _parar_monitor(self):

        self._thread_coleta.parar()
        Log.info('Thread monitoramento parada')

    def _parar_servico(self):
        self._thread_coleta.parar()
        self._thread_coleta = None
        sleep(1)
        self._is_rodando_app = False
       
        Log.info('Desligando programa')
        

    def cont_rodando_serv(self):

        return self._is_rodando_app





