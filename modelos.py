from peewee import *
from datetime import datetime
from util import Conversor, Log
import json, traceback

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

    @staticmethod
    def ignicao():
        return 'ignicao'

    @staticmethod
    def desligamento():
        return 'desligamento'

    @staticmethod
    def parada():
        return 'parada'
        
    @staticmethod
    def acima_velocidade():
        return 'acima_velocidade'

    class Meta:
        database = db
        db_table = 'dados_coletados'

    data_hora  = DateTimeField(formats=['%d/%m/%Y %H:%M'])
    latitude   = CharField()
    longitude  = CharField()
    velocidade = CharField()    
    fluxo1     = CharField(default=None)
    fluxo2     = CharField(default=None)
    sentido    = CharField(default=None)
    razao      = CharField(default='')
    transmitido = BooleanField(default=False)

    def nome_db(self):
        return nome_db

    @staticmethod
    def por_intervalo(data_inicio, data_final):
        
        inicio = Conversor.str_para_datetime(data_inicio)
        final = Conversor.str_para_datetime(data_final)

        consulta = None
        
        try:
            consulta = DadosColetados.select().where(
                (DadosColetados.data_hora >= inicio) and (DadosColetados.data_hora <= final))
            lista =[]
            for c in consulta:
                dado = {
                    'id': c.id,
                    'data_hora': c.data_hora,
                    'lat': c.latitude,
                    'lng': c.longitude,
                    'pressao_a':None,
                    'pressao_b':None,
                    'fluxo_a': c.fluxo1,
                    'fluxo_b': c.fluxo2,
                    'velocidade': c.velocidade,
                    'sentido': c.sentido,
                    'razao': c.razao
                }
                lista.append(dado)

        except:
            tb = traceback.format_exc()
            Log.error('por_intervalo traceback: '+str(tb))

        return lista

    def para_json(self):
        return Conversor.objeto_para_json(self)

    
