from peewee import *
from datetime import datetime

nome_db = 'monitoramento.db'

db = SqliteDatabase('monitoramento.db')

class DadosColetados():

    class Meta:
        database = db
        db_table = 'dados_coletados'

    data_hora = DateTimeField()
    latitude  = CharField();
    longitude = CharField();

    def nome_db(self):
        return nome_db