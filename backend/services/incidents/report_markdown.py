from __future__ import annotations

from datetime import datetime
from enum import Enum

from backend.domain.incidents.entities import Incident


TIMELINE_ORDER = "created_at_desc_id_desc"
_MARKDOWN_ESCAPE_CHARS = set(r"`*_{}[]()#+-.!|<>")


def render_incident_report_markdown(incident: Incident) -> str:
    lines = [
        f"# Incident Report: {_escape_single_line(incident.title)}",
        "",
        "## Incident",
        "",
        f"- ID: {incident.id}",
        f"- Severity: {_enum_value(incident.severity)}",
        f"- Status: {_enum_value(incident.status)}",
        f"- Created at: {_isoformat(incident.created_at)}",
        f"- Updated at: {_isoformat(incident.updated_at)}",
        f"- Description: {_description(incident.description)}",
        "",
        "## Timeline",
        "",
        f"Timeline order: {TIMELINE_ORDER}",
        f"Timeline event count: {len(incident.events)}",
        "",
    ]

    if not incident.events:
        lines.append("_No timeline events recorded._")
        return "\n".join(lines) + "\n"

    for index, event in enumerate(incident.events):
        if index:
            lines.append("")
        lines.extend(
            [
                f"### Event {event.id}",
                "",
                f"- Event type: {_escape_single_line(event.event_type)}",
                f"- Occurred at: {_isoformat(event.occurred_at)}",
                f"- Created at: {_isoformat(event.created_at)}",
                f"- Updated at: {_isoformat(event.updated_at)}",
                "",
                _message(event.message),
            ]
        )

    return "\n".join(lines) + "\n"


def _description(value: str | None) -> str:
    if not value:
        return "N/A"
    return _escape_single_line(value)


def _message(value: str | None) -> str:
    if not value:
        return "N/A"
    return _escape_markdown(value).replace("\r\n", "\n").replace("\r", "\n")


def _escape_single_line(value: str) -> str:
    escaped = _escape_markdown(value)
    return escaped.replace("\r\n", r"\n").replace("\r", r"\n").replace("\n", r"\n")


def _escape_markdown(value: str) -> str:
    value = value.replace("\\", "\\\\")
    return "".join(
        f"\\{character}" if character in _MARKDOWN_ESCAPE_CHARS else character
        for character in value
    )


def _enum_value(value: object) -> str:
    if isinstance(value, Enum):
        return str(value.value)
    return str(value)


def _isoformat(value: datetime) -> str:
    return value.isoformat()
