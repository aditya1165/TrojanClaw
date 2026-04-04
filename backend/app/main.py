from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import chat

app = FastAPI(
    title="TrojanClaw API",
    version="0.1.0",
    description="Backend API for TrojanClaw powered by FastAPI.",
)

# Setup CORS to allow React Frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For hackathon, allow all
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(chat.router)

@app.get("/")
def root() -> dict[str, str]:
    return {"message": "Welcome to TrojanClaw API"}


@app.get("/healthcheck")
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}
