import os
from dotenv import load_dotenv
from pyModbusTCP.client import ModbusClient
import psycopg2
import time

load_dotenv()

DB_CONFIG = {
    'dbname': os.getenv('DB_NAME'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASS'),
    'host': 'localhost',
    'port': '5431'
}

cliente = ModbusClient(host='localhost', port=5020, auto_open=True)


def inserir_no_postgres(temp, pressao, vazao):
    conn = None
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        sql = "INSERT INTO leituras_caldeira (temperatura, pressao, vazao) VALUES (%s, %s, %s)"
        cursor.execute(sql, (temp, pressao, vazao))

        conn.commit()
        cursor.close()
        print(f"Salvo no DB ID: (Temp: {temp}, Press: {pressao}, Vazao: {vazao})")

    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Erro no PostgreSQL: {error}")
    finally:
        if conn is not None:
            conn.close()


def coletar_e_enviar():
    # Tenta ler os registradores (endereços 0 a 3)
    regs = cliente.read_holding_registers(0, 3)

    if regs:
        temp_bruta = regs[0]
        pressao_bruta = regs[1]
        vazao_bruta = regs[2]


        temp_final = temp_bruta / 10.0
        pressao_final = pressao_bruta / 100.0
        vazao_final = vazao_bruta / 10.0

        print(f"Modbus -> Temp: {temp_final}°C | Pressão: {pressao_final} bar | Vazao: {vazao_final} m³/min")

        inserir_no_postgres(temp_final, pressao_final, vazao_final)
    else:
        print("Falha na leitura do Servidor Modbus")


if __name__ == "__main__":
    print("Iniciando Coletor (Producer)...")
    print("Pressione Ctrl+C para parar")

    try:
        while True:
            coletar_e_enviar()
            time.sleep(5)
    except KeyboardInterrupt:
        print("\n Encerrando coletor...")
        cliente.close()
