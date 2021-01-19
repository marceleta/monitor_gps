import serial
from datetime import timedelta
from datetime import datetime
import time
from threading import Thread
from util import Log
import RPi.GPIO as GPIO
import subprocess, requests, json, traceback
from time import sleep

from modelos import DadosColetados
from configuracao import Config as config



class ThreadColetaDados(Thread):

    def __init__(self, config):
        Thread.__init__(self)
        self.monitor = Monitor(config)


    def run(self):
        self.monitor.executar()

    def parar(self):
        self.monitor.parar()

    def set_ignicao(self, ignicao):
        self.monitor.set_ignicao(ignicao)

    def ignicao(self):
        return self.monitor._ignicao
    

class Monitor():

    def __init__(self, config):

        self._loop_execucao = True
        self._config = config
        #self._INPUT_PIN = 16
        self._medidores_fluxo = self._config_fluxo(config.medidores_fluxo)
        self._gps = Monitor_gps(config.gps)
        self._tempo_config = config.tempo_captura()
        '''
            recebe um boleano para a ignicao do carro
            True -> ignicao ligada
            False -> ignicao desligada
        '''        
        self._ignicao = True
        

        

    def set_ignicao(self, ignicao):
        self._ignicao = ignicao


    def _config_fluxo(self, monitores_fluxo):
        GPIO.setmode(GPIO.BOARD)
        lista = []
        try:
            for monitor in monitores_fluxo:
                #print('Monitor GPIO: '+str(monitor.gpio))
                fluxo = Monitor_fluxo()
                GPIO.setup(monitor.gpio, GPIO.IN, pull_up_down=GPIO.PUD_UP)
                GPIO.add_event_detect(monitor.gpio,
                                    GPIO.RISING,
                                    callback=fluxo.pulseCallback,
                                    bouncetime=20)
                lista.append(fluxo)
        except:
            tb = traceback.print_exc()
            Log.error('_config_fluxo: '+tb)

        #print('tamanho lista fluxo: %s' % len(lista))
        return lista



    def executar(self):
        
        dados_coletados = None
        _ignicao_inicial = True
        tempo_captura = datetime.now() + timedelta(0, self._tempo_config)
        
        while self._loop_execucao:
            #print('_is_desligado: '+str(self._is_desligado))    
            dados = self._gps.executar()
            print('Monitor dados gps: '+str(dados))
            agora = datetime.now()

            if self._ignicao == False:
                self._loop_execucao = False

            if agora > tempo_captura and dados != None:
                dados_coletados = DadosColetados()
                dados_coletados.razao = DadosColetados.sem_ocorrencia()

                dados_coletados.latitude, dados_coletados.longitude, dados_coletados.velocidade, dados_coletados.sentido, dados_coletados.data_hora = dados
                
                if _ignicao_inicial:
                    dados_coletados.razao = DadosColetados.ignicao()
                    _ignicao_inicial = False
                    
                print('executar: monitor ignicao: '+str(self._ignicao))
                if self._ignicao == False:
                    self._ignicao = None
                    dados_coletados.razao = DadosColetados.desligamento()
                    print('dados coletados: '+str(dados_coletados.razao))
                    
                
                fluxo1 = self._medidores_fluxo[0]    
                str_fluxo = str(fluxo1.taxa_fluxo())
                dados_coletados.fluxo1 = str_fluxo

                fluxo2 = self._medidores_fluxo[1]
                str_fluxo = str(fluxo2.taxa_fluxo())
                dados_coletados.fluxo2 = str_fluxo

                
                
                dados_coletados.save()
                    
                tempo_captura = datetime.now() +  timedelta(0, self._tempo_config)
                

                

    def _limpar_gpio(self):
        for medidor in self._config.medidores_fluxo:
            GPIO.cleanup(medidor.gpio)

    def parar(self):
        self._loop_execucao = False
        self._gps._fechar_serial()
        self._limpar_gpio()

    def iniciar(self):
        self._loop_execucao = True

class Monitor_gps():

    def __init__(self, gps):
        self._gps = gps
        self._serialPort = None                
        self._existe_dados = False
        self._dados_gps = None
        self._iniciar_serial()

    def executar(self):        
        try:
            linha_serial = self._serialPort.readline()
            linha_rmc = linha_serial.decode('ascii')
            #print('linha: '+linha_rmc)
            
            gp = linha_rmc[0:6]
            try:        
                if gp == '$GPRMC':
                    self._dados_gps = self._tratar_dados(linha_rmc)
                    #print('RMC: '+linha_rmc)
            except IndexError:
                tb = traceback.format_exc()
                Log.error('Não a dados do GPS: '+tb)
                        
        except UnicodeDecodeError:
            self._fechar_serial()
            sleep(2)
            self._iniciar_serial()
            tb = traceback.format_exc()
            Log.error('Erro no encode do GPS: '+tb)
        except ValueError:
            pass
            #tb = traceback.format_exc()
            #Log.error('Erro de conversao na base 10: '+tb)
            

        return self._dados_gps

    def _iniciar_serial(self):
        Log.info('_iniciar_serial')
        self._serialPort = serial.Serial(self._gps.porta, self._gps.baud, timeout=self._gps.timeout)

    def _fechar_serial(self):
        Log.info('_fechar_serial')
        self._serialPort.close()
        self._serialPort = None                


    def _tratar_dados(self, linha):
        
        dados = None
        
        dados_gps = linha.split(",")
        hora    = dados_gps[1]
        dia     = dados_gps[9]
        knot    = dados_gps[7]
        lat     = dados_gps[3]
        lon     = dados_gps[5]
        sentido = dados_gps[8]

        data_hora = datetime(int('20'+dia[4:6]), int(dia[2:4]), int(dia[0:2]), 
                                int(hora[0:2]), int(hora[2:4]), int(hora[4:6]))
        
        if lat[0] == '0':
            latitude = '-' + lat[1:]
        else:
            latitude = '-' + lat

        if lon[0] == '0':
            longitude = '-' + lon[1:]
        else:
            longitude = '-' + lon


        ###Transformar knot em km/h##
        
        k = float(knot)

        metros_segundos = float(k * 0.5)
        km_hora =round(float(metros_segundos * 3.6),2)
        str_km_hora = str(km_hora)

        ###---------------------------------###

       
        if latitude != '' and longitude != '':

            lat_decimais = latitude[-8:]
            lat_graus = latitude[0:2]

            lat_decimais_f = float(lat_decimais) / 60
            lat_graus_f = float(lat_graus)

            if lat_graus_f < 0:
                lat_decimais_f = lat_decimais_f * (-1)
            
            lat_graus_f = lat_graus_f + lat_decimais_f

            lng_decimais = longitude[-8:]
            lng_graus = longitude[0:3]

            lng_decimais_f = float(lng_decimais) / 60
            lng_graus_f = float(lng_graus)

            if lng_graus_f < 0:
                lng_decimais_f = lng_decimais_f * (-1)

            lng_graus_f = lng_graus_f + lng_decimais_f

            dados = (round(lat_graus_f, 6), round(lng_graus_f, 6), str_km_hora, sentido, data_hora)
            self._existe_dados = True

        return dados    
    

class Monitor_fluxo():

    def __init__(self):
        self._taxa_fluxo = 0.0
        self._ultimo_tempo = datetime.now()

    def pulseCallback(self, p):
        
        tempo_corrente = datetime.now()
        diferenca = (tempo_corrente - self._ultimo_tempo).total_seconds()

        frequencia = 1. / diferenca
        self._taxa_fluxo = (frequencia / 7.5)

        self._ultimo_tempo = tempo_corrente

    
    def taxa_fluxo(self):
        
        if (datetime.now() - self._ultimo_tempo).total_seconds() > 1:
            self._taxa_fluxo = 0.0
            


        return round(self._taxa_fluxo,2)


class SensorThread(Thread):

    def __init__(self, config):
        Thread.__init__(self)
        self._config = config
        self._loop = True
        self._ligado = True
        self._sensores = Sensores(self._config)

    def run(self):
        Log.info('Iniciando sensores da placa')
        while self._loop:
            if self._sensores.is_ignicao() == 0:
                # ignicao do veiculo desligada
                self._ligado = False
            else:
                # ignicao do veiculo ligada
                self._ligado = True
            time.sleep(self._config.loop_checagem)

    def parar(self):
        Log.info('Parando sensores da placa')
        self._sensores.limpar_gpio()
        self._loop = False

    def is_ignicao(self):
        return self._ligado

    def descarregar_capacitor(self):
        self._sensores.descarga_capacitor()

    def desligar_placa(self):
        self._sensores.desliga_placa()
        


class Sensores():
    
    def __init__(self, config):
        
        self._config = config
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(config.sensor_ignicao, GPIO.IN)
        GPIO.setup(config.capacitor, GPIO.OUT)
        GPIO.setup(config.desliga_placa, GPIO.OUT)



    def is_ignicao(self):
        return GPIO.input(self._config.sensor_ignicao)

    def descarga_capacitor(self):
        GPIO.output(self._config.capacitor, GPIO.HIGH)

    def desliga_placa(self):
        GPIO.output(self._config.desliga_placa, GPIO.HIGH)

    def limpar_gpio(self):
        GPIO.cleanup([self._config.sensor_ignicao, self._config.capacitor, self._config.desliga_placa])


class Transmissao():

    def __init__(self, config):
        self._host = config['servidor']
        self._path_envio = config['url_envio']
        self._tempo_espera_envio = int(config['tempo_espera_envio'])
        self._loop = True
        self._url = 'http://'+ self._host + self._path_envio



    def _status_servidor(self):
        ping = subprocess.Popen(['ping', '-c', '1', self._host], stdout = subprocess.PIPE, stderr = subprocess.PIPE)
        out, error = ping.communicate()
        
        saida = out.decode()
        resultado = saida.find('100% packet loss')

        if resultado == -1:
            resposta = True
        else:
            resposta = False

        return resposta

    def _transmitir(self, dados):
        print('_transmitir')
        md5 = dados['md5']
        path_arquivo = dados['arquivo']

        formulario = {}
        formulario['md5'] = md5

        session = requests.session()
        headers = {
                    'origin': 'http://35.199.78.129/posicoes',
                    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36"
                    }

        form = session.get(self._url, headers=headers)
        
        #csrf_token = re.findall(r'<input type="hidden" name="_token" value="(.*)"', form.text)[0]

        #print('_token: '+csrf_token)
        
        #formulario['_token'] = csrf_token
                
        files = {'jsonFile': open(path_arquivo, 'rb')}

        
        response = session.post(self._url, files=files, data=formulario)
        Log.info('_transmitir: enviando dados')
        return response

    # verifica se o servidor esta online e envia os dados
    # caso o servidor responda com um numero maior que 0 e atualizado a flag transmitida no banco
    def posicoes(self, dados_envio):

        tempo_loop = datetime.now() + timedelta(0, int(self._tempo_espera_envio))

        while self._loop:

            if self._status_servidor():
                response = self._transmitir(dados_envio)
                resposta = int(response.text)
                

                if resposta > 0:
                    
                    self._sucesso(dados_envio)
                    Log.info('loop_envio: posicoes enviadas com sucesso')
                    self._loop = False

            
            agora = datetime.now()            
            if agora > tempo_loop:
                self._loop = False
            
            sleep(20)

    
    # prepara a lista de ids para alterar a flag de transmitido
    def _sucesso(self, dados_enviados):
        banco = DadosColetados()        
        
        arquivo = open(dados_enviados['arquivo'], 'r')
        dados = arquivo.read()
        _json = json.loads(dados)


        conteudo = _json['conteudo']
        transmitidos = []
        for linha in conteudo:
            str_id = linha['id']
            id = int(str_id)
            transmitido = {'id':id,'transmitido':1} 
            transmitidos.append(transmitido)

        
        try:
            banco.transmitidos_sucesso(transmitidos)
            Log.info('Dados enviados com sucesso ao servidor')
        except:
            tb = traceback.format_exc()
            Log.error('_sucesso_envio: '+tb)




class ThreadTransmissao(Thread):

    def __init__(self, config, arquivo):
        Thread.__init__(self)
        self._transmissao = Transmissao(config)
        self._arquivo = arquivo

    def run(self):
        self._transmissao.posicoes(self._arquivo)

    def parar(self):
        self._transmissao._loop = False


class Desligar():

    def __init__(self):
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(32, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(22, GPIO.OUT)
        GPIO.setup(19, GPIO.OUT)

    def agora(self):
        GPIO.output(22, GPIO.HIGH)
        sleep(2)
        GPIO.output(19, GPIO.HIGH)
        GPIO.cleanup()

    


            








    


        

