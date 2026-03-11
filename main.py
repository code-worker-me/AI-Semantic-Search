from fastapi import FastAPI
from contextlib import asynccontextmanager
from routes import router
from database import init_db
from watcher import start_watching

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    
    # observer = start_watching("arsip")
    # print("👀 Folder watcher aktif. Memantau penambahan PDF di folder 'arsip'...")
    
    yield
    # observer.stop()
    # observer.join()
    # print("Folder watcher dimatikan.")
    
app = FastAPI(
    title="Arsip Semantic Search API",
    description="API pencarian arsip semantik dengan Gemma3",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(router, prefix="/api")