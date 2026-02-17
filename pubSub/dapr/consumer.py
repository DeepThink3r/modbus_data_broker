import httpx
import os
import uvicorn
from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

PBI_ENDPOINT = os.getenv('POWER_BI_URL')

@app.get("/dapr/subscribe")
async def subscribe():
    return [{
        "pubsubname": "industrial-pubsub",
        "topic": "leituras-caldeira",
        "route": "/processar-leituras"
    }]


@app.post("/processar-leituras")
async def processar_leituras(event = Body(...)):
    leituras = event.get("data")

    if leituras:

        agora = datetime.now() 
        
        timestamp_pbi = agora.isoformat()

        payload_pbi = [
            {
                "40001_Temp": float(leituras.get('temperatura', 0)),
                "40002_Pressao": float(leituras.get('pressao', 0)),
                "40003_vazao": float(leituras.get('vazao', 0)),
                "timestmp": timestamp_pbi
            }
        ]

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(PBI_ENDPOINT, json=payload_pbi)
                if response.status_code == 200:
                    print(f"Enviado: {timestamp_pbi} | Status: {response.status_code}", flush=True)
                else:
                    print(f"Erro PBI: {response.status_code} - {response.text}", flush=True)
            except Exception as e:
                print(f"Falha de rede: {e}", flush=True)

    return {"status": "SUCCESS"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5001)