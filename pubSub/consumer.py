import os
import requests
import json
import select
import psycopg2
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

POWER_BI_URL = os.getenv('POWER_BI_URL')

DB_CONFIG = {
    'dbname': os.getenv('DB_NAME'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASS'),
    'host': 'localhost',
    'port': '5431'
}

def enviar_ao_powerbi(dados):

    agora = datetime.now()
    
    timestamp_pbi = agora.strftime('%d/%m/%Y %H:%M:%S')
        
    payload = [
        {
            "40001_Temp": float(dados['temperatura']),
            "40002_Pressao": float(dados['pressao']),
            "40003_vazao": float(dados['vazao']),
            "timestmp": timestamp_pbi
        }
    ]
    
    try:
        response = requests.post(POWER_BI_URL, json=payload)
        if response.status_code == 200:
            print(f"Dados enviados ao Power BI")
        else:
            print(f"Erro Power BI: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Falha na requisição: {e}")

def iniciar_consumidor():
    conn = psycopg2.connect(**DB_CONFIG)
    conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()

    cursor.execute("LISTEN novas_leituras;")
    print("Aguardando notificações no canal 'novas_leituras'...")

    try:
        while True:
            # Espera por eventos no socket da conexão
            if select.select([conn], [], [], 5) == ([], [], []):
                # Timeout de 5s sem notificações (útil para manter o loop vivo)
                continue
            
            conn.poll()
            while conn.notifies:
                notify = conn.notifies.pop(0)
                
                # O payload vem como string do Postgres, convertemos para dicionário
                dados_recebidos = json.loads(notify.payload)
                
                print(f"\n Notificação recebida: {dados_recebidos}")
                
                # Chamada da função de envio
                enviar_ao_powerbi(dados_recebidos)

    except KeyboardInterrupt:
        print("\n Parando consumidor...")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    iniciar_consumidor()