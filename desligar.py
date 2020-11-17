import sys
from time import sleep
import json

file = open('configuracao.json', 'r')
json_object = json.load(file)
file.close()

json_object['desliga_geo_sensor']['desliga'] = 1

file = open('configuracao.json','w')
json.dump(json_object, file)
file.close()

sleep(40)

file = open('configuracao.json', 'r')
json_object = json.load(file)
file.close()

json_object['desliga_geo_sensor']['desliga'] = 0

file = open('configuracao.json','w')
json.dump(json_object, file)
file.close()


'''
arquivo = open('configuracao.json')
_json = json.load(arquivo)
dados = _json['desliga_geo_sensor']
dados['desliga'] = 1
arquivo.flush()
arquivo.close()
'''