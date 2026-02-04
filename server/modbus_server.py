from pyModbusTCP.server import DataBank, ModbusServer
from time import sleep
import random

class ServidorCaldeira():

    def __init__(self, host_ip, port):
        self._db = DataBank()
        self._server = ModbusServer(host=host_ip, port=port, no_block=True, data_bank=self._db)

    def execute(self):
        try:
            self._server.start()
            print(f"Servidor Caldeira ativo em {self._server.host}:{self._server.port}")

            while True:
                # Usando endereços 0 e 1 (que o Master lerá como 40001 e 40002)
                temp = random.randint(800, 900)
                self._db.set_holding_registers(0, [temp])

                pressao = random.randint(200, 250)
                self._db.set_holding_registers(1, [pressao])

                print('----STATUS DA CALDEIRA----')
                print(f'Temp (40001): {temp/10.0} °C')
                print(f'Pressao (40002): {pressao/100.0} bar')
                print('--------------------------')

                sleep(3)

        except Exception as erro:
            print("Erro na execução do servidor:", erro)
            self._server.stop()
