## Comandos utilizados

````CLI
brew install dapr/tap/dapr-cli
dapr init
dapr run --app-id publisher-caldeira --dapr-http-port 3500 --resources-path ./components -- python3 -u producer.py
```

