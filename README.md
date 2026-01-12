# APIBook — API Pública para Consulta de Livros

API RESTful para consulta de dados de livros, desenvolvida como Tech Challenge da pós-graduação em Machine Learning da FIAP.

## Sobre o Projeto

Sistema completo de extração e disponibilização de dados de livros via API pública. Inclui:

- Web scraper que extrai dados de 1000 livros do site Books to Scrape
- API REST com endpoints para consulta, busca e estatísticas
- Autenticação JWT para rotas administrativas
- Pipeline de dados preparados para Machine Learning
- Registro estruturado de todas chamadas
- Endpoint específico para consulta de métricas de performance da API
- Dashboard simples para exposição das métricas de performance 

### Contexto

Projeto desenvolvido para o primeiro módulo da pós-graduação em Machine Learning Engineering, simulando o cenário de um Engenheiro de ML montando infraestrutura de dados para um sistema de recomendação de livros.

## Tecnologias

- **Python 3.12**
- **FastAPI** — Framework web
- **SQLAlchemy** — ORM para banco de dados
- **SQLite** — Banco de dados de usuários
- **BeautifulSoup4** — Web scraping
- **Passlib + BCrypt** — Hash de senhas
- **Python-Jose** — Tokens JWT
- **Python-json-logger + Python logging** - Logging
- **Pydantic** - Data Validation

## Arquitetura

### Diagrama de Componentes

:::mermaid
flowchart TB
    subgraph Cliente
        USER[Usuario]
        POSTMAN[HTTP Client]
    end

    subgraph API[FastAPI - APIBook]
        MAIN[main.py<br>Middleware de Logging]
        
        subgraph Rotas
            ROUTES[routes.py<br>/books endpoints]
            AUTH[auth.py<br>/auth endpoints]
            ML[ml.py<br>/ml endpoints]
            METRICS[metrics.py<br>/metrics endpoint]
        end
    end

    subgraph Dados
        CSV[(books.csv<br>1000 livros)]
        SQLITE[(users.db<br>Usuarios + Predictions)]
        LOGS[(app.log<br>Logs JSON)]
    end

    subgraph Monitoramento
        DASH[dashboard.py<br>Streamlit]
    end

    subgraph Externos
        SCRAPER[scraper.py]
        BOOKS_SITE[books.toscrape.com]
    end

    USER --> POSTMAN
    POSTMAN --> MAIN
    MAIN --> ROUTES
    MAIN --> AUTH
    MAIN --> ML
    MAIN --> METRICS
    
    ROUTES --> CSV
    AUTH --> SQLITE
    ML --> CSV
    ML --> SQLITE
    METRICS --> LOGS
    MAIN --> LOGS
    
    DASH --> LOGS
    
    SCRAPER --> BOOKS_SITE
    SCRAPER --> CSV
:::

### Diagrama de Sequência

:::mermaid
sequenceDiagram
    participant U as Usuario
    participant API as FastAPI
    participant JWT as Auth/JWT
    participant DB as SQLite
    
    U->>API: POST /auth/login
    API->>DB: Verifica credenciais
    DB-->>API: Usuario válido
    API-->>U: Token JWT
    
    U->>API: GET /ml/training-data?target=preço
    API->>API: Processa books.csv
    API-->>U: {X, y, feature_names}
    
    Note over U: Treina modelo externamente
    
    U->>API: POST /ml/predictions (com JWT)
    API->>JWT: Valida token
    JWT-->>API: Usuario autenticado
    API->>DB: Salva predictions
    DB-->>API: OK
    API-->>U: Confirmação
:::

## Instalação

### Pré-requisitos

- Python 3.10+
- pip

### Passo a Passo

1. Clone o Repositório
2. Crie e ative o ambiente virtual
3. instale as dependências - pip install -r requirements.txt
4. Execute o scraper para popular dados ou chame o endpoint http://127.0.0.1:8000//api/v1/scraping/trigger 
5. Inicie a API
6. Acesse a documentação http://127.0.0.1:8000/docs

## Endpoints

### Livros

| Método | Endpoint | Descrição |
|--------|----------|-----------|
|GET| `/api/v1/books` | Lista todos os livros |
|GET| `/api/v1/books/search?title=&category=` | Busca por Título e/ou categoria |
|GET| `/api/v1/books/top-rated` | Lista de livros com avaliação máxima |
|GET| `/api/v1/books/price-range?min=&max=` | lista livros dentreo de um range de preços |
|GET| `/api/v1/books/{id}` | Retorna um livro por id |

### Categorias e Estatisticas

| Método | Endpoint | Descrição |
|--------|----------|-----------|
|GET| `/api/v1/categories` | Lista todas as categorias |
|GET| `/api/v1/stats/overview` | Estatístiacas gerais da coleção |
|GET| `/api/v1/stats/categories` | Estatístiacas por categoria |
|GET| `/api/v1/health` | Status da API |

### Autenticação

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/api/v1/auth/register` | Cadastrar usuário |
| POST | `/api/v1/auth/login` | Login (retorna token JWT) |
| POST | `/api/v1/auth/refresh` | Renovar token |

### Gatilhos

| Método | Endpoint | Descrição |
|--------|----------|-----------|
|POST| `/api/v1/scraping/trigger` | Executa Scraper (protegida) |

### Pipeline ML

| Método | Endpoint | Descrição |
|--------|----------|-----------|
|POST| `/api/v1/ml/features` | Dados formatados para ML |
|POST| `/api/v1/ml/training-data` | Dataset para treinamento |
|POST| `/api/v1/ml/predictions` | Dados formatados para ML (protegida) |

### Métricas

| Método | Endpoint | Descrição |
|--------|----------|-----------|
|POST| `/api/v1//metrics` | Métricas de performance da API |

## Exemplos de Uso

### Buscar livro por título e categoria

**Request**
```bash
curl http://127.0.0.1:8000/api/v1/books/search?title=without&category=FiCtion
```
**Response**
```json
[
    {
        "id": "55",
        "titulo": "World Without End (The Pillars of the Earth #2)",
        "categoria": "Historical Fiction",
        "preço": "£32.97",
        "rating": "Four",
        "disponibilidade": "In stock",
        "imagem": "https://books.toscrape.com/media/cache/be/7c/be7ce6fbc9a8e1a5a5b5c32e73cfd78a.jpg"
    },
    {
        "id": "374",
        "titulo": "10% Happier: How I Tamed the Voice in My Head, Reduced Stress Without Losing My Edge, and Found Self-Help That Actually Works",
        "categoria": "Nonfiction",
        "preço": "£24.57",
        "rating": "Two",
        "disponibilidade": "In stock",
        "imagem": "https://books.toscrape.com/media/cache/40/b2/40b246cf12df5345dc0371c040fddb4b.jpg"
    },
    {
        "id": "426",
        "titulo": "Blink: The Power of Thinking Without Thinking",
        "categoria": "Nonfiction",
        "preço": "£21.74",
        "rating": "Five",
        "disponibilidade": "In stock",
        "imagem": "https://books.toscrape.com/media/cache/5d/41/5d415bc31b1f856a2a9dc8706fd19abd.jpg"
    }
]
```

### Autenticar e acessar rota protegida

```bash
# 1. Registrar usuário
curl -X POST "http://127.0.0.1:8000/api/v1/auth/register?username=admin&password=123456"

# 2. Fazer login
curl -X POST "http://127.0.0.1:8000/api/v1/auth/login?username=admin&password=123456"
# Retorna: {"access_token": "eyJ...", "token_type": "bearer"}

# 3. Usar token para rota protegida
curl -X POST http://127.0.0.1:8000/api/v1/scraping/trigger \
  -H "Authorization: Bearer eyJ..."
```

## Estrutura do Projeto
```
apibook/
├── api/
│   ├── auth.py             # Autenticação JWT
│   ├── database.py         # Configuração SQLAlchemy
│   ├── logging_config.py   # Configuração Logger
│   ├── main.py             # App FastAPI
│   ├── metrics.py          # Endpoints Métricas 
│   ├── models.py           # Modelo User
│   ├── ml.py               # Endpoints ML
│   ├── routes.py           # Rotas de livros
│   └── schemas.py          # Esquemas para validação
├── data/
│   ├── books.csv           # Dados extraídos
│   └── users.db            # Banco de usuários
├── scripts/
│   └── scraper.py          # Web scraper
├── dashboard.py            # Dashboard métricas
├── README.md
└── requirements.txt
```

## Deploy

API disponível em: [URL do deploy]


## Autor

**Caio Grazzini**

- LinkedIn: [seu-linkedin]
- GitHub: [seu-github]

---

Desenvolvido como parte do Tech Challenge — Pós-Graduação em Machine Learning Engineering — FIAP 2024/2025
```