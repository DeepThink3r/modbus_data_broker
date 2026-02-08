import asyncio
import asyncpg
import httpx
import json
import os
from fastapi import FastAPI
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Configurações do ambiente
PBI_ENDPOINT = os.getenv('PBI_ENDPOINT_URL')
DB_URL = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASS')}@localhost:5431/{os.getenv('DB_NAME')}"

# Função que envia o dado para o Power BI


async def enviar_para_power_bi(dados_json):
    async with httpx.AsyncClient() as client:
        try:
            # O payload costuma vir como string do NOTIFY, convertemos para dict
            payload = json.loads(dados_json)

            # Power BI Streaming Dataset espera uma lista [{}, {}]
            response = await client.post(PBI_ENDPOINT, json=[payload])
            print(f"Power BI Atualizado: {payload}")

        except Exception as e:
            print(f"Erro ao processar notificação: {e}")

# Callback que é executado toda vez que o NOTIFY chega
def notificacao_recebida(connection, pid, channel, payload):
    # Criamos uma tarefa para não travar a conexão com o banco
    asyncio.create_task(enviar_para_power_bi(payload))


async def escutar_postgres():
    conn = await asyncpg.connect(DB_URL)

    # Ativa o LISTEN no canal que sua trigger utiliza
    await conn.add_listener('novas_leituras', notificacao_recebida)

    print("👂 Escutando canal 'novas_leituras' no Postgres...")

    # Mantém a task viva enquanto o app rodar
    while True:
        await asyncio.sleep(1)


@app.on_event("startup")
async def startup_event():
    # Inicia a escuta do banco de dados em segundo plano assim que o FastAPI sobe
    asyncio.create_task(escutar_postgres())


@app.get("/status")
async def status():
    return {"status": "operacional", "monitorando": "novas_leituras"}

if __name__ == "__main__":
    import uvicorn
    # Rodando o servidor
    uvicorn.run(app, host="127.0.0.1", port=5000)
