import time
from fastapi import FastAPI
from api.routes import router as books_router
from api.auth import router as auth_router
from api.ml import router as ml_router
from api.metrics import router as metrics_router
from api.database import engine, Base
from api.logging_config import logger

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="APIBook",
    version="1.0.0",
    description="API Publica para Consulta de Livros"
)

app.include_router(books_router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1")
app.include_router(ml_router, prefix="/api/v1")
app.include_router(metrics_router, prefix="/api/v1")

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


@app.get("/")
async def home():
    return "Hello"



