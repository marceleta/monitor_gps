from flask import Flask, request
from flask_restful import Resource, Api
import json
from sys import exit
from threading import Thread

from util import Log
from configuracao import Config

serv_config = Config().servidor_web

class WebService(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.webservice = Monitor_web()

    def run(self):
        self.monitor.iniciar()

    def parar(self):
        self.monitor.parar()


class Consulta_periodo(Resource):
    def __init__(self):
        pass

    def post(self):
            
        mensagem = request.form['data']
        Log.info('requisição recebida: '+mensagem)
        controle.exec_mensagem(mensagem)
        resposta = json.loads(controle.resposta())
        resposta = controle.resposta()
        
        return resposta

    def _resposta(self):
        

class Monitor_web(Api, App):
    def _init__(self):
        self.add_resource(Consulta_periodo, '/consulta-periodo')
        self.app = None

    def iniciar(self):
        app = Flask('Monitor GPS')
        app.run(debug=True, host=serv_config.host, port=serv_config.porta)

    def parar(self):
        shutdown = request.environ.get('werkzeug.server.shutdown')
        shutdown()       


    

