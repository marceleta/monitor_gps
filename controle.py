import json
import os.path
from modelos import DadosColetados
from util import Log


class Controle():

    self._parar_servico = 'parar_servico'
    self._resposta = ''
    self._is_rodando_servico = False
    
    def __init__(self):
        self._criar_db()

    def exec_mensagem(self, msg_json):

        mensagem = json.loads(msg_json)
        comando = mensagem['comando']
        self._registar_log(comando)

        if comando == self.parar_servico:
            self._resposta = "{resposta:'desligando'}"
            self._is_rodando_servico = True

    def _registar_log(self, msg):
        str = 'Comando recebido: '+ msg
        Log.info(str)


    def _criar_db(self):
        dados = DadosColetados()

        if not os.path.isfile(dados.nome_db()):
            Log.info('Criando base de dados')
            dados.create_table()



