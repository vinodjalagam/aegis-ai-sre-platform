from __future__ import annotations

import requests


class PrometheusClient:
    """
    Client for querying Prometheus.
    """

    def __init__(
        self,
        base_url: str = "http://10.43.177.204:9090",
    ):
        self.base_url = base_url.rstrip("/")

    async def query(self, promql: str) -> list[dict]:
        """
        Execute an instant PromQL query.
        """

        response = requests.get(
            f"{self.base_url}/api/v1/query",
            params={"query": promql},
            timeout=10,
        )

        response.raise_for_status()

        payload = response.json()

        if payload.get("status") != "success":
            return []

        return payload["data"]["result"]