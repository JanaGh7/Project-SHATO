# app/routes.py
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from .models import ValidatorPayload
from .clients import call_validator
from .logging_config import logger
import httpx

router = APIRouter()

@router.post("/orchestrate")
async def orchestrate(payload: ValidatorPayload):
    """
    Accept only validator-style JSON:
      { "command": "...", "command_params": {...} }
    Forward it unchanged (aside from validation) to robot-validator.
    """
    # payload is already validated by Pydantic (extra fields forbidden)
    validator_payload = {
        "command": payload.command,
        "command_params": payload.command_params
    }

    logger.info(f"[ORCH] received payload for validator: {validator_payload}")

    try:
        resp = await call_validator(validator_payload)
    except httpx.RequestError as e:
        logger.error(f"[ORCH] validator unreachable: {e}")
        raise HTTPException(status_code=503, detail="validator_unreachable")

    if resp.status_code in (400, 422):
        try:
            detail = resp.json()
        except Exception:
            detail = resp.text

        # Extract a simpler reason if possible
        if isinstance(detail, dict) and "detail" in detail:
            reason = detail["detail"]
        else:
            reason = str(detail)

        logger.info(f"[ORCH] validator rejected: {reason}")

        return JSONResponse(
            status_code=400,
            content={
                "status": "rejected",
                "reason": reason
            }
        )

    if 500 <= resp.status_code < 600:
        logger.error(f"[ORCH] validator returned {resp.status_code}")
        raise HTTPException(status_code=503, detail="validator_error")

    try:
        validator_json = resp.json()
    except Exception:
        validator_json = {"raw": resp.text}

    logger.info(f"[ORCH] validator approved: {validator_json}")

    return JSONResponse(status_code=200, content={"status": "approved", "validator_response": validator_json})

