# modbus_data_broker
Esse projeto consiste na criação de um servidor modbus que irá gerar dados fictícios de sensores, um client python/producer que enviará dados para um broker no Postgres que notificará um consumer.py que, além de consumir os dados, irá carrega-los em um modelo semântico streaming do Power BI
