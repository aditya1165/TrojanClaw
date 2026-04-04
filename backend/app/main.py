from fastapi import FastAPI

app = FastAPI(
    title="TrojanClaw API",
    version="0.1.0",
    description="Backend API for TrojanClaw powered by FastAPI.",
)


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "Welcome to TrojanClaw API"}


@app.get("/healthcheck")
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}
