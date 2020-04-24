from peewee import *
from datetime import datetime
from util import Conversor, Log
import json
nome_db = '/home/pi/projetos/monitor_gps/monitoramento.db'

db = SqliteDatabase(nome_db)

class DadosColetados(Model):

    class Meta:
        database = db
        db_table = 'dados_coletados'

    data_hora = DateTimeField(formats=['%d/%m/%Y %H:%M'], default=datetime.now)
    latitude  = CharField();
    longitude = CharField();

    def nome_db(self):
        return nome_db

    @staticmethod
    def por_intervalo(data_inicio, data_final):
        inicio = Conversor.str_para_datetime(data_inicio)
        print('inicio: '+str(inicio))
        final = Conversor.str_para_datetime(data_final)
        print('final: '+str(final))
        consulta = None
        try:
            consulta = DadosColetados.select().where(
                (DadosColetados.data_hora >= inicio) & (DadosColetados.data_hora <= final))
            print('consulta: '+str(consulta))
            lista =[]
            for c in consulta:
                dado = {
                    'id': c.id,
                    'data_hora': c.data_hora,
                    'latitude': c.latitude,
                    'longitude': c.longitude
                }
                lista.append(dado)

        except:
            Log.info('por_intervalo:Erro ao fazer consulta no banco')

        return lista

    def para_json(self):
        return Conversor.objeto_para_json(self)
