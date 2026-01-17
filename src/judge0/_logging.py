import logging.handlers
import sys
from pathlib import Path


def setup_logging(
    log_file: Path | None = None,
    file_level: int | None = None,
    console_level: int | None = None,
) -> None:
    """Set up logging for the package."""
    if log_file is None:
        try:
            log_dir = Path.home() / ".judge0" / "logs"
            log_dir.mkdir(parents=True, exist_ok=True)
            log_file = log_dir / "judge0.log"
        except (OSError, PermissionError):
            # Fallback to user's current working directory
            log_file = Path("judge0.log")

    logger = logging.getLogger("judge0")
    logger.setLevel(logging.DEBUG)

    # Check if handlers are already added to avoid duplication.
    if logger.hasHandlers():
        return

    # Determine log levels: parameter > env var > default
    if file_level is None:
        file_level = getattr(
            logging, os.getenv("JUDGE0_FILE_LOG_LEVEL", "DEBUG").upper(), logging.DEBUG
        )
    if console_level is None:
        console_level = getattr(
            logging, os.getenv("JUDGE0_CONSOLE_LOG_LEVEL", "INFO").upper(), logging.INFO
        )

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # File handler with weekly rotation.
    file_handler = logging.handlers.TimedRotatingFileHandler(
        filename=log_file,
        when="W0",  # Rotate every Monday
        interval=1,
        backupCount=4,  # Keep 4 weeks of logs
    )
    file_handler.setLevel(file_level)
    file_handler.setFormatter(formatter)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(console_level)
    console_handler.setFormatter(formatter)

    # Add handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
