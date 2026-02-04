from modbus_server import ServidorCaldeira

srv = ServidorCaldeira(host_ip='127.0.0.1', port=5020)
srv.execute()