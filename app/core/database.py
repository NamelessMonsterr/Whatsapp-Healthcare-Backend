# app/config.py  (snippet)
import logging
import logging.handlers
from pathlib import Path
from pydantic_settings import BaseSettings

...

def setup_logging() -> None:
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    # Root logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Console handler
    console = logging.StreamHandler()
    console.setFormatter(
        logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )
    logger.addHandler(console)

    # File handler (rotating)
    file_handler = logging.handlers.RotatingFileHandler(
        log_dir / "app.log",
        maxBytes=5 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.INFO)          # <-- setLevel called after construction
    file_handler.setFormatter(console.formatter)
    logger.addHandler(file_handler)
