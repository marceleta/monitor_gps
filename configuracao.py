import json, os
from modelos import Servidor, Gps, Medidor_fluxo
class Config():
    
    def __init__(self):
        self.servidor_web = self._config_servidor()
        self.gps = self._config_gps()
        self.medidores_fluxo = self._config_medidor_fluxo()
        self._mac_address = ''


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


    def id_monitor(self):
        id = ''
        if self._mec_address == '':
            with open('configuracao.json') as arquivo:
                _json = json.load(arquivo)
                wlan = _json['wlan']

            saida_terminal =  os.popen('ifconfig -a '+wlan)
            terminal_texto = saida_terminal.read()
            posicao = texto.find('ether')
            inicio = posicao + 6
            final = inicio + 17
            self._mec_address = terminal_texto[inicio:final]


        return self._mec_address
    
    def tempo_captura(self):
        #tempo padrao
        _tempo_captura = 30
        with open('configuracao.json') as arquivo:
            _json = json.load(arquivo)
            _tempo_captura = _json['tempo_captura']

        return _tempo_captura




        

