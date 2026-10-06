from fastapi import FastAPI


app = FastAPI(
    title="Transit App API",
    version = "0.1.0-demo",
)

@app.get("/health")
def health_check():
    return {"status": "ok"}