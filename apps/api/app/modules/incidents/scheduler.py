"""
Background scheduler for incident detection.
"""

import asyncio
import logging

from app.db.session import SessionLocal
from app.modules.clusters.repository import ClusterRepository
from app.modules.incidents.detector import IncidentDetector

logger = logging.getLogger(__name__)


class IncidentScheduler:

    def __init__(self):
        self._running = False

    async def start(self):
        """
        Start background incident detection.
        """

        self._running = True

        logger.info("Incident scheduler started.")

        while self._running:

            logger.info("Scheduler loop started")

            try:

                async with SessionLocal() as db:

                    cluster_repository = ClusterRepository(db)

                    # Get all clusters
                    clusters = await cluster_repository.list()

                    logger.info(
                        "Found %d cluster(s)",
                        len(clusters),
                    )

                    for cluster in clusters:

                        logger.info(
                            "Scanning cluster %s (%s)",
                            cluster.name,
                            cluster.id,
                        )

                        detector = IncidentDetector(
                            db=db,
                            cluster_id=cluster.id,
                        )

                        await detector.scan()

            except Exception:
                logger.exception(
                    "Incident detection failed."
                )

            await asyncio.sleep(30)

    def stop(self):
        """
        Stop background detection.
        """

        logger.info("Stopping incident scheduler.")

        self._running = False