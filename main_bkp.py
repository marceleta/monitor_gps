from servidor import Servidor


host = 'localhost'
port = 6000
listen = 3

servidor = Servidor(host,port, listen)
servidor.iniciar()



