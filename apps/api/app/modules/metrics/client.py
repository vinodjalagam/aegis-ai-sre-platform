from __future__ import annotations

import ast
import json
from urllib.parse import urlencode

from kubernetes import client

class PrometheusClient:
    """
    Client for querying Prometheus through the Kubernetes API.

    Prometheus is discovered dynamically inside the selected cluster.
    No Prometheus ClusterIP is hardcoded.
    """

    def __init__(
        self,
        core_v1: client.CoreV1Api,
        namespace: str,
        service: str,
        port: int = 9090,
    ):
        self.core_v1 = core_v1
        self.namespace = namespace
        self.service = service
        self.port = port

    async def query(self, promql: str) -> list[dict]:
        """
        Execute an instant PromQL query through the Kubernetes
        API service proxy.
        """

        query = urlencode({"query": promql})

        resource_path = (
            f"/api/v1/namespaces/"
            f"{self.namespace}/services/"
            f"{self.service}:{self.port}/proxy"
            f"/api/v1/query?{query}"
        )

        response = self.core_v1.api_client.call_api(
            resource_path,
            "GET",
            response_types_map={200: "str"},
            auth_settings=["BearerToken"],
            _return_http_data_only=True,
            _preload_content=True,
        )

        if isinstance(response, bytes):
            response = response.decode("utf-8")

        if isinstance(response, str):
            # Kubernetes Python client returns the response body
            # as a Python dictionary representation.
            payload = ast.literal_eval(response)
        else:
            payload = response

        if payload.get("status") != "success":
            return []

        return payload.get("data", {}).get("result", [])