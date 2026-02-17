import os
import time
import requests # Usamos requests para falar com o Sidecar
from pyModbusTCP.client import ModbusClient

#Variáveis globais

DAPR_PORT = "3500"
PUBSUB_NAME = "industrial-pubsub"
TOPIC_NAME = "leituras_caldeira"
DAPR_URL = f"http://localhost:{DAPR_PORT}/v1.0/publish/{PUBSUB_NAME}/{TOPIC_NAME}"

cliente = ModbusClient(host='localhost', port=5020, auto_open=True)

def publicar_no_dapr(temp, pressao, vazao):
    payload = {
        "temperatura": temp,
        "pressao": pressao,
        "vazao": vazao
    }
    try:
        # Enviamos para o SIDECAR, não para o banco
        response = requests.post(DAPR_URL, json=payload)
        if response.status_code == 204:
            print(f"Publicado no Dapr: {payload}")
        else:
            print(f"Erro no Dapr: {response.text}")
    except Exception as e:
        print(f"Erro de conexão com Sidecar: {e}")