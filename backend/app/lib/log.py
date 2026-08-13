"""Structured logging setup."""
from __future__ import annotations

import logging
import sys

from app.config import settings


def setup_logging() -> None:
    level = getattr(logging, settings.log_level.upper(), logging.INFO)
    fmt = "%(asctime)s %(levelname)-8s %(name)s :: %(message)s"
    logging.basicConfig(stream=sys.stdout, level=level, format=fmt)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
