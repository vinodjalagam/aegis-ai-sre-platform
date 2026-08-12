"""
Kubernetes client wrapper.
"""

from __future__ import annotations

import yaml

from kubernetes import client, config
from kubernetes.config.config_exception import ConfigException


class KubernetesClient:
    """
    Kubernetes client wrapper for a specific cluster.

    The kubeconfig is supplied dynamically for the selected cluster.
    No global ~/.kube/config is used.
    """

    def __init__(self, kubeconfig: str):
        self.kubeconfig = kubeconfig

        self.core_v1: client.CoreV1Api | None = None
        self.apps_v1: client.AppsV1Api | None = None
        self.version_api: client.VersionApi | None = None

    def connect(self) -> None:
        """
        Load the supplied kubeconfig and initialize Kubernetes clients.
        """

        try:
            kubeconfig_dict = yaml.safe_load(self.kubeconfig)

            if not isinstance(kubeconfig_dict, dict):
                raise ValueError(
                    "Invalid kubeconfig: expected YAML object"
                )

            config.load_kube_config_from_dict(
                kubeconfig_dict
            )

            self.core_v1 = client.CoreV1Api()
            self.apps_v1 = client.AppsV1Api()
            self.version_api = client.VersionApi()

        except (
            ConfigException,
            ValueError,
            yaml.YAMLError,
        ) as exc:
            raise RuntimeError(
                f"Failed to load cluster kubeconfig: {exc}"
            ) from exc

    def is_connected(self) -> bool:
        """
        Verify cluster connectivity.
        """

        if self.core_v1 is None:
            self.connect()

        self.core_v1.list_node()

        return True
