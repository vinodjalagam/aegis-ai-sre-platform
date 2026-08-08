from enum import Enum


class IncidentSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class IncidentStatus(str, Enum):
    OPEN = "open"
    RESOLVED = "resolved"


class IncidentSource(str, Enum):
    KUBERNETES = "kubernetes"
    PROMETHEUS = "prometheus"