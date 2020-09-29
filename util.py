import logging
from datetime import datetime
import json
logging.basicConfig(level=logging.INFO, filename='/home/pi/programas/monitor_gps/monitoramento.log', filemode='a',
                    format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%d/%m/%Y %H:%M')


class Log:

    @staticmethod
    def debug(mensagem):
        logging.debug(mensagem)

    @staticmethod
    def info(mensagem):
        logging.info(mensagem)

    @staticmethod
    def warning(mensagem):
        logging.warning(mensagem)

    @staticmethod
    def error(mensagem):
        logging.error(mensagem)

class Conversor:

    @staticmethod
    def str_para_datetime(data_hora):
        formato = '%d/%m/%Y %H:%M'
        
        resposta = None
        try:
           resposta = datetime.strptime(data_hora, formato)
        except:
            Log.info('str_para_datetime: erro ao formatar str para datetime')

        return resposta

    @staticmethod
    def objeto_para_json(objeto):
        resposta = None
        if objeto != None:
            resposta = json.dumps(objeto.__dict__)

        return resposta




