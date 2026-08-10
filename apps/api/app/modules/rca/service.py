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
from app.modules.kubernetes.service import KubernetesService

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
        self.kubernetes_service = KubernetesService()

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
    def _collect_kubernetes_context(
        self,
        namespace: str | None,
        resource_name: str | None,
    ) -> dict:
        """
        Collect Kubernetes context for the affected resource.
        """

        if not namespace or not resource_name:
            return {}

        # -------------------------------------------------
        # Pod lookup
        # -------------------------------------------------

        try:
            pod = self.kubernetes_service.find_pod_by_resource(
                namespace,
                resource_name,
            )
        except Exception:
            pod = None

        if pod:
            pod_name = pod["name"]
            container_name = pod.get("container")

            # Pod details are the most important RCA evidence.
            try:
                details = self.kubernetes_service.get_pod_details(
                    namespace,
                    pod_name,
                )
            except Exception:
                details = None

            # Events are supplementary evidence.
            try:
                events = self.kubernetes_service.get_pod_events(
                    namespace,
                    pod_name,
                )
            except Exception:
                events = []

            # Logs are supplementary evidence.
            try:
                logs = self.kubernetes_service.get_pod_logs(
                    namespace,
                    pod_name,
                    container_name,
                    previous=True,
                )
            except Exception:
                logs = ""

            return {
                "resource_type": "pod",
                "pod": pod,
                "details": details,
                "events": events,
                "logs": logs,
            }

        # -------------------------------------------------
        # Node lookup
        # -------------------------------------------------

        try:
            node_name = self.kubernetes_service.find_node_by_resource(
                resource_name,
            )
        except Exception:
            node_name = None

        if node_name:
            try:
                node_details = (
                    self.kubernetes_service.get_node_details(
                        node_name
                    )
                )
            except Exception:
                node_details = None

            return {
                "resource_type": "node",
                "node": node_name,
                "details": node_details,
            }

        return {}
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

        namespace = latest.namespace

        kubernetes_context = self._collect_kubernetes_context(
            namespace,
            latest.resource_name,
        )
                # -------------------------------------------------
        # Kubernetes evidence
        # -------------------------------------------------

        kubernetes_oom = False

        if kubernetes_context:
            details = kubernetes_context.get("details") or {}

            evidence_text += " " + str(details).lower()

            events = kubernetes_context.get("events") or []

            for event in events:
                evidence_text += " " + str(
                    event.get("reason") or ""
                ).lower()

                evidence_text += " " + str(
                    event.get("message") or ""
                ).lower()

            logs = kubernetes_context.get("logs") or ""

            evidence_text += " " + logs.lower()

            # -------------------------------------------------
            # Detect Kubernetes OOMKilled from structured state
            # -------------------------------------------------

            for container in details.get("containers", []):
                state = container.get("state") or {}

                last_terminated = (
                    container.get("last_terminated") or {}
                )

                if (
                    state.get("reason") == "OOMKilled"
                    or last_terminated.get("reason") == "OOMKilled"
                ):
                    kubernetes_oom = True
                    break
        # -------------------------------------------------
        # CPU
        # -------------------------------------------------

        if not kubernetes_oom and any(
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

        elif kubernetes_oom or any(
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
            details = (
                kubernetes_context.get("details")
                if kubernetes_context
                else None
            )

            containers = (
                details.get("containers", [])
                if details
                else []
            )

            oom_container = None

            for container in containers:
                state = container.get("state") or {}

                if (
                    state.get("reason") == "OOMKilled"
                    or (
                        container.get("last_terminated") or {}
                    ).get("reason") == "OOMKilled"
                ):
                    oom_container = container
                    break

            if oom_container:
                container_name = oom_container.get(
                    "name",
                    "unknown",
                )

                limits = oom_container.get(
                    "limits",
                    {},
                )

                requests = oom_container.get(
                    "requests",
                    {},
                )

                state = oom_container.get(
                    "state",
                    {},
                )

                terminated = (
                    state.get("terminated") or {}
                )

                exit_code = terminated.get(
                    "exit_code"
                )

                node_name = (
                    details.get("node")
                    if details
                    else None
                )

                memory_limit = limits.get(
                    "memory"
                )

                memory_request = requests.get(
                    "memory"
                )

                root_cause = (
                    f"Container '{container_name}' in pod "
                    f"'{details.get('name', resource_name)}' "
                    f"was OOMKilled after exceeding its "
                    f"memory limit"
                )

                summary_parts = [
                    (
                        f"Kubernetes terminated container "
                        f"'{container_name}' because it exceeded "
                        f"its configured memory limit."
                    )
                ]

                if memory_limit:
                    summary_parts.append(
                        f"Memory limit: {memory_limit}."
                    )

                if memory_request:
                    summary_parts.append(
                        f"Memory request: {memory_request}."
                    )

                if exit_code is not None:
                    summary_parts.append(
                        f"Exit code: {exit_code}."
                    )

                if node_name:
                    summary_parts.append(
                        f"Node: {node_name}."
                    )

                summary = " ".join(summary_parts)

                confidence = 0.99

                recommendations = [
                    RCARecommendation(
                        action=(
                            f"Review memory usage of container "
                            f"'{container_name}'"
                        ),
                        reason=(
                            "The container was terminated by "
                            "Kubernetes because it exceeded "
                            "its memory limit."
                        ),
                    ),
                    RCARecommendation(
                        action=(
                            "Increase the container memory limit "
                            "if the workload legitimately requires "
                            "more memory"
                        ),
                        reason=(
                            f"The configured memory limit is "
                            f"{memory_limit or 'not available'}."
                        ),
                    ),
                    RCARecommendation(
                        action=(
                            "Investigate possible memory leaks "
                            "or abnormal memory growth"
                        ),
                        reason=(
                            "Repeated OOMKilled events can indicate "
                            "a memory leak or unexpectedly high "
                            "application memory consumption."
                        ),
                    ),
                ]

            else:
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
                            "Check for memory leaks in the "
                            "affected application"
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