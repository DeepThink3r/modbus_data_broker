# modbus_data_broker
Esse projeto consiste na criação de um servidor modbus que irá gerar dados fictícios de sensores, um client python/producer que enviará dados para um broker no Postgres que notificará um consumer.py que, além de consumir os dados, irá carrega-los em um modelo semântico streaming do Power BI.

## Subindo Banco de dados
O postgres será utilizado como um broker usando um recurso nativo chamado LISTEN/NOTIFY

```bash
docker run -d \
--name pg_broker \
--network ambiente_modbus \
-p 5431:5432 \
-e POSTGRES_PASSWORD=postgres \
-v postgredb:/var/lib/postgresql/data
```
Em seguida, na guia _exec_ do container, execute os seguintes comandos:

```bash
psql -U postgres -d postgres
```

Agora crie uma role para um usuário específico de serviço para o broker no banco:

```sql
CREATE ROLE pgbroker WITH LOGIN PASSWORD 'pgbroker';
ALTER ROLE pgbroker SUPERUSER;
```
⭐️ Para fins didáticos, atribuiremos a role de SUPERUSER ao usuário. Mas em produção, ele deverá ter somente os privilégios para executar as atividades necessárias.

Criar o banco de dados:
```
CREATE DATABASE modbus_broker;
```



