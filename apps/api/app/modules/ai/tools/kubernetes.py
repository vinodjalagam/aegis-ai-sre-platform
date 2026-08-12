from __future__ import annotations

from app.modules.kubernetes.service import KubernetesService


class KubernetesInvestigationTool:
    """
    Read-only Kubernetes investigation tool for the Aegis AI agent.

    This tool is intentionally read-only.
    No cluster modifications are allowed.
    """

    def __init__(self, kubeconfig: str) -> None:
        self.service = KubernetesService(kubeconfig)

    def investigate_pod(
        self,
        namespace: str,
        pod_name: str,
    ) -> dict:
        """
        Collect useful investigation context for a pod.
        """

        try:
            details = self.service.get_pod_details(
                namespace,
                pod_name,
            )
        except Exception:
            details = None

        try:
            events = self.service.get_pod_events(
                namespace,
                pod_name,
            )
        except Exception:
            events = []

        try:
            logs = self.service.get_pod_logs(
                namespace,
                pod_name,
                previous=True,
            )
        except Exception:
            logs = ""

        return {
            "resource_type": "pod",
            "namespace": namespace,
            "pod_name": pod_name,
            "details": details,
            "events": events,
            "logs": logs,
        }
    
    def investigate_resource(
        self,
        namespace: str | None,
        resource_name: str | None,
    ) -> dict:
        """
        Investigate a Kubernetes resource.

        The tool is read-only and collects the relevant
        Kubernetes evidence for the AI agent.
        """

        if not namespace or not resource_name:
            return {}

        # Pod investigation
        try:
            pod = self.service.find_pod_by_resource(
                namespace,
                resource_name,
            )
        except Exception:
            pod = None

        if pod:
            pod_name = pod["name"]
            container_name = pod.get("container")

            try:
                details = self.service.get_pod_details(
                    namespace,
                    pod_name,
                )
            except Exception:
                details = None

            try:
                events = self.service.get_pod_events(
                    namespace,
                    pod_name,
                )
            except Exception:
                events = []

            try:
                logs = self.service.get_pod_logs(
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

        # Node investigation
        try:
            node_name = self.service.find_node_by_resource(
                resource_name,
            )
        except Exception:
            node_name = None

        if node_name:
            try:
                details = self.service.get_node_details(
                    node_name
                )
            except Exception:
                details = None

            return {
                "resource_type": "node",
                "node": node_name,
                "details": details,
            }

        return {}
