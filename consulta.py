from util import Log
from configuracao import Config
from modelos import DadosColetados
import json, traceback

class Consulta():

    def __init__(self):
        self._resposta = ''
        self._config = Config()

    def exec_mensagem(self, msg_json):
        
        mensagem = json.loads(msg_json)
        comando = mensagem['comando']
        print('comando: '+ comando)
        Log.info(comando)

        if comando == 'lst_por_data':            
            self._resposta = self._lista_por_data(mensagem)        
        else:
            self._resposta = "{resposta:'comando nao encontrado'}"

        return json.dumps(self._resposta)    

    def _lista_por_data(self, mensagem):
    
        resposta = {
            'id_monitor':self._config.id_monitor(),
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
            Log.error('_lista_por_data: formato da data incorreto')
            e = traceback.format_exc()
            Log.error('_lista_por_data: '+e)
        
        print(resposta)
        return resposta
    
