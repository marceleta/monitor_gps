import json, os
from modelos import Servidor, Gps, Medidor_fluxo
class Config():
    
    def __init__(self):
        #configurações default do sensor
        self.sensor_ignicao = 32
        self.capacitor = 22
        self.desliga_placa = 19
        self.loop_checagem = 45

        self.gps = self._config_gps()
        self._config_sensor()
        self.medidores_fluxo = self._config_medidor_fluxo()
        self._mac_address = ''
        self.servidor = Servidor()
        self.host = '0.0.0.0'
        self.porta = 5000


    def _config_servidor(self):
        with open('configuracao.json') as arquivo:
            _json = json.load(arquivo)
            dados = _json['servidor_web']
            self.porta = dados['porta']
            self.host = dados['host']


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

    def _config_sensor(self):
        with open('configuracao.json') as arquivo:
            _json = json.load(arquivo)
            dados = _json['controle_placa']
            self.sensor_ignicao = dados['sensor_ignicao']
            self.capacitor = dados['capacitor']
            self.desliga_placa = dados['desliga_placa']


    def id_monitor(self):
        id = ''
        if self._mec_address == '':
            with open('configuracao.json') as arquivo:
                _json = json.load(arquivo)
                wlan = _json['wlan']

            saida_terminal =  os.popen('ifconfig -a '+wlan)
            terminal_texto = saida_terminal.read()
            posicao = terminal_texto.find('ether')
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




        

