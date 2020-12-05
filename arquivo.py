from datetime import datetime, timedelta
import hashlib, traceback
from util import Log
import subprocess, requests
import json, re
from configuracao import Config
from modelos import DadosColetados
from threading import Thread
from time import sleep

class Arquivo():
    
    '''
    Cria um arquivo com a data+hora+minuto.json
    '''
    @staticmethod
    def posicoes(dados):
        Log.info('criar_arquivo: criando arquivo')
        retorno = {}
        try:
            ## Nome do arquivo
            data_hora = datetime.now()
            str_data_hora = data_hora.strftime('%d%m%y_%H%M%S')
            nome_arquivo = 'arquivos_json/' + str_data_hora + '.json'
            #escrita no arquivo
            if len(dados) > 0:
                arquivo = open(nome_arquivo, 'a')
                arquivo.write(json.dumps(dados))
                arquivo.flush()
                arquivo.close()

                #MD5
                arquivo = open(nome_arquivo, 'rb')

                md5 = hashlib.md5(arquivo.read()).hexdigest()

                arquivo.close()

                retorno['md5'] = md5
                retorno['arquivo'] = nome_arquivo

        except:
            e = traceback.format_exc()
            Log.error('criar_arquivo: '+e)        

        return retorno




