from flask import Flask, request
from flask_restful import Resource, Api
import json
from sys import exit

from controle import Controle
from util import Log
from configuracao import Config

app = Flask(__name__)
api = Api(app)

controle = Controle()
servidor = Config().servidor_web

class Consulta(Resource):
    
    def post(self):
        
        mensagem = request.form['data']
        Log.info('requisição recebida: '+mensagem)
        controle.exec_mensagem(mensagem)
        resposta = json.loads(controle.resposta())
        resposta = controle.resposta()
        
        return resposta

    def get(self):
        return '<html>ola mundo</html>'

api.add_resource(Consulta, '/consulta-periodo')


if __name__ == '__main__':
    app.run(debug=True, host=servidor.host, port=servidor.porta)


