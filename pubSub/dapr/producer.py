import os
import time
import logging
from fastapi import FastAPI
import requests
from pyModbusTCP.client import ModbusClient

# FastAPI para fazer o post no Dapr
app = FastAPI()


#Configuração de logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

#Variáveis globais
DAPR_PORT = os.getenv("DAPR_HTTP_PORT", "3500")
PUBSUB_NAME = "industrial-pubsub"
TOPIC_NAME = "leituras-caldeira"
DAPR_URL = f"http://localhost:{DAPR_PORT}/v1.0/publish/{PUBSUB_NAME}/{TOPIC_NAME}"

# Cliente modbus
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
            logging.info(f"Publicado no Dapr: {payload}")
        else:
            logging.error(f"Erro no Dapr: {response.text}")
    except Exception as e:
        logging.error(f"Erro de conexão com Sidecar: {e}")


def coletar_e_enviar():
    regs = cliente.read_holding_registers(0, 3)
    if regs:
        temp_final = regs[0] / 10.0
        pressao_final = regs[1] / 100.0
        vazao_final = regs[2] / 10.0
        
        # O trabalho do Publisher termina aqui
        publicar_no_dapr(temp_final, pressao_final, vazao_final)
    else:
        logging.error("Falha na leitura Modbus")


@app.post("/agendador-caldeira")
def trigger_event():
    logging.info("Sinal de agendamento recebido do Dapr.")
    coletar_e_enviar()

    return {"status": "coleta_iniciada"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)