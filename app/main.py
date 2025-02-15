from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.models.routers import auth, transfer, merch, history

app = FastAPI(
    title = settings.PROJECT_NAME,
    version=settings.VERSION
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(auth.router, prefix="/api/auth")
app.include_router(transfer.router, prefix="/api")
app.include_router(merch.router, prefix="/api")
app.include_router(history.router, prefix="/api")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}