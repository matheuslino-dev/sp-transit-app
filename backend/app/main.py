from fastapi import FastAPI
from app.core.config import settings


app = FastAPI(
    title="Transit App API",
    version = "0.1.0-demo",
)

@app.get("/health")
def health_check():
    return {"status": "ok"}