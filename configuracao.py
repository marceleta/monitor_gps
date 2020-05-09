import json
from modelos import Servidor, Gps, Medidor_fluxo
class Config():
    
    def __init__(self):
        self.servidor_web = self._config_servidor()
        self.gps = self._config_gps()
        self.medidores_fluxo = self._config_medidor_fluxo()


    def _config_servidor(self):
        servidor = Servidor()
        with open('configuracao.json') as arquivo:
            _json = json.load(arquivo)
            dados = _json['servidor_web']
            servidor.porta = dados['porta']
            servidor.host = dados['host']


        return servidor

    
    def _config_gps(self):
        gps = Gps()
        with open('configuracao.json') as arquivo:
            _json = json.load(arquivo)
            dados = _json['gps']
            gps.porta   = dados['porta']
            gps.baud    = dados['baud']
            gps.timeout = dados['timeout']

        return gps


    def _config_medidor_fluxo(self):
        lista = []
        with open('configuracao.json') as arquivo:
            _json = json.load(arquivo)
            dados = _json['medidor_fluxo']

            for d in dados:
                medidor = Medidor_fluxo()
                medidor.descricao = d['descricao']
                medidor.gpio = d['gpio']
                medidor.vazao = d['vazao']
                medidor.divisor = d['divisor_frequencia']
                lista.append(medidor)

        return lista

