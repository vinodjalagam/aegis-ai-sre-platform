"""
Incident detection engine.
"""

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.metrics.client import PrometheusClient
from app.modules.incidents.rules import IncidentRules
from app.modules.incidents.repository import IncidentRepository
from app.modules.incidents.service import IncidentService
from app.modules.incidents.schemas import IncidentCreate

logger = logging.getLogger(__name__)

class IncidentDetector:
    """
    Periodically scans Prometheus metrics and creates incidents.
    """

    def __init__(
        self,
        db: AsyncSession,
        cluster_id: str,
    ):
        self.db = db
        self.cluster_id = cluster_id

        self.prometheus = PrometheusClient()
        self.repository = IncidentRepository(db)
        self.service = IncidentService(db)

    async def scan(self):
        """
        Execute all configured detection rules.
        """

        logger.info("Starting incident scan...")

        for rule in IncidentRules.ALL_RULES:

            logger.info("Executing rule: %s", rule["name"])

            try:
                result = await self.prometheus.query(rule["query"])

                logger.info(
                    "Rule '%s' returned %d result(s)",
                    rule["name"],
                    len(result),
                )

                if not result:

                    logger.info(
                        "No metrics matched rule: %s",
                        rule["name"],
                    )

                    open_incidents = (
                        await self.repository.get_open_incidents(
                            title=rule["name"],
                        )
                    )

                    for incident in open_incidents:

                        logger.info(
                            "Resolving incident %s",
                            incident.id,
                        )

                        await self.service.resolve_incident(
                            incident
                        )

                        logger.info(
                            "Resolved incident %s",
                            incident.id,
                        )

                    continue

                for item in result:

                    metric = item.get("metric", {})

                    resource_name = (
                        metric.get("instance")
                        or metric.get("pod")
                        or metric.get("node")
                        or metric.get("service")
                        or "unknown"
                    )

                    namespace = metric.get("namespace")

                    logger.info(
                        "Resource: %s",
                        resource_name,
                    )

                    existing = await self.repository.get_open_incident(
                        title=rule["name"],
                        resource_name=resource_name,
                    )

                    if existing:
                        logger.info(
                            "Incident already exists: %s (%s)",
                            rule["name"],
                            resource_name,
                        )
                        continue

                    logger.warning(
                        "Rule triggered: %s (%s)",
                        rule["name"],
                        resource_name,
                    )

                    logger.info(
                        "Creating incident for %s",
                        resource_name,
                    )

                    incident = IncidentCreate(
                        cluster_id=self.cluster_id,
                        title=rule["name"],
                        description=rule["description"],
                        severity=rule["severity"],
                        source=rule["source"],
                        resource_name=resource_name,
                        namespace=namespace,
                    )

                    created = await self.service.create_incident(
                        incident
                    )

                    logger.info(
                        "Incident created successfully: %s",
                        created.id,
                    )

            except Exception:
                logger.exception(
                    "Failed to execute rule: %s",
                    rule["name"],
                )

        logger.info("Incident scan completed.")