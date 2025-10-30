# Dicionário Vetorial API

API REST para busca semântica em dicionário usando embeddings e Qdrant.

## Estrutura do Projeto

```
dicionario_vetorial/
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── README.md
├── api/
│   ├── __init__.py                # Pacote principal da API
│   ├── dicionarioAPI.py          # Endpoints REST
│   ├── models.py                 # Modelos Pydantic
│   └── config.py                 # Configurações da aplicação
└── services/
    ├── __init__.py
    └── dicionarioService.py      # Lógica de negócio
```

## Como Executar

### Usando Docker Compose (Recomendado)

```bash
# Constrói e inicia todos os serviços automaticamente
docker-compose up --build

# Parar os serviços
docker-compose down
```

**O que o Docker faz automaticamente:**
- Instala todas as dependências Python
- Configura o ambiente Qdrant
- Carrega o modelo SentenceTransformer
- Inicia a API na porta 9000

A API estará disponível em: `http://localhost:9000`

### Executando Localmente (Desenvolvimento)

**Para desenvolvimento sem Docker:**

1. Certifique-se de ter Python 3.11+ instalado

2. Execute o Qdrant via Docker:
```bash
docker run -p 6333:6333 qdrant/qdrant:v1.11.3
```

3. Instale as dependências Python:
```bash
pip install -r requirements.txt
```

4. Execute a API:
```bash
python -m api.dicionarioAPI
```

**Observação:** O método recomendado é usar `docker-compose up --build` que configura automaticamente todo o ambiente.

## Endpoints da API

### GET `/`
Informações básicas da API e lista de endpoints disponíveis.

### GET `/status`
Verifica o status da conexão com o Qdrant e se o modelo está carregado.

### GET `/estatisticas`
Obtém estatísticas da coleção.

### POST `/buscar`
Busca palavras semanticamente similares a uma query.

**Body:**
```json
{
  "query": "local onde alguém vive",
  "limit": 5
}
```

**Resposta:**
```json
{
  "query": "local onde alguém vive",
  "resultados": [
    {
      "palavra": ["casa", "local onde alguém mora"],
      "score": 0.8945
    },
    {
      "palavra": ["moradia", "local onde alguém mora, casa, residência"],
      "score": 0.8723
    }
  ]
}
```

### POST `/adicionar`
Adiciona uma nova palavra ao dicionário.

**Body:**
```json
{
  "palavra": "cachorro",
  "definicao": "animal doméstico quadrúpede da família dos canídeos"
}
```

**Resposta:**
```json
{
  "message": "Palavra adicionada com sucesso",
  "palavra": "cachorro",
  "definicao": "animal doméstico quadrúpede da família dos canídeos",
  "id": 13
}
```

## Documentação Interativa

A API possui documentação Swagger/OpenAPI completa e interativa:

- **Swagger UI**: `http://localhost:9000/docs`
  - Interface interativa para testar endpoints
  - Documentação detalhada de cada operação
  - Exemplos de requisições e respostas
  - Validação de schemas em tempo real

- **ReDoc**: `http://localhost:9000/redoc`
  - Documentação alternativa mais focada em leitura
  - Layout otimizado para consulta
  - Melhor para entender a API como um todo

### Recursos da Documentação

- **Tags organizadas**: Endpoints agrupados por funcionalidade
- **Exemplos completos**: Requests e responses de exemplo
- **Validação automática**: Schemas Pydantic com validação
- **Descrições detalhadas**: Cada endpoint com explicação completa
- **Códigos de status**: Documentação de todos os retornos possíveis
- **Modelos de dados**: Estruturas de entrada e saída documentadas

## Testando a API

### Usando curl

```bash
# Verificar status
curl http://localhost:9000/status

# Buscar palavras
curl -X POST http://localhost:9000/buscar \
  -H "Content-Type: application/json" \
  -d '{"query": "sentimento de alegria", "limit": 3}'

# Adicionar palavra
curl -X POST http://localhost:9000/adicionar \
  -H "Content-Type: application/json" \
  -d '{"palavra": "carro", "definicao": "veículo automotor de quatro rodas"}'
```

### Usando Python

```python
import requests

# Buscar palavras
response = requests.post('http://localhost:9000/buscar', json={
    'query': 'fruta doce',
    'limit': 5
})
print(response.json())

# Adicionar palavra
response = requests.post('http://localhost:9000/adicionar', json={
    'palavra': 'livro',
    'definicao': 'objeto com páginas impressas contendo texto'
})
print(response.json())
```

## Arquitetura

- **FastAPI**: Framework web assíncrono para a API REST
- **SentenceTransformers**: Modelo para gerar embeddings multilíngues
- **Qdrant**: Banco de dados vetorial para busca semântica
- **Docker**: Containerização dos serviços
- **Pydantic**: Validação de dados e documentação automática

## Estrutura Modular

### Pacote `api/`
- **`dicionarioAPI.py`**: Endpoints e configuração FastAPI
- **`models.py`**: Modelos Pydantic para validação
- **`config.py`**: Configurações centralizadas
- **`__init__.py`**: Inicialização do pacote

### Pacote `services/`
- **`dicionarioService.py`**: Lógica de negócio e integração com Qdrant
- **`__init__.py`**: Inicialização do pacote

## Configuração

### Variáveis de Ambiente

- `QDRANT_HOST`: Host do Qdrant (padrão: localhost)
- `QDRANT_PORT`: Porta do Qdrant (padrão: 6333)

### Modelo de Embeddings

O projeto usa o modelo `paraphrase-multilingual-MiniLM-L12-v2` que suporta português e oferece boa performance para textos curtos como definições de dicionário.

## Dados Iniciais

A API é inicializada com um conjunto de palavras exemplo incluindo:
- Frutas (banana, abacaxi, melão)
- Locais (lar, casa, moradia)
- Sentimentos (felicidade, tristeza, amizade, ciúmes)
- Capitais (Jacarta, Brasília)

## Troubleshooting

### Qdrant não conecta
- Verifique se o container do Qdrant está rodando
- Confirme se as portas 6333 e 6334 estão livres

### Modelo demora para carregar
- O modelo SentenceTransformers é baixado na primeira execução
- Downloads subsequentes usam cache local

### API não responde
- Verifique se a porta 9000 está livre
- Confirme se todas as dependências estão instaladas

## Desenvolvimento

### Estrutura de Arquivos
O projeto segue uma arquitetura modular separando responsabilidades:
- **API**: Interface REST com documentação automática
- **Services**: Lógica de negócio e integração com bases de dados
- **Models**: Validação e serialização de dados
- **Config**: Configurações centralizadas

### Extensibilidade
Para adicionar novos recursos:
1. Adicione novos modelos em `api/models.py`
2. Implemente lógica em `services/dicionarioService.py`
3. Crie endpoints em `api/dicionarioAPI.py`
4. Atualize configurações em `api/config.py` se necessário