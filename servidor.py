from flask import Flask, request
from flask_restful import Resource, Api
from werkzeug.serving import make_server
import json
from threading import Thread
from util import Log
from configuracao import Config
from consulta import Consulta

serv_config = Config().servidor_web

class WebServiceThread(Thread):

    def __init__(self, host='0.0.0.0', porta=5000, app):
        Thread.__init__(self)
        self.srv = make_server(host, porta, app)
        self.ctx = app.app_context()
        self.ctx = ctx.push()



class ServicoStatus(Resource):

    def get(self):
        return "<html>WebService: online</html>"


class ConsultaPeriodo(Resource):
    def __init__(self):
        pass

    def post(self):
            
        mensagem = request.form['data']
        Log.info('requisição recebida: '+mensagem)
        resposta = Consulta.exec_mensagem(mensagem)
        
        return resposta

