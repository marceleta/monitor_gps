from datetime import datetime
import hashlib, traceback
from util import Log
import subprocess, requests

class Arquivo():
    
    '''
    Cria um arquivo com a data+hora+minuto.json
    '''
    @staticmethod
    def criar_arquivo(dados):
        Log.info('criar_arquivo: criando arquivo')
        retorno = {}
        try:
            ## Nome do arquivo
            data_hora = datetime.now()
            str_data_hora = data_hora.strftime('%d%m%y_%H%M%S')
            nome_arquivo = 'arquivos_json/' + str_data_hora + '.json'

            #escrita no arquivo
            arquivo = open(nome_arquivo, 'a')
            arquivo.write(dados)
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

class EnvioWeb():

    def __init__(self, host):
        self.host = host

    def status_servidor(self):
        ping = subprocess.Popen(['ping', '-c', '1', self.host], stdout = subprocess.PIPE, stderr = subprocess.PIPE)
        out, error = ping.communicate()
        
        saida = out.decode()
        resultado = saida.find('100% packet loss')

        if resultado == -1:
            resposta = True
        else:
            resposta = False

        return resposta

    def enviar(self, dados, path_servidor):
        md5 = dados['md5']
        f = dados['arquivo']

        arquivo = open(f, 'rb')

        dados = {}
        dados['md5'] = md5
        files = {'jsonFile': arquivo.read()}

        url = self.host + path_servidor

        r = requests.post(url, files=files, data=dados)

        resposta = False

        if r == '<Response [200]>':
            resposta = True

        return resposta










