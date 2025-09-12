# app/logging_config.py
import logging
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("orchestrator")
