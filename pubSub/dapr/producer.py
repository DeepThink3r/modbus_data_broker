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


def coletar_e_enviar():
    regs = cliente.read_holding_registers(0, 3)
    if regs:
        temp_final = regs[0] / 10.0
        pressao_final = regs[1] / 100.0
        vazao_final = regs[2] / 10.0
        
        # O trabalho do Publisher termina aqui
        publicar_no_dapr(temp_final, pressao_final, vazao_final)
    else:
        print("Falha na leitura Modbus")

if __name__ == "__main__":
    try:
        while True:
            coletar_e_enviar()
            time.sleep(5)
    except KeyboardInterrupt:
        cliente.close()