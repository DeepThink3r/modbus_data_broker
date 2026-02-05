# modbus_data_broker
Esse projeto consiste na criação de um servidor modbus que irá gerar dados fictícios de sensores, um client python/producer que enviará dados para um broker no Postgres que notificará um consumer.py que, além de consumir os dados, irá carrega-los em um modelo semântico streaming do Power BI.

## Subir o Container do Servidor Modbus

Execute o comando `docker build -t modbus_server_caldeira . ` no terminal para subir a imagem.

Em seguida execute as seguintes instruções:

```
docker run -d \
  --name modbus_caldeira \
  --network ambiente_modbus \
  -p 5020:5020 \
  modbus_server_caldeira
```

## Subindo Banco de Dados
O postgres será utilizado como um broker usando um recurso nativo chamado LISTEN/NOTIFY

```bash
docker run -d \
--name pg_broker \
--network ambiente_modbus \
-p 5431:5432 \
-e POSTGRES_PASSWORD=postgres \
-v postgredb:/var/lib/postgresql/18/main\
-d postgres
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
```sql
CREATE DATABASE modbus_broker;
```

### Configurando Broker no Postgres

1. Criar tabela para armazenar histórico dos dados recebidos pelo producer.py

```sql
CREATE TABLE IF NOT EXISTS leituras_caldeira (
    id SERIAL PRIMARY KEY,
    temperatura REAL NOT NULL,
    pressao REAL NOT NULL,
    data_leitura TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);
```
2. Criar função que envia a notificação. Caso não haja nenhum aplicativo ou serviço escutando, o postgres simplesmente elimina a notificação.

```sql
CREATE OR REPLACE FUNCTION notificar_nova_leitura()
RETURNS TRIGGER AS $$
DECLARE
    payload JSON;
BEGIN
    -- Cria um JSON com os dados que acabaram de chegar
    payload = json_build_object(
        'id', NEW.id,
        'temperatura', NEW.temperatura,
        'pressao', NEW.pressao,
        'timestamp', NEW.data_leitura
    );

    -- Envia a notificação no canal 'novas_leituras'
    -- O payload precisa ser convertido para texto
    PERFORM pg_notify('novas_leituras', payload::text);

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
```

3. Criar trigger que dispara a função toda vez que houver uma inserção na tabela.

```sql
CREATE TRIGGER trg_notifica_leitura
AFTER INSERT ON leituras_caldeira
FOR EACH ROW
EXECUTE FUNCTION notificar_nova_leitura();
```
