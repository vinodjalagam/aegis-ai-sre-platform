"""
Application lifespan management.
"""

from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.logging.logger import get_logger
from app.modules.incidents.scheduler import IncidentScheduler

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage application startup and shutdown.
    """

    logger.info("Starting Aegis API...")

    scheduler = IncidentScheduler()

    scheduler_task = asyncio.create_task(
        scheduler.start()
    )

    logger.info("Incident scheduler started.")

    try:
        yield

    finally:
        logger.info("Stopping Aegis API...")

        scheduler.stop()

        scheduler_task.cancel()

        try:
            await scheduler_task
        except asyncio.CancelledError:
            pass