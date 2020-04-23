import json
import os.path
from modelos import DadosColetados
from util import Log
from servicos import ThreadMonitor


class Controle():

    
    def __init__(self):
        self._criar_db()
        self._resposta = ''
        self._is_rodando_app = False
        self._thread_monitor = ThreadMonitor()
        self._inicia_monitor()
        

    def exec_mensagem(self, msg_json):
        print('comando: '+ msg_json)
        mensagem = json.loads(msg_json)
        comando = mensagem['comando']
        self._registar_log(comando)

        if comando == 'parar_servico':
            self._resposta = "{resposta:'desligando'}"
            self._parar_servico()
        elif comando == 'lst_por_data':            
            self._resposta = self._lista_por_data(mensagem)
        elif comando == 'parar_monitor':
            self._resposta = "{resposta:'monitor_parado'}"
        else:
            self._resposta = "{resposta:'comando_404'}"

    def resposta(self):
        
        return json.dumps(self._resposta)

    def _lista_por_data(self, mensagem):
        resposta = {
            'resposta':'list_por_data',
            'conteudo':'None'
        }

        try:
            data_inicio = mensagem['data_inicio']
            data_final  = mensagem['data_final']

            resultados = DadosColetados.por_intervalo(data_inicio, data_final)
            resposta = {
                'resposta': 'lst_por_data',
                'conteudo': resultados
            }
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

    def _inicia_monitor(self):

        if self._thread_monitor != None:
            self._parar_monitor()

        self._thread_monitor = ThreadMonitor()
        self._thread_monitor.start()

    def _parar_monitor(self):
        self._monitor = self._thread_monitor.monitor
        self._monitor.parar()
        self._thread_monitor = None

    def _parar_servico(self):
        self._parar_monitor()
        self._is_rodando_app = True


    def cont_rodando_serv(self):
        
        return self._is_rodando_app





