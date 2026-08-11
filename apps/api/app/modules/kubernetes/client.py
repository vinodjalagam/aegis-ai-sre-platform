from __future__ import annotations

from kubernetes import client, config
from kubernetes.config.config_exception import ConfigException


class KubernetesClient:
    """
    Kubernetes client wrapper.
    """

    def __init__(
        self,
        kubeconfig_path: str,
    ):
        self.kubeconfig_path = kubeconfig_path

        self.core_v1: client.CoreV1Api | None = None
        self.apps_v1: client.AppsV1Api | None = None
        self.version_api: client.VersionApi | None = None

    def connect(self) -> None:
        """
        Load kubeconfig and initialize clients.
        """

        try:
            config.load_kube_config(
                config_file=self.kubeconfig_path,
            )

            self.core_v1 = client.CoreV1Api()
            self.apps_v1 = client.AppsV1Api()
            self.version_api = client.VersionApi()

        except ConfigException as exc:
            raise RuntimeError(
                f"Failed to load kubeconfig: {exc}"
            ) from exc

    def is_connected(self) -> bool:
        """
        Verify cluster connectivity.
        """

        if self.core_v1 is None:
            self.connect()

        self.core_v1.list_node()

        return True