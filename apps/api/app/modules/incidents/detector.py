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
from app.modules.incidents.evidence.service import (
    IncidentEvidenceService,
)
from app.modules.incidents.evidence.schemas import (
    IncidentEvidenceCreate,
)

from app.modules.incidents.timeline.service import (
    IncidentTimelineService,
)
from app.modules.incidents.timeline.schemas import (
    IncidentTimelineEventCreate,
)
from app.modules.kubernetes.service import KubernetesService
from app.modules.clusters.repository import ClusterRepository

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

        self.cluster_repository = ClusterRepository(db)

        self.prometheus = None
        self.repository = IncidentRepository(db)
        self.service = IncidentService(db)
        self.evidence_service = IncidentEvidenceService(db)
        self.timeline_service = IncidentTimelineService(db)
        self.kubernetes_service = None
        
    async def scan(self):
        """
        Execute all configured detection rules.
        """

        await self.initialize_cluster()

        logger.info(
            "Starting incident scan for cluster %s",
            self.cluster_id,
        )

        for rule in IncidentRules.ALL_RULES:

            logger.info(
                "Executing rule: %s",
                rule["name"],
            )

            try:
                result = await self.prometheus.query(
                    rule["query"]
                )

                logger.info(
                    "Rule '%s' returned %d result(s)",
                    rule["name"],
                    len(result),
                )

                # -------------------------------------------------
                # No metrics matched
                # -------------------------------------------------

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

                        # await self.service.resolve_incident(
                        #     incident
                        # )

                        # await self.timeline_service.create(
                        #     incident_id=incident.id,
                        #     data=IncidentTimelineEventCreate(
                        #         event_type="resolved",
                        #         title="Incident resolved",
                        #         description=(
                        #             f"{rule['name']} is no longer triggered"
                        #         ),
                        #     ),
                        # )
                        await self.service.auto_resolve_incident(
                            incident
                        )

                        logger.info(
                            "Resolved incident %s",
                            incident.id,
                        )

                    continue

                # -------------------------------------------------
                # Rule triggered
                # -------------------------------------------------

                for item in result:

                    metric = item.get(
                        "metric",
                        {},
                    )

                    if metric.get("pod"):
                        resource_name = metric["pod"]
                    elif metric.get("node"):
                        resource_name = metric["node"]
                    elif metric.get("instance"):
                        resource_name = metric["instance"]
                    elif metric.get("service"):
                        resource_name = metric["service"]
                    else:
                        resource_name = "unknown"

                    namespace = metric.get(
                        "namespace"
                    )
                    kubernetes_metadata = None

                    if namespace and resource_name:
                        try:
                            pod = self.kubernetes_service.find_pod_by_resource(
                                namespace,
                                resource_name,
                            )

                            if pod:
                                pod_details = (
                                    self.kubernetes_service.get_pod_details(
                                        namespace,
                                        pod["name"],
                                    )
                                )

                                kubernetes_metadata = {
                                    "pod": pod["name"],
                                    "container": pod.get("container"),
                                }

                                if pod_details:
                                    kubernetes_metadata.update(
                                        {
                                            "node": pod_details.get("node"),
                                            "pod_ip": pod_details.get("pod_ip"),
                                            "phase": pod_details.get("phase"),
                                            "restart_policy": pod_details.get("restart_policy"),
                                            "containers": pod_details.get("containers", []),
                                        }
                                    )

                                    kubernetes_metadata["events"] = (
                                        self.kubernetes_service.get_pod_events(
                                            namespace,
                                            pod["name"],
                                        )
                                    )

                                    container_name = pod.get("container")

                                    if container_name:
                                        kubernetes_metadata["logs"] = (
                                            self.kubernetes_service.get_pod_logs(
                                                namespace,
                                                pod["name"],
                                                container_name=container_name,
                                                previous=True,
                                            )
                                        )

                        except Exception:
                            logger.exception(
                                "Failed to collect Kubernetes metadata "
                                "for resource: %s",
                                resource_name,
                            )

                    # Prometheus returns the actual value
                    # in item["value"][1].
                    value = None

                    if item.get("value"):
                        value = str(
                            item["value"][1]
                        )

                    logger.info(
                        "Resource: %s",
                        resource_name,
                    )

                    logger.info(
                        "Metric value: %s",
                        value,
                    )

                    # -------------------------------------------------
                    # Check whether incident already exists
                    # -------------------------------------------------

                    existing = (
                        await self.repository.get_open_incident(
                            title=rule["name"],
                            resource_name=resource_name,
                        )
                    )

                    if existing:

                        logger.info(
                            "Incident already exists: %s (%s)",
                            rule["name"],
                            resource_name,
                        )

                        # -------------------------------------------------
                        # Add fresh evidence to existing incident
                        # -------------------------------------------------

                        evidence = (
                            IncidentEvidenceCreate(
                                evidence_type="prometheus",
                                title=rule["name"],
                                description=rule["description"],
                                query=rule["query"],
                                resource_name=resource_name,
                                namespace=namespace,
                                metric_value=value,
                                metadata_json=kubernetes_metadata,
                            )
                        )


                        created_evidence = await self.evidence_service.create(
                            incident_id=existing.id,
                            data=evidence,
                        )

                        if created_evidence:
                            logger.info(
                                "Evidence added to existing incident: %s",
                                existing.id,
                            )
                        else:
                            logger.debug(
                                "Duplicate evidence skipped for incident: %s",
                                existing.id,
                            )

                        continue

                    # -------------------------------------------------
                    # Create new incident
                    # -------------------------------------------------

                    logger.warning(
                        "Rule triggered: %s (%s)",
                        rule["name"],
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

                    created = (
                        await self.service.create_incident(
                            incident
                        )
                    )
                    await self.timeline_service.create(
                        incident_id=created.id,
                        data=IncidentTimelineEventCreate(
                            event_type="detected",
                            title="Incident detected",
                            description=(
                                f"{rule['name']} detected on "
                                f"{resource_name}"
                            ),
                        ),
                    )

                    logger.info(
                        "Incident created successfully: %s",
                        created.id,
                    )

                    # -------------------------------------------------
                    # Create evidence for new incident
                    # -------------------------------------------------

                    evidence = IncidentEvidenceCreate(
                        evidence_type="prometheus",
                        title=rule["name"],
                        description=rule["description"],
                        query=rule["query"],
                        resource_name=resource_name,
                        namespace=namespace,
                        metric_value=value,
                        metadata_json=kubernetes_metadata,
                    )

                    created_evidence = (
                        await self.evidence_service.create(
                            incident_id=created.id,
                            data=evidence,
                        )
                    )
                    await self.timeline_service.create(
                        incident_id=created.id,
                        data=IncidentTimelineEventCreate(
                            event_type="evidence_collected",
                            title="Evidence collected",
                            description=(
                                f"Prometheus evidence collected for "
                                f"{resource_name}"
                            ),
                            metadata_json=None,
                        ),
                    )

                    logger.info(
                        "Evidence created successfully: %s",
                        created_evidence.id,
                    )

            except Exception:
                logger.exception(
                    "Failed to execute rule: %s",
                    rule["name"],
                )

        logger.info(
            "Incident scan completed."
        )
    async def initialize_cluster(self) -> None:
        """
        Initialize Kubernetes connectivity for the selected cluster.
        """

        cluster = await self.cluster_repository.get_by_id(
            self.cluster_id
        )

        if cluster is None:
            raise ValueError(
                f"Cluster not found: {self.cluster_id}"
            )

        if not cluster.is_active:
            raise ValueError(
                f"Cluster is inactive: {cluster.name}"
            )

        self.kubernetes_service = KubernetesService(
            cluster.kubeconfig
        )