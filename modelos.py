from peewee import *
from datetime import datetime
from util import Conversor, Log
import json

class Servidor():
    
    def __init__(self, porta=5000, host="0.0.0.0"):
        self.porta = porta
        self.host  = host 

class Gps():
    
    def __init__(self, porta="/dev/ttyAMA0", baud="9600", timeout=0.5):
        self.porta = porta
        self.baud = baud
        self.timeout = timeout

class Medidor_fluxo():

    def __init__(self, descricao="", vazao=" L/min" , gpio=16, divisor=7.5):
        self.descricao = descricao
        self.vazao = vazao
        self.gpio = gpio
        self.divisor = divisor


nome_db = '/home/pi/programas/monitor_gps/monitoramento.db'

db = SqliteDatabase(nome_db)

class DadosColetados(Model):

    class Meta:
        database = db
        db_table = 'dados_coletados'

    data_hora  = DateTimeField(formats=['%d/%m/%Y %H:%M'])
    latitude   = CharField()
    longitude  = CharField()
    velocidade = CharField()    
    fluxo1     = CharField()
    fluxo2     = CharField()
    direcao    = CharField()
    ignicao    = BooleanField(default=False)
    desligamento = BooleanField(default=False)

    def nome_db(self):
        return nome_db

    @staticmethod
    def por_intervalo(data_inicio, data_final):
        inicio = Conversor.str_para_datetime(data_inicio)
        final = Conversor.str_para_datetime(data_final)
        consulta = None
        try:
            consulta = DadosColetados.select().where(
                (DadosColetados.data_hora >= inicio) & (DadosColetados.data_hora <= final))
            lista =[]
            for c in consulta:
                dado = {
                    'id': c.id,
                    'data_hora': c.data_hora,
                    'latitude': c.latitude,
                    'longitude': c.longitude,
                    'fluxo1': c.fluxo1,
                    'fluxo2': c.fluxo2,
                    'velocidade': c.velocidade,
                    'direcao': c.direcao,
                    'ignicao_veiculo': c.ignicao_veiculo
                }
                lista.append(dado)

        except:
            Log.info('por_intervalo:Erro ao fazer consulta no banco')

        return lista

    def para_json(self):
        return Conversor.objeto_para_json(self)
