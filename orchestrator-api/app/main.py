# orchestrator-api/app/main.py
from fastapi import FastAPI
from .routes import router
from .logging_config import logger
from . import clients

app = FastAPI(title="Orchestrator API")
app.include_router(router)  

# on shutdown, close httpx client
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("[ORCH] shutdown - closing http clients")
    await clients.close_client()
