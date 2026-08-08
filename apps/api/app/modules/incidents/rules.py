"""
Incident detection rules.
"""

from app.modules.incidents.enums import (
    IncidentSeverity,
    IncidentSource,
)


class IncidentRules:

    NODE_DOWN = {
        "name": "Node Down",
        "severity": IncidentSeverity.CRITICAL,
        "source": IncidentSource.PROMETHEUS,
        "query": 'up{job="kubelet"} == 0',
        "description": "One or more Kubernetes nodes are unreachable.",
    }

    POD_CRASHLOOP = {
        "name": "CrashLoopBackOff",
        "severity": IncidentSeverity.CRITICAL,
        "source": IncidentSource.PROMETHEUS,
        "query": 'kube_pod_container_status_waiting_reason{reason="CrashLoopBackOff"} > 0',
        "description": "Pod is in CrashLoopBackOff.",
    }

    HIGH_CPU = {
        "name": "High CPU",
        "severity": IncidentSeverity.WARNING,
        "source": IncidentSource.PROMETHEUS,
        "query": '100 - (avg by(instance)(irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 80',
        "description": "CPU utilization exceeded 80%.",
    }
    # HIGH_CPU = {
    # "name": "High CPU",
    # "severity": IncidentSeverity.WARNING,
    # "source": IncidentSource.PROMETHEUS,
    # "query": '100 - (avg by(instance)(irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 10',
    # "description": "CPU utilization exceeded 10%.",
    # }

    HIGH_MEMORY = {
        "name": "High Memory",
        "severity": IncidentSeverity.WARNING,
        "source": IncidentSource.PROMETHEUS,
        "query": '(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100 > 90',
        "description": "Memory utilization exceeded 90%.",
    }

    ALL_RULES = [
        NODE_DOWN,
        POD_CRASHLOOP,
        HIGH_CPU,
        HIGH_MEMORY,
    ]