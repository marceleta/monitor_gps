from datetime import datetime
import hashlib, traceback
from util import Log
import subprocess, requests
import json, re
from configuracao import Config
from modelos import DadosColetados

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

class TransmitirWeb():

    def __init__(self, host):
        self.host = host
        self._config = Config()
        self._loop = True

    def _status_servidor(self):
        ping = subprocess.Popen(['ping', '-c', '1', self.host], stdout = subprocess.PIPE, stderr = subprocess.PIPE)
        out, error = ping.communicate()
        
        saida = out.decode()
        resultado = saida.find('100% packet loss')

        if resultado == -1:
            resposta = True
        else:
            resposta = False

        return resposta

    def _enviar(self, dados, url):
        md5 = dados['md5']
        path_arquivo = dados['arquivo']

        file = open(path_arquivo, 'r')
        print('arquivo conteudo: '+file.read())

        formulario = {}
        formulario['md5'] = md5

        
        print('url: '+url)

        session = requests.session()
        headers = {
                    'origin': 'http://35.199.78.129/posicoes',
                    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36"
                    }

        form = session.get(url, headers=headers)
        print(form.text)
        #csrf_token = re.findall(r'<input type="hidden" name="_token" value="(.*)"', form.text)[0]

        #print('_token: '+csrf_token)
        
        #formulario['_token'] = csrf_token
                
        files = {'jsonFile': open(path_arquivo, 'rb')}

        
        response = session.post(url, files=files, data=formulario)

        print('response: '+response.text)

        
        return response

    # verifica se o servidor esta online e envia os dados
    # caso o servidor responda com um numero maior que 0 e atualizado a flag transmitida no banco
     def loop_envio(self, dados_envio):

        config = self._config.envio_dados()
        servidor = config['servidor']
        url = config['url_envio']
        path_envio = servidor + url

        loop = True
        tempo_loop = datetime.now() + timedelta(0, int(self._config.tempo_espera_envio()))

        while self._loop:

            if self._status_servidor():
                response = self._enviar(dados_envio, path_envio)
                print('response: '+response)
                resposta = int(resposta)
                if resposta > 0:
                    self.sucesso_envio(dados_envio)
                    loop = False

            
            agora = datetime.now()            
            if agora > tempo_loop:
                loop = False
            
            sleep(20)

    
    # prepara a lista de ids para alterar a flag de transmitido
    def _sucesso_envio(self, dados_enviados):
        
        conteudo = dados_enviados['conteudo']
        ids = []
        for linha in conteudo:
            str_id = linha['id']
            id = int(str_id)
            lista.append(id)

        print('ids: '+str(ids))
        try:
            DadosColetados.enviados_sucesso(ids)
            Log.info('Dados enviados com sucesso ao servidor')
        except:
            tb = traceback.format_exc()
            Log.error('_sucesso_envio: '+tb)


class ThreadTransmissao(Thread):

    def __init__(self):
        Thread.__init__(self)
        self.transmitir = TransmitirWeb()

    def run(self):
        self.transmitir.loop_envio()

    def is_rodando(self):
        return self.transmitir._loop

    def parar(self):
        self.transmitir._loop = False







