from flask import Flask, request
from flask_restful import Resource, Api
import json

from controle import Controle
from util import Log
app = Flask(__name__)
api = Api(app)

controle = Controle()


class Consulta(Resource):
    
    def post(self):
        mensagem = request.form['data']
        Log.info('requisição recebida: '+mensagem)
        controle.exec_mensagem(mensagem)   
         
        return json.loads(controle.resposta())

    def get(self):
        return '<html>ola mundo</html>'

api.add_resource(Consulta, '/consulta-periodo')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port='5000')


