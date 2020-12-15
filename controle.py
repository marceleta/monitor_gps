import json
import os.path
from time import sleep
from datetime import datetime, timedelta
import sys, os
from util import Log
from servicos import ThreadColetaDados, SensorThread, ThreadTransmissao, Desligar
from modelos import DadosColetados
from configuracao import Config
from servidor import WebServiceThread
from time import sleep
from threading import Thread
import traceback
import RPi.GPIO as GPIO
from arquivo import Arquivo

class Controle():

    
    def __init__(self):
        self._criar_db()
        self._is_rodando_app = False
        self._thread_coleta = None
        self._thread_web = None
        self._sensor_thread = None
        self._config = Config() 
        self._web_service = None
        self._thread_transmissao = None

    # o iniciar/parar da coleta depende da ignição por isso fica em outro local: _verifica_ignicao 
    def start(self):
        Log.info('iniciando Geo Sensor')
        self._loop_verifica_ignicao = True
        try:
            self._inicia_thread_sensores()
            self._thread_check_ignicao()
            self._thread_check_stop()
        except KeyboardInterrupt:
            print('saindo...')

    def desligar(self):
        Log.info('Parando Geo Sensor')
        try:
            self._parar_web_service()
            Log.info('Desligando Geo Sensor')
            desligar = Desligar()
            #desligar.agora()
            #sleep(60)
            #os.system('sudo shutdown -h now')
        except:
            tb = traceback.format_exc()
            Log.error('stop: '+tb)        


    def _inicia_coleta(self):

        if self._thread_coleta != None:
            self._parar_coleta()

        self._thread_coleta = ThreadColetaDados(self._config)
        self._thread_coleta.start()
        self.cont_rodando_serv = True
        
        Log.info('Thread monitoramento iniciada')

    def _parar_coleta(self):
        
        if self._thread_coleta != None:
            self._thread_coleta.parar()
            self._thread_coleta = None
        Log.info('Thread monitoramento parada')

    def _inicia_web_service(self):

        if self._web_service != None:
            self._parar_web_service()

        self._web_service = WebServiceThread(self._config.host, self._config.porta)
        self._web_service.start()

        Log.info('Inicia web service')

    def _parar_web_service(self):
        if self._web_service != None:
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

    # verifica se a ignicao esta ligada
    # True -> liga a coleta do GPS
    # False -> desliga a coleta do GPS
    #Controla a transmissao de dados
    # Quando a ignição e desligada começa a tentativa de enviar os dados
    # Se a ignicao for ligada espera a tentativa acabar para matar a thread de transmissao
    def _verifica_ignicao(self):

        
        while self._loop_verifica_ignicao:

            is_ignicao = self._sensor_thread.is_ignicao()

            print('ignicao: '+str(is_ignicao))

            if is_ignicao: 
                if self._thread_coleta == None or self._thread_coleta.is_alive() == False:             
                    self._inicia_coleta()
                    if self._thread_transmissao != None and self._thread_transmissao.is_alive() == False:
                        self._parar_transmissao()

            else:
                if self._thread_coleta != None:
                    self._thread_coleta.is_ignicao(is_ignicao)

                if self._thread_coleta.is_alive() == False:
                    if self._thread_transmissao == None:
                        self._inicia_transmissao()


            if self._thread_transmissao != None and self._thread_transmissao.status != None:
                self.desligar()

            sleep(10)


    def _thread_check_ignicao(self):
        thread = Thread(target=self._verifica_ignicao, args=())
        thread.start()

    
    def _verifica_desligamento(self):

        while True:
            desliga = self._config.deligar_geo_sensor()
            
            if desliga:
                self.desligar()
            sleep(20)

    def _thread_check_stop(self):
        thread = Thread(target=self._verifica_desligamento, args=())
        thread.start()

    def cont_rodando_serv(self):

        return self._is_rodando_app

    #cria a string estruturado para o envio pela web
    def posicoes_nao_transmitidas(self):
        lista = DadosColetados.nao_transmitidos()
        dados = {
            "id_monitor":self._config.id_monitor(),
            "conteudo":lista
        }
        

        return dados
    #cria o arquivo para ser enviado 
    def arquivo_transmissao(self, posicoes_json):
        posicoes_arquivo = Arquivo.posicoes(posicoes_json)

        return posicoes_arquivo


    def _inicia_transmissao(self):
        print('inicia transmissao')
        config = self._config.servidor_transmissao()

        posicoes = self.posicoes_nao_transmitidas()
        arquivo = self.arquivo_transmissao(posicoes)

        if self._thread_transmissao == None:
            try:
                self._thread_transmissao = ThreadTransmissao(config, arquivo)
                self._thread_transmissao.start()
            except:
                tb = tranceback.format_exc()
                Log.error('_inicia_transmissao: '+tb)

        Log.info('transmissao iniciada')

    def _parar_transmissao(self):

        if self._thread_transmissao != None:
            print('para transmissao')
            self._thread_transmissao.parar()
            self._thread_transmissao = None
            Log.info('transmissao parada')

