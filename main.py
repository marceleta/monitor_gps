from flask import Flask, request
from flask_restful import Resource, Api
import json

from controle import Controle

app = Flask(__name__)
api = Api(app)

controle = Controle()


class Consulta(Resource):
    
    def post(self):
        mensagem = request.form['mensagem']

        controle.exec_mensagem(mensagem)
        

        return json.loads(controle.resposta())    

api.add_resource(Consulta, '/consulta-periodo')


if __name__ == '__main__':
    app.run(debug=True)


