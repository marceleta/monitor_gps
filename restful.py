from flask import Flask, request
from flask_restful import Resource, Api

app = Flask(__name__)
api = Api(app)

class Consulta(Resource):

    def post(self):
        data_inicio = request.form['data_inicio']
        data_final = request.form['data_final']
    
        return {'data_inicio':data_inicio, 'data_final':data_final}
    

api.add_resource(Consulta, '/consulta-periodo')

if __name__ == '__main__':
    app.run(debug=True)

