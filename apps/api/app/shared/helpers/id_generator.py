"""
Enterprise ID generation utilities.

This module centralizes ID generation across the platform.
Business modules must never directly use third-party ID libraries.
"""

from __future__ import annotations

from ulid import ULID

from app.shared.constants.ids import (
    AGENT_PREFIX,
    ALERT_PREFIX,
    CORRELATION_PREFIX,
    ID_SEPARATOR,
    INCIDENT_PREFIX,
    JOB_PREFIX,
    REQUEST_PREFIX,
    USER_PREFIX,
)


def _generate(prefix: str) -> str:
    """
    Generate a prefixed ULID.
    """
    return f"{prefix}{ID_SEPARATOR}{ULID()}"


def generate_request_id() -> str:
    return _generate(REQUEST_PREFIX)


def generate_correlation_id() -> str:
    return _generate(CORRELATION_PREFIX)


def generate_incident_id() -> str:
    return _generate(INCIDENT_PREFIX)


def generate_alert_id() -> str:
    return _generate(ALERT_PREFIX)


def generate_user_id() -> str:
    return _generate(USER_PREFIX)


def generate_agent_id() -> str:
    return _generate(AGENT_PREFIX)


def generate_job_id() -> str:
    return _generate(JOB_PREFIX)