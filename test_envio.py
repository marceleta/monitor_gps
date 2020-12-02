from configuracao import Config
from arquivo import Arquivo, EnvioWeb
from modelos import DadosColetados
import json
config = Config() 
lista = DadosColetados.nao_enviados()

resposta = {
            "id_monitor":config.id_monitor(),
            "resposta":"list_por_data",
            "conteudo":lista
        }

arquivo = Arquivo.criar_arquivo(resposta)
print(str(arquivo))

dados_servidor = config.servidor_envio()
endereco = dados_servidor['servidor']

envio = EnvioWeb(endereco)
print(envio.status_servidor())

r = envio.enviar(arquivo, dados_servidor['url_envio'])