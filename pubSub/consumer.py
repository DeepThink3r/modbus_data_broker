import os
from dotenv import load_dotenv
import psycopg2
import select
import json

load_dotenv()

# Conexão com o banco
DB_CONFIG = {
    'dbname': os.getenv('DB_NAME'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASS'),
    'host': 'localhost',       
    'port': '5432'
}

def iniciar_consumidor():
    conn = psycopg2.connect(**DB_CONFIG)
    conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)

    cursor = conn.cursor()
    
    # Se inscreve no canal que definimos no SQL
    cursor.execute("LISTEN novas_leituras;")

    try:
        while True:
            # O select bloqueia o script até chegar uma notificação (ou timeout de 5s)
            if select.select([conn], [], [], 5) == ([], [], []):
                pass
            else:
                conn.poll()
                while conn.notifies:
                    notify = conn.notifies.pop(0)
                    
                    # Converte o payload de texto para JSON Python
                    dados = json.loads(notify.payload)
                    
                    print(f"\n NOTIFICAÇÃO RECEBIDA!")
                    print(f"   Canal: {notify.channel}")
                    print(f"   Temp: {dados['temperatura']}°C")
                    print(f"   Pressão: {dados['pressao']} bar")

    except KeyboardInterrupt:
        print("\n Parando consumidor...")
    finally:
        conn.close()

if __name__ == "__main__":
    iniciar_consumidor()