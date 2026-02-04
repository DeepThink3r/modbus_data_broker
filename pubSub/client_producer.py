from pyModbusTCP.client import ModbusClient
import time


cliente = ModbusClient(host='127.0.0.1', port=5020)

def coletar_e_enviar():

    regs = cliente.read_holding_registers(0, 2)
    
    if regs:
        temp_bruta = regs[0]
        pressao_bruta = regs[1]
        
        temp_final = temp_bruta / 10.0
        pressao_final = pressao_bruta / 100.0
        
        print(f"Lido do Modbus -> Temp: {temp_final}°C | Pressão: {pressao_final} bar")
        
        # AQUI VOCÊ CHAMA SUA FUNÇÃO DO POSTGRES
        # inserir_no_postgres(temp_final, pressao_final) 
    else:
        print("Falha na leitura do Servidor Modbus")

if __name__ == "__main__":
    print("Iniciando Coletor (Master)...")
    while True:
        coletar_e_enviar()
        time.sleep(5) # Coleta a cada 5 segundos