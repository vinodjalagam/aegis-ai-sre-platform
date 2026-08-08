"""
Root cause analysis service.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.incidents.evidence.repository import (
    IncidentEvidenceRepository,
)
from app.modules.rca.models import IncidentRCA
from app.modules.rca.repository import RCARepository
from app.modules.rca.schemas import (
    RCACreate,
    RCAAnalysisResponse,
    RCARecommendation,
)


class RCAService:
    """
    Business logic for root cause analysis.
    """

    def __init__(
        self,
        db: AsyncSession,
    ):
        self.repository = RCARepository(db)
        self.evidence_repository = IncidentEvidenceRepository(db)

    async def create(
        self,
        incident_id: str,
        data: RCACreate,
    ) -> IncidentRCA:
        """
        Create an RCA result for an incident.
        """

        rca = IncidentRCA(
            incident_id=incident_id,
            **data.model_dump(),
        )

        return await self.repository.create(rca)

    async def get_by_incident(
        self,
        incident_id: str,
    ) -> IncidentRCA | None:
        """
        Return RCA for an incident.
        """

        return await self.repository.get_by_incident(
            incident_id
        )

    async def analyze_incident(
        self,
        incident_id: str,
    ) -> RCAAnalysisResponse:
        """
        Analyze incident evidence and generate dynamic RCA.
        """

        evidence = await self.evidence_repository.list_by_incident(
            incident_id
        )

        if not evidence:
            raise ValueError(
                "No evidence found for incident"
            )

        # -------------------------------------------------
        # Combine all available evidence
        # -------------------------------------------------

        evidence_text = " ".join(
            filter(
                None,
                [
                    str(item.title or "")
                    for item in evidence
                ]
                + [
                    str(item.description or "")
                    for item in evidence
                ]
                + [
                    str(item.query or "")
                    for item in evidence
                ]
                + [
                    str(item.evidence_type or "")
                    for item in evidence
                ],
            )
        ).lower()

        latest = evidence[-1]

        resource_name = (
            latest.resource_name
            or "the affected resource"
        )

        # -------------------------------------------------
        # CPU
        # -------------------------------------------------

        if any(
            keyword in evidence_text
            for keyword in [
                "cpu",
                "processor",
                "cpu utilization",
                "cpu usage",
            ]
        ):
            root_cause = (
                f"High CPU utilization on {resource_name}"
            )

            summary = (
                "Monitoring detected CPU utilization above "
                "the configured threshold."
            )

            confidence = 0.95

            recommendations = [
                RCARecommendation(
                    action=(
                        "Inspect the top CPU-consuming "
                        "processes on the affected resource"
                    ),
                    reason=(
                        "Identify the workload responsible "
                        "for the elevated CPU utilization"
                    ),
                ),
                RCARecommendation(
                    action=(
                        "Review recent workload or deployment changes"
                    ),
                    reason=(
                        "A recent deployment or configuration "
                        "change may have increased CPU usage"
                    ),
                ),
                RCARecommendation(
                    action=(
                        "Review CPU requests and limits"
                    ),
                    reason=(
                        "Incorrect resource configuration can "
                        "cause CPU contention"
                    ),
                ),
            ]

        # -------------------------------------------------
        # Memory / OOM
        # -------------------------------------------------

        elif any(
            keyword in evidence_text
            for keyword in [
                "memory",
                "oom",
                "oomkilled",
                "out of memory",
                "memory utilization",
                "memory usage",
            ]
        ):
            root_cause = (
                f"High memory utilization or memory pressure "
                f"on {resource_name}"
            )

            summary = (
                "Monitoring detected excessive memory usage "
                "or an out-of-memory condition."
            )

            confidence = 0.93

            recommendations = [
                RCARecommendation(
                    action=(
                        "Identify the processes or containers "
                        "consuming excessive memory"
                    ),
                    reason=(
                        "Determine the workload responsible "
                        "for the memory pressure"
                    ),
                ),
                RCARecommendation(
                    action=(
                        "Review Kubernetes memory requests "
                        "and limits"
                    ),
                    reason=(
                        "Insufficient memory limits can result "
                        "in OOMKilled containers"
                    ),
                ),
                RCARecommendation(
                    action=(
                        "Check for memory leaks in the affected application"
                    ),
                    reason=(
                        "Repeated memory growth can indicate "
                        "an application memory leak"
                    ),
                ),
            ]

        # -------------------------------------------------
        # Pod CrashLoopBackOff
        # -------------------------------------------------

        elif any(
            keyword in evidence_text
            for keyword in [
                "crashloopbackoff",
                "crash loop",
                "crashed",
                "container crash",
                "container restart",
            ]
        ):
            root_cause = (
                f"Kubernetes container repeatedly failed "
                f"on {resource_name}"
            )

            summary = (
                "The affected Kubernetes workload is repeatedly "
                "crashing or restarting."
            )

            confidence = 0.92

            recommendations = [
                RCARecommendation(
                    action=(
                        "Inspect the affected pod status and events"
                    ),
                    reason=(
                        "Kubernetes events can identify the reason "
                        "for container restarts"
                    ),
                ),
                RCARecommendation(
                    action=(
                        "Review the container logs"
                    ),
                    reason=(
                        "Application logs can reveal the underlying "
                        "startup or runtime failure"
                    ),
                ),
                RCARecommendation(
                    action=(
                        "Check liveness and readiness probes"
                    ),
                    reason=(
                        "Incorrect probes can repeatedly restart "
                        "otherwise healthy containers"
                    ),
                ),
            ]

        # -------------------------------------------------
        # Pod Pending / Scheduling
        # -------------------------------------------------

        elif any(
            keyword in evidence_text
            for keyword in [
                "pending",
                "unschedulable",
                "failedscheduling",
                "failed scheduling",
                "scheduler",
            ]
        ):
            root_cause = (
                f"Kubernetes workload could not be scheduled "
                f"on available nodes"
            )

            summary = (
                "The workload is unable to obtain a suitable "
                "Kubernetes node for scheduling."
            )

            confidence = 0.90

            recommendations = [
                RCARecommendation(
                    action=(
                        "Inspect Kubernetes scheduling events"
                    ),
                    reason=(
                        "Scheduling events identify resource, "
                        "taint, affinity, or constraint problems"
                    ),
                ),
                RCARecommendation(
                    action=(
                        "Check node capacity and allocatable resources"
                    ),
                    reason=(
                        "Insufficient CPU or memory can prevent "
                        "pod scheduling"
                    ),
                ),
                RCARecommendation(
                    action=(
                        "Review node selectors, affinity, and tolerations"
                    ),
                    reason=(
                        "Scheduling constraints may prevent the "
                        "pod from matching available nodes"
                    ),
                ),
            ]

        # -------------------------------------------------
        # Image Pull
        # -------------------------------------------------

        elif any(
            keyword in evidence_text
            for keyword in [
                "imagepullbackoff",
                "errimagepull",
                "image pull",
                "failed to pull image",
                "pull image",
            ]
        ):
            root_cause = (
                f"Container image could not be pulled "
                f"for {resource_name}"
            )

            summary = (
                "Kubernetes was unable to download the required "
                "container image."
            )

            confidence = 0.94

            recommendations = [
                RCARecommendation(
                    action=(
                        "Verify the container image name and tag"
                    ),
                    reason=(
                        "An incorrect image reference can cause "
                        "image pull failures"
                    ),
                ),
                RCARecommendation(
                    action=(
                        "Verify registry authentication credentials"
                    ),
                    reason=(
                        "Private registries require valid image "
                        "pull credentials"
                    ),
                ),
                RCARecommendation(
                    action=(
                        "Check node connectivity to the container registry"
                    ),
                    reason=(
                        "Network connectivity problems can prevent "
                        "image downloads"
                    ),
                ),
            ]

        # -------------------------------------------------
        # Node Down / Unreachable
        # -------------------------------------------------

        elif any(
            keyword in evidence_text
            for keyword in [
                "node down",
                "node notready",
                "node not ready",
                "node unreachable",
                "kubelet down",
                "kubelet unavailable",
            ]
        ):
            root_cause = (
                f"Kubernetes node health failure involving "
                f"{resource_name}"
            )

            summary = (
                "The affected Kubernetes node is unhealthy, "
                "unreachable, or not reporting Ready status."
            )

            confidence = 0.94

            recommendations = [
                RCARecommendation(
                    action=(
                        "Check Kubernetes node status"
                    ),
                    reason=(
                        "Node conditions identify the specific "
                        "health problem"
                    ),
                ),
                RCARecommendation(
                    action=(
                        "Check kubelet service and node logs"
                    ),
                    reason=(
                        "Kubelet failures can cause nodes to "
                        "become NotReady"
                    ),
                ),
                RCARecommendation(
                    action=(
                        "Check node CPU, memory, disk, and network health"
                    ),
                    reason=(
                        "Infrastructure resource exhaustion can "
                        "cause node failures"
                    ),
                ),
            ]

        # -------------------------------------------------
        # Disk
        # -------------------------------------------------

        elif any(
            keyword in evidence_text
            for keyword in [
                "disk",
                "filesystem",
                "file system",
                "disk usage",
                "disk full",
                "no space left",
            ]
        ):
            root_cause = (
                f"High disk utilization or filesystem pressure "
                f"on {resource_name}"
            )

            summary = (
                "The affected resource is experiencing high "
                "disk or filesystem utilization."
            )

            confidence = 0.92

            recommendations = [
                RCARecommendation(
                    action=(
                        "Identify directories and files consuming disk space"
                    ),
                    reason=(
                        "Large files or logs may be responsible "
                        "for filesystem exhaustion"
                    ),
                ),
                RCARecommendation(
                    action=(
                        "Review application and container log retention"
                    ),
                    reason=(
                        "Unbounded logs can rapidly consume disk space"
                    ),
                ),
                RCARecommendation(
                    action=(
                        "Increase storage capacity if required"
                    ),
                    reason=(
                        "Persistent workload growth may require "
                        "additional storage"
                    ),
                ),
            ]

        # -------------------------------------------------
        # Network
        # -------------------------------------------------

        elif any(
            keyword in evidence_text
            for keyword in [
                "network",
                "connection refused",
                "connection timeout",
                "timeout",
                "unreachable",
                "dns",
                "dns resolution",
                "network error",
            ]
        ):
            root_cause = (
                f"Network connectivity failure involving "
                f"{resource_name}"
            )

            summary = (
                "The monitored resource is experiencing a "
                "network connectivity or communication problem."
            )

            confidence = 0.85

            recommendations = [
                RCARecommendation(
                    action=(
                        "Test connectivity between the affected services"
                    ),
                    reason=(
                        "Connectivity testing can identify "
                        "where communication is failing"
                    ),
                ),
                RCARecommendation(
                    action=(
                        "Check DNS resolution and service endpoints"
                    ),
                    reason=(
                        "Incorrect DNS or service configuration "
                        "can cause connection failures"
                    ),
                ),
                RCARecommendation(
                    action=(
                        "Review Kubernetes Services, NetworkPolicies, "
                        "and ingress configuration"
                    ),
                    reason=(
                        "Kubernetes networking rules can block "
                        "application communication"
                    ),
                ),
            ]

        # -------------------------------------------------
        # HTTP / Application errors
        # -------------------------------------------------

        elif any(
            keyword in evidence_text
            for keyword in [
                "http 500",
                "500 error",
                "5xx",
                "internal server error",
                "application error",
                "request error",
            ]
        ):
            root_cause = (
                f"Application-level failure detected on "
                f"{resource_name}"
            )

            summary = (
                "The monitored application is returning server-side "
                "errors."
            )

            confidence = 0.82

            recommendations = [
                RCARecommendation(
                    action=(
                        "Inspect application logs around the failure time"
                    ),
                    reason=(
                        "Application logs can identify the failing "
                        "component or exception"
                    ),
                ),
                RCARecommendation(
                    action=(
                        "Review recent application deployments"
                    ),
                    reason=(
                        "Recent code changes can introduce runtime errors"
                    ),
                ),
                RCARecommendation(
                    action=(
                        "Check dependent services and databases"
                    ),
                    reason=(
                        "Dependency failures can surface as application "
                        "server errors"
                    ),
                ),
            ]

        # -------------------------------------------------
        # Availability / Service Down
        # -------------------------------------------------

        elif any(
            keyword in evidence_text
            for keyword in [
                "service down",
                "service unavailable",
                "availability",
                "target down",
                "instance down",
                "up == 0",
            ]
        ):
            root_cause = (
                f"Service or monitoring target is unavailable "
                f"on {resource_name}"
            )

            summary = (
                "The monitored service or target is not available "
                "or is no longer responding."
            )

            confidence = 0.90

            recommendations = [
                RCARecommendation(
                    action=(
                        "Verify whether the service process is running"
                    ),
                    reason=(
                        "A stopped process can make the service unavailable"
                    ),
                ),
                RCARecommendation(
                    action=(
                        "Check service endpoints and health probes"
                    ),
                    reason=(
                        "Incorrect endpoints or failed health checks "
                        "can cause availability alerts"
                    ),
                ),
                RCARecommendation(
                    action=(
                        "Review recent deployments and configuration changes"
                    ),
                    reason=(
                        "Recent changes may have caused the service "
                        "to become unavailable"
                    ),
                ),
            ]

        # -------------------------------------------------
        # Unknown failure
        # -------------------------------------------------

        else:
            root_cause = (
                f"Unable to determine the exact root cause "
                f"for {resource_name}"
            )

            summary = (
                "The available incident evidence does not contain "
                "enough information to determine a specific root cause."
            )

            confidence = 0.50

            recommendations = [
                RCARecommendation(
                    action=(
                        "Collect additional Prometheus metrics"
                    ),
                    reason=(
                        "Additional metrics can help identify "
                        "the affected resource and failure condition"
                    ),
                ),
                RCARecommendation(
                    action=(
                        "Collect Kubernetes events and pod logs"
                    ),
                    reason=(
                        "Kubernetes and application evidence can "
                        "provide more context"
                    ),
                ),
                RCARecommendation(
                    action=(
                        "Review recent deployments and configuration changes"
                    ),
                    reason=(
                        "Recent changes are common contributors "
                        "to infrastructure incidents"
                    ),
                ),
            ]

        # -------------------------------------------------
        # Save or update RCA
        # -------------------------------------------------

        existing = await self.repository.get_by_incident(
            incident_id
        )

        if existing:
            existing.root_cause = root_cause
            existing.summary = summary
            existing.confidence = confidence
            existing.status = "completed"

            await self.repository.db.commit()
            await self.repository.db.refresh(existing)

        else:
            await self.create(
                incident_id=incident_id,
                data=RCACreate(
                    root_cause=root_cause,
                    summary=summary,
                    confidence=confidence,
                    status="completed",
                ),
            )

        return RCAAnalysisResponse(
            incident_id=incident_id,
            root_cause=root_cause,
            summary=summary,
            confidence=confidence,
            recommendations=recommendations,
        )