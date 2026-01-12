import time
from fastapi import FastAPI
from api.routes import router as books_router
from api.auth import router as auth_router
from api.ml import router as ml_router
from api.metrics import router as metrics_router
from api.database import engine, Base
from api.logging_config import logger

# Criar tabelas no banco de dados
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="APIBook",
    version="1.0.0",
    description="API Publica para Consulta de Livros"
)


# Incluindo as rotas com prefixo /api/v1
app.include_router(books_router, prefix="/api/v1")# Rota de livros
app.include_router(auth_router, prefix="/api/v1")# Rota de autenticação
app.include_router(ml_router, prefix="/api/v1")# Rota de Machine Learning
app.include_router(metrics_router, prefix="/api/v1")# Rota de Métricas

# Middleware de logging: um middleware HTTP que mede o tempo 
# de execução de cada requisição, chama call_next, e registra
# via logger.info um dicionário extra com method, path, 
# status_code e Execution time.
@app.middleware("http")
async def logging_middleware(request, call_next):
    request_time = time.time()
    response = await call_next(request)
    delta_time = time.time() - request_time
    logger.info("request completed", 
                extra = {
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": response.status_code,
                    "Execution time": delta_time     
                         })
    return response

# Rota raiz
@app.get("/")
async def home():
    return "Hello"



