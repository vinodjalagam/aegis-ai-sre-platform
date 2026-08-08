"""
Utilities for validating platform identifiers.
"""

from __future__ import annotations


def is_request_id(value: str) -> bool:
    """Return True if the value looks like a request ID."""
    return value.startswith("REQ-")


def is_correlation_id(value: str) -> bool:
    """Return True if the value looks like a correlation ID."""
    return value.startswith("CORR-")


def is_incident_id(value: str) -> bool:
    """Return True if the value looks like an incident ID."""
    return value.startswith("INC-")