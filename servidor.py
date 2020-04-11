import socket
import selectors
import logging
import time
import threading
import sys
from datetime import datetime

from controle import Controle
from util import Log

class Servidor():

    def __init__(self, host, port, listen):
        self.main_socket = socket.socket()
        self.main_socket.bind((host, port))
        self.main_socket.listen(100)
        self.main_socket.setblocking(False)

        self.selector = selectors.DefaultSelector()
        self.selector.register(fileobj=self.main_socket,
                                events=selectors.EVENT_READ,
                                data=self.on_accept)

        self.current_peers = {}
        self._loop_servidor = True

        self._controle = Controle()


    def on_accept(self, sock, mask):
        conn, addr = self.main_socket.accept()
        conn.setblocking(False)

        self.current_peers[conn.fileno()] = conn.getpeersname()
        self.selector.register(fileobj=conn, events=selectors.EVENT_READ,
                                data=self.on_read)

    
    def on_read(self, conn, mask):
        try:
            data = conn.recv(1024)
            
            if data:
                self._controle.exec_mensagem(data)
                conn.send(self._controle.resposta())

                if self._controle.cont_rodando_serv():
                    self._finaliza_servidor()

            else:
                self._fechar_conexao(conn)

        except ConnectionResetError:
            self._fechar_conexao(conn)

    def _finaliza_servidor(self):
        self._loop_servidor = False
        self.selector.close()
        sys.exit()        

    def _fechar_conexao(self, conn):
        peername = self.current_peers[conn.fileno()]
        del self.current_peers[conn.fileno()]
        self.selector.unregister(conn)
        conn.close()


    def _rodar_servidor(self):
        log = 'Iniciado loop do servidor'
        Log.info(log)

        while self._loop_servidor:
            eventos = self.selector.select(timeout=0.2)
            for key, mask in eventos:
                handler = key.data
                handler(key.fileobj, mask)


    def iniciar_servidor(self):
        Log.info('Iniciando thread do servidor')
        self.thread = threading.Thread(target=self._rodar_servidor)
        self.thread.start()

        
    




