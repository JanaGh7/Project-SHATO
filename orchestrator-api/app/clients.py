# app/clients.py
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from .config import settings
from .logging_config import logger

_client: httpx.AsyncClient | None = None

def get_client() -> httpx.AsyncClient:
    global _client
    if _client is None:
        _client = httpx.AsyncClient(timeout=settings.request_timeout)
    return _client

@retry(
    stop=stop_after_attempt(settings.retry_count),
    wait=wait_exponential(multiplier=0.5, min=0.5, max=4.0),
    retry=retry_if_exception_type(httpx.RequestError)
)
async def call_validator(payload: dict) -> httpx.Response:
    """
    Send payload to robot validator. Returns the httpx.Response.
    Retries only on network errors (RequestError).
    """
    client = get_client()
    headers = {
        "Authorization": f"Bearer {settings.validator_api_key}",
        "Content-Type": "application/json",
    }
    logger.info(f"[CLIENT->VALIDATOR] POST {settings.validator_url} payload={payload}")
    resp = await client.post(settings.validator_url, json=payload, headers=headers)
    return resp

async def close_client():
    global _client
    if _client is not None:
        await _client.aclose()
        _client = None
