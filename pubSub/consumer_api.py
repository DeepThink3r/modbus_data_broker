import asyncio
import asyncpg
import httpx
import json
import os
from fastapi import FastAPI
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

app = FastAPI()

PBI_ENDPOINT = os.getenv('POWER_BI_URL')
DB_URL = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASS')}@localhost:5431/{os.getenv('DB_NAME')}"

async def enviar_para_power_bi(dados_json):
    async with httpx.AsyncClient() as client:
        try:

            dados = json.loads(dados_json)

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

            await client.post(PBI_ENDPOINT, json=payload)
            print(f"Power BI Atualizado: {payload}")

        except Exception as e:
            print(f"Erro ao processar notificação: {e}")

def notificacao_recebida(connection, pid, channel, payload):
    # Criamos a tarefa assíncrona para o envio
    asyncio.create_task(enviar_para_power_bi(payload))

async def escutar_postgres():
    conn = await asyncpg.connect(DB_URL)
    await conn.add_listener('novas_leituras', notificacao_recebida)
    print("Escutando canal 'novas_leituras' no Postgres...")
    
    while True:
        await asyncio.sleep(1)

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(escutar_postgres())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=5000)