import socket
import json
from datetime import datetime
from modelos import DadosColetados
from util import Conversor
from servicos import Monitor_gps, ThreadColetaDados, ThreadPersistir, Monitor

class conexao():

        @staticmethod
        def envia_comando(string):
                mensagem = json.dumps(string)

                cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                cliente.connect(('localhost', 6000))
                cliente.send(mensagem.encode('utf-8'))
                recebi = cliente.recv(4096)
                cliente.close()

                return recebi.decode('utf-8')

class teste_sistema():
        
        def desligar(self):
                comando = {
                        'comando':'parar_servico'
                }
                recebi = conexao.envia_comando(comando)
                print(recebi)

        def conversor(self):
                data_inicio = '15/04/2020 8:00'
                data_final = '15/04/2020 10:00'

                inicio = Conversor.str_para_datetime(data_inicio)
                final = Conversor.str_para_datetime(data_final)

                print('data_inicio: '+inicio)
                print('data_final: '+final)

        

class teste_consultas():

    def lista_por_intervalo(self):
        data_inicio = '14/04/2020 8:00'
        data_final = '15/04/2020 8:00'
        recebi =  DadosColetados.por_intervalo(data_inicio, data_final)
        print('lista_por_intervalo: '+str(recebi))


        data_inicio = '14/04/2020 8:00'
        data_final = '15/04/2020 8:00'
        comando = {
                'comando': 'lst_por_data',
                'data_inicio': data_inicio,
                'data_final':data_final
        }

        recebi = conexao.envia_comando(comando)

        f = open('saida_teste_consultas.txt','w')
        f.write(recebi)
        f.close()

class Teste_gps():

        def __init__(self):
                pass

        def teste_monitor_gps(self):
                monitor_gps = Monitor_gps()
                dados = monitor_gps.executar()
                print('dados: '+str(dados))

class Teste_tread_coletadados():

        def __init__(self):
                self._thread = ThreadColetaDados()
                

        def teste_thread(self):
                self._thread.start()

class Teste_thread_persistir():

        def __init__(self):
                self.monitor = Monitor()
                self._thread_coleta = ThreadColetaDados()
                self._thread_persistir = ThreadPersistir()

        def teste_thread(self):
                self._thread_coleta.start()
                self._thread_persistir.start()




##Execução dos Testes
#teste = teste_sistema()
#teste.conversor()
#teste = teste_consultas()
#teste.lista_por_intervalo()
#teste_gps = Teste_gps()
#teste_gps.teste_monitor_gps()
thread_coleta = Teste_tread_coletadados()
thread_coleta.teste_thread()
#thead_persistir = Teste_thread_persistir()
#thead_persistir.teste_thread()



