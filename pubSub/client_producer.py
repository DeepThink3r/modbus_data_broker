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
    'port': '5432'
}

cliente = ModbusClient(host='localhost', port=5020, auto_open=True)

def inserir_no_postgres(temp, pressao):
    conn = None
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        sql = "INSERT INTO leituras_caldeira (temperatura, pressao) VALUES (%s, %s)"
        cursor.execute(sql, (temp, pressao))
        
        conn.commit()
        cursor.close()
        print(f"Salvo no DB ID: (Temp: {temp}, Press: {pressao})")
        
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Erro no PostgreSQL: {error}")
    finally:
        if conn is not None:
            conn.close()

def coletar_e_enviar():
    # Tenta ler os registradores (endereços 0 e 1)
    regs = cliente.read_holding_registers(0, 2)
    
    if regs:
        temp_bruta = regs[0]
        pressao_bruta = regs[1]
        
        temp_final = temp_bruta / 10.0
        pressao_final = pressao_bruta / 100.0
        
        print(f"Modbus -> Temp: {temp_final}°C | Pressão: {pressao_final} bar")
        
        inserir_no_postgres(temp_final, pressao_final) 
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