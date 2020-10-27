from flask import Flask, request
from flask_restful import Resource, Api
from werkzeug.serving import make_server
import json
from threading import Thread
from util import Log
from configuracao import Config
from consulta import Consulta

class WebServiceThread(Thread):

    def __init__(self, host='0.0.0.0', porta=5000):
        Thread.__init__(self)
        app = Flask('Web Service')
        self.api = Api(app)
        self.srv = make_server(host, porta, app)
        self.ctx = app.app_context()
        self.ctx.push()
    
    def run(self):
        self._config()
        Log.info('iniciando web service')
        self.srv.serve_forever()

    def stop_server(self):
        Log.info('parando web service')
        self.srv.shutdown()

    def _config(self):
        self.api.add_resource(ServicoStatus, '/status')
        self.api.add_resource(ConsultaPeriodo,'/periodo')
        

class ServicoStatus(Resource):

    def get(self):
        Log.info('requisicao de estatus')
        return "<html>WebService: online</html>"


class ConsultaPeriodo(Resource):
    
    def post(self):
            
        mensagem = request.form['data']
        Log.info('requisição recebida: '+mensagem)
        resposta = Consulta.exec_mensagem(mensagem)
        
        return resposta

