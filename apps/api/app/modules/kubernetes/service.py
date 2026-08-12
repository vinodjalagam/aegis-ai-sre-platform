from __future__ import annotations

from kubernetes.client import ApiException

from app.modules.kubernetes.client import KubernetesClient


class KubernetesService:
    """
    Service for interacting with Kubernetes clusters.
    """

    def __init__(self, kubeconfig: str):
        self.client = KubernetesClient(kubeconfig)
        self.client.connect()

    def connect(self) -> bool:
        """
        Verify cluster connectivity.
        """
        return self.client.is_connected()

    def get_cluster_summary(self) -> dict:
        """
        Return a summary of the cluster.
        """

        core = self.client.core_v1
        apps = self.client.apps_v1
        version = self.client.version_api

        nodes = core.list_node().items
        namespaces = core.list_namespace().items
        pods = core.list_pod_for_all_namespaces().items
        services = core.list_service_for_all_namespaces().items
        deployments = apps.list_deployment_for_all_namespaces().items
        version_info = version.get_code()

        return {
            "cluster_version": version_info.git_version,
            "nodes": len(nodes),
            "namespaces": len(namespaces),
            "pods": len(pods),
            "services": len(services),
            "deployments": len(deployments),
        }

    def get_nodes(self) -> list[dict]:
        """
        Return all cluster nodes.
        """

        nodes = self.client.core_v1.list_node().items

        result = []

        for node in nodes:

            roles = []

            labels = node.metadata.labels

            if "node-role.kubernetes.io/control-plane" in labels:
                roles.append("control-plane")

            if "node-role.kubernetes.io/master" in labels:
                roles.append("master")

            if not roles:
                roles.append("worker")

            status = "Unknown"

            for condition in node.status.conditions:
                if (
                    condition.type == "Ready"
                    and condition.status == "True"
                ):
                    status = "Ready"

            result.append(
                {
                    "name": node.metadata.name,
                    "status": status,
                    "roles": ", ".join(roles),
                    "kubelet_version": node.status.node_info.kubelet_version,
                    "os": node.status.node_info.operating_system,
                    "architecture": node.status.node_info.architecture,
                }
            )

        return result
    
    def get_node_details(
        self,
        node_name: str,
    ) -> dict | None:
        """
        Return Kubernetes node health information.
        """

        try:
            node = self.client.core_v1.read_node(
                name=node_name,
            )
        except ApiException as exc:
            if exc.status == 404:
                return None
            raise

        conditions = []

        for condition in node.status.conditions or []:
            conditions.append(
                {
                    "type": condition.type,
                    "status": condition.status,
                    "reason": condition.reason,
                    "message": condition.message,
                    "last_transition_time": (
                        condition.last_transition_time.isoformat()
                        if condition.last_transition_time
                        else None
                    ),
                }
            )

        return {
            "name": node.metadata.name,
            "kubelet_version": (
                node.status.node_info.kubelet_version
                if node.status.node_info
                else None
            ),
            "conditions": conditions,
            "unschedulable": node.spec.unschedulable,
        }

    def get_namespaces(self) -> list[str]:
        """
        Return all namespaces.
        """

        namespaces = self.client.core_v1.list_namespace().items

        return [
            namespace.metadata.name
            for namespace in namespaces
        ]

    def get_pods(self) -> list[dict]:
        """
        Return all pods.
        """

        pods = self.client.core_v1.list_pod_for_all_namespaces().items

        result = []

        for pod in pods:
            result.append(
                {
                    "name": pod.metadata.name,
                    "namespace": pod.metadata.namespace,
                    "status": pod.status.phase,
                    "node": pod.spec.node_name,
                }
            )

        return result
        
    def get_pod_details(
        self,
        namespace: str,
        pod_name: str,
    ) -> dict | None:
        """
        Return useful Kubernetes details for a pod.
        """

        try:
            pod = self.client.core_v1.read_namespaced_pod(
                name=pod_name,
                namespace=namespace,
            )
        except ApiException as exc:
            if exc.status == 404:
                return None
            raise

        containers = []

        for container in pod.spec.containers or []:
            status = next(
                (
                    item
                    for item in (pod.status.container_statuses or [])
                    if item.name == container.name
                ),
                None,
            )

            resources = container.resources

            last_terminated = None

            if status and status.last_state and status.last_state.terminated:
                terminated = status.last_state.terminated

                last_terminated = {
                    "reason": terminated.reason,
                    "exit_code": terminated.exit_code,
                    "signal": terminated.signal,
                    "message": terminated.message,
                    "started_at": (
                        terminated.started_at.isoformat()
                        if terminated.started_at
                        else None
                    ),
                    "finished_at": (
                        terminated.finished_at.isoformat()
                        if terminated.finished_at
                        else None
                    ),
                }

            containers.append(
                {
                    "name": container.name,
                    "image": container.image,
                    "restart_count": (
                        status.restart_count
                        if status
                        else 0
                    ),
                    "state": (
                        {
                            "status": "terminated",
                            "reason": status.state.terminated.reason,
                            "exit_code": status.state.terminated.exit_code,
                            "signal": status.state.terminated.signal,
                            "message": status.state.terminated.message,
                            "started_at": (
                                status.state.terminated.started_at.isoformat()
                                if status.state.terminated.started_at
                                else None
                            ),
                            "finished_at": (
                                status.state.terminated.finished_at.isoformat()
                                if status.state.terminated.finished_at
                                else None
                            ),
                        }
                        if status
                        and status.state
                        and status.state.terminated
                        else (
                            {
                                "status": "waiting",
                                "reason": status.state.waiting.reason,
                                "message": status.state.waiting.message,
                            }
                            if status
                            and status.state
                            and status.state.waiting
                            else (
                                {"status": "running"}
                                if status
                                and status.state
                                and status.state.running
                                else None
                            )
                        )
                    ),
                    "last_terminated": last_terminated,
                    "requests": (
                        resources.requests
                        if resources and resources.requests
                        else {}
                    ),
                    "limits": (
                        resources.limits
                        if resources and resources.limits
                        else {}
                    ),
                }
            )

        return {
            "name": pod.metadata.name,
            "namespace": pod.metadata.namespace,
            "phase": pod.status.phase,
            "node": pod.spec.node_name,
            "pod_ip": pod.status.pod_ip,
            "restart_policy": pod.spec.restart_policy,
            "containers": containers,
        }

    def get_pod_logs(
        self,
        namespace: str,
        pod_name: str,
        container_name: str | None = None,
        previous: bool = False,
    ) -> str:
        """
        Return pod/container logs.
        """

        try:
            return self.client.core_v1.read_namespaced_pod_log(
                name=pod_name,
                namespace=namespace,
                container=container_name,
                previous=previous,
                tail_lines=200,
            )
        except ApiException as exc:
            if exc.status == 400 and previous:
                return ""

            if exc.status == 404:
                return ""

            raise
            
    def get_pod_events(
        self,
        namespace: str,
        pod_name: str,
    ) -> list[dict]:
        """
        Return Kubernetes events associated with a pod.
        """

        events = self.client.core_v1.list_namespaced_event(
            namespace=namespace,
            field_selector=f"involvedObject.name={pod_name}",
        ).items

        result = []

        for event in events:
            result.append(
                {
                    "type": event.type,
                    "reason": event.reason,
                    "message": event.message,
                    "count": event.count,
                    "first_timestamp": (
                        event.first_timestamp.isoformat()
                        if event.first_timestamp
                        else None
                    ),
                    "last_timestamp": (
                        event.last_timestamp.isoformat()
                        if event.last_timestamp
                        else None
                    ),
                }
            )

        return result
    
    def find_pod_by_resource(
        self,
        namespace: str,
        resource_name: str,
    ) -> dict | None:
        """
        Find a pod by name or Prometheus resource name.
        """

        pods = self.client.core_v1.list_namespaced_pod(
            namespace=namespace,
        ).items

        # First try the actual Kubernetes pod name.
        for pod in pods:
            if pod.metadata.name == resource_name:
                return {
                    "name": pod.metadata.name,
                    "namespace": pod.metadata.namespace,
                    "container": (
                        pod.spec.containers[0].name
                        if pod.spec.containers
                        else None
                    ),
                }

        # Fallback: Prometheus may return IP:port.
        pod_ip = resource_name.split(":")[0]

        for pod in pods:
            if pod.status.pod_ip == pod_ip:
                return {
                    "name": pod.metadata.name,
                    "namespace": pod.metadata.namespace,
                    "container": (
                        pod.spec.containers[0].name
                        if pod.spec.containers
                        else None
                    ),
                }

        return None
    
    def find_node_by_resource(
        self,
        resource_name: str,
    ) -> str | None:
        """
        Find a Kubernetes node by name or Prometheus resource name.
        """

        nodes = self.client.core_v1.list_node().items

        # First try node name.
        for node in nodes:
            if node.metadata.name == resource_name:
                return node.metadata.name

        # Fallback: Prometheus may return IP:port.
        node_ip = resource_name.split(":")[0]

        for node in nodes:
            if not node.status.addresses:
                continue

            for address in node.status.addresses:
                if (
                    address.type == "InternalIP"
                    and address.address == node_ip
                ):
                    return node.metadata.name

        return None
    
    def get_services(self) -> list[dict]:
        """
        Return all services.
        """

        services = (
            self.client.core_v1
            .list_service_for_all_namespaces()
            .items
        )

        result = []

        for service in services:

            result.append(
                {
                    "name": service.metadata.name,
                    "namespace": service.metadata.namespace,
                    "type": service.spec.type,
                    "cluster_ip": service.spec.cluster_ip,
                }
            )

        return result

    def get_deployments(self) -> list[dict]:
        """
        Return all deployments.
        """

        deployments = (
            self.client.apps_v1
            .list_deployment_for_all_namespaces()
            .items
        )

        result = []

        for deployment in deployments:

            result.append(
                {
                    "name": deployment.metadata.name,
                    "namespace": deployment.metadata.namespace,
                    "replicas": deployment.spec.replicas,
                    "available": deployment.status.available_replicas or 0,
                }
            )

        return result
    def get_replicasets(self) -> list[dict]:
        """
        Return all ReplicaSets.
        """

        replicasets = (
            self.client.apps_v1
            .list_replica_set_for_all_namespaces()
            .items
        )

        result = []

        for replicaset in replicasets:
            result.append(
                {
                    "name": replicaset.metadata.name,
                    "namespace": replicaset.metadata.namespace,
                    "replicas": replicaset.spec.replicas,
                    "ready": (
                        replicaset.status.ready_replicas
                        or 0
                    ),
                }
            )

        return result
    
    def get_statefulsets(self) -> list[dict]:
        """
        Return all StatefulSets.
        """

        statefulsets = (
            self.client.apps_v1
            .list_stateful_set_for_all_namespaces()
            .items
        )

        result = []

        for statefulset in statefulsets:
            result.append(
                {
                    "name": statefulset.metadata.name,
                    "namespace": statefulset.metadata.namespace,
                    "replicas": statefulset.spec.replicas,
                    "ready": (
                        statefulset.status.ready_replicas
                        or 0
                    ),
                }
            )

        return result

    def get_daemonsets(self) -> list[dict]:
        """
        Return all DaemonSets.
        """

        daemonsets = (
            self.client.apps_v1
            .list_daemon_set_for_all_namespaces()
            .items
        )

        result = []

        for daemonset in daemonsets:
            result.append(
                {
                    "name": daemonset.metadata.name,
                    "namespace": daemonset.metadata.namespace,
                    "desired": (
                        daemonset.status.desired_number_scheduled
                        or 0
                    ),
                    "ready": (
                        daemonset.status.number_ready
                        or 0
                    ),
                }
            )

        return result