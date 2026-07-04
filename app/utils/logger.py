import logging
import sys
from app.core.config import settings

logger = logging.getLogger("notes_automation")
logger.setLevel(settings.log_level)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(settings.log_level)
formatter = logging.Formatter(
    "%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
handler.setFormatter(formatter)
logger.addHandler(handler)
