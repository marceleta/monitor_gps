import json
import os.path
from time import sleep
import sys
from modelos import DadosColetados
from util import Log
from servicos import ThreadColetaDados
from configuracao import Config

class Controle():

    
    def __init__(self):
        self._criar_db()
        self._resposta = ''
        self._is_rodando_app = False
        self._thread_coleta = None
        self._thread_web = None
        self._config = Config() 
        self._inicia_monitor()
        

    def exec_mensagem(self, msg_json):
        
        mensagem = json.loads(msg_json)
        comando = mensagem['comando']
        print('comando: '+ comando)
        self._registar_log(comando)

        if comando == 'parar_servico':
            self._resposta = '{"resposta":"desligando"}'
            self._parar_servico()
        elif comando == 'lst_por_data':            
            self._resposta = self._lista_por_data(mensagem)
        elif comando == 'parar_monitor':
            self._parar_servico()
            self._resposta = "{'resposta':'monitor_parado'}"
        else:
            self._resposta = "{resposta:'comando_404'}"

    def resposta(self):
        return json.dumps(self._resposta)

    def _lista_por_data(self, mensagem):

        resposta = {
            'id_monitor':self.config.id_monitor(),
            'resposta':'list_por_data',
            'conteudo':'None'
        }

        try:
            data_inicio = mensagem['data_inicio']
            data_final  = mensagem['data_final']

            resultados = DadosColetados.por_intervalo(data_inicio, data_final)

            if len(resultados) > 0:
                resposta['conteudo'] = resultados
                
        except:
            Log.info('_lista_por_data: formato da data incorreto')

        

        return resposta
            

    def _registar_log(self, msg):
        str = 'Comando recebido: '+ msg
        Log.info(str)


    def _criar_db(self):
        dados = DadosColetados()

        if not os.path.isfile(dados.nome_db()):
            Log.info('Criando base de dados')
            dados.create_table()

        Log.info('Banco de dados criado')

    def _inicia_monitor(self):

        if self._thread_coleta != None:
            self._config = Config()
            self._parar_monitor()

        if self._thread_web != None:
            self._thread_web.parar()


        self._thread_coleta = ThreadColetaDados(self._config)
        self._thread_coleta.start()
        self.cont_rodando_serv = True
        
        Log.info('Thread monitoramento iniciada')

    def _parar_monitor(self):

        self._thread_coleta.parar()
        Log.info('Thread monitoramento parada')

    def _parar_servico(self):
        self._thread_coleta.parar()
        self._thread_coleta = None
        sleep(1)
        self._is_rodando_app = False
       
        Log.info('Desligando programa')
        

    def cont_rodando_serv(self):

        return self._is_rodando_app





