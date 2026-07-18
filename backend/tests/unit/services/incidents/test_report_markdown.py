from __future__ import annotations

from datetime import datetime, timezone

from backend.domain.incidents.entities import Incident, TimelineEvent
from backend.domain.incidents.enums import Severity, Status
from backend.services.incidents.report_markdown import render_incident_report_markdown


def _dt(hour: int, minute: int = 0) -> datetime:
    return datetime(2026, 1, 23, hour, minute, tzinfo=timezone.utc)


def _event(
    *,
    event_id: int,
    message: str = "Restarting the primary node.",
    event_type: str = "update",
) -> TimelineEvent:
    return TimelineEvent(
        id=event_id,
        incident_id=1,
        occurred_at=_dt(12, event_id),
        event_type=event_type,
        message=message,
        created_at=_dt(13, event_id),
        updated_at=_dt(14, event_id),
    )


def _incident(
    *,
    events: list[TimelineEvent] | None = None,
    title: str = "Database outage",
    description: str | None = "Primary unavailable",
) -> Incident:
    return Incident(
        id=1,
        title=title,
        description=description,
        severity=Severity.SEV1,
        status=Status.INVESTIGATING,
        created_at=_dt(10),
        updated_at=_dt(11),
        events=events or [],
    )


def test_markdown_report_includes_incident_fields_datetimes_and_enum_values():
    markdown = render_incident_report_markdown(_incident(events=[_event(event_id=10)]))

    assert "# Incident Report: Database outage" in markdown
    assert "- ID: 1" in markdown
    assert "- Severity: sev1" in markdown
    assert "- Status: investigating" in markdown
    assert "- Created at: 2026-01-23T10:00:00+00:00" in markdown
    assert "- Updated at: 2026-01-23T11:00:00+00:00" in markdown
    assert "- Description: Primary unavailable" in markdown
    assert "Severity.SEV1" not in markdown
    assert "Status.INVESTIGATING" not in markdown


def test_markdown_report_includes_timeline_order_count_and_supplied_event_order():
    first = _event(event_id=10, message="First supplied event")
    second = _event(event_id=20, message="Second supplied event")
    markdown = render_incident_report_markdown(_incident(events=[first, second]))

    assert "Timeline order: created_at_desc_id_desc" in markdown
    assert "Timeline event count: 2" in markdown
    assert markdown.index("### Event 10") < markdown.index("### Event 20")
    assert markdown.index("First supplied event") < markdown.index("Second supplied event")


def test_markdown_report_renders_no_events_message():
    markdown = render_incident_report_markdown(_incident(events=[]))

    assert markdown == (
        "# Incident Report: Database outage\n"
        "\n"
        "## Incident\n"
        "\n"
        "- ID: 1\n"
        "- Severity: sev1\n"
        "- Status: investigating\n"
        "- Created at: 2026-01-23T10:00:00+00:00\n"
        "- Updated at: 2026-01-23T11:00:00+00:00\n"
        "- Description: Primary unavailable\n"
        "\n"
        "## Timeline\n"
        "\n"
        "Timeline order: created_at_desc_id_desc\n"
        "Timeline event count: 0\n"
        "\n"
        "_No timeline events recorded._\n"
    )


def test_markdown_report_uses_na_for_missing_description_and_message():
    event = _event(event_id=10, message="")
    markdown = render_incident_report_markdown(
        _incident(description=None, events=[event])
    )

    assert "- Description: N/A" in markdown
    assert markdown.endswith("N/A\n")


def test_markdown_report_escapes_user_authored_markdown():
    incident = _incident(
        title=r"# Title *x* [link](url) \ <tag>",
        description=r"- description | value.",
        events=[
            _event(
                event_id=10,
                event_type=r"note+alert",
                message="**message** with `code` and <html>.",
            )
        ],
    )

    markdown = render_incident_report_markdown(incident)

    assert r"# Incident Report: \# Title \*x\* \[link\]\(url\) \\ \<tag\>" in markdown
    assert r"- Description: \- description \| value\." in markdown
    assert r"- Event type: note\+alert" in markdown
    assert r"\*\*message\*\* with \`code\` and \<html\>\." in markdown


def test_markdown_report_normalizes_heading_and_list_field_newlines():
    incident = _incident(
        title="Title\r\nInjected",
        description="Description\rInjected",
        events=[_event(event_id=10, event_type="note\nInjected")],
    )

    markdown = render_incident_report_markdown(incident)

    assert r"# Incident Report: Title\nInjected" in markdown
    assert r"- Description: Description\nInjected" in markdown
    assert r"- Event type: note\nInjected" in markdown
    assert "Injected\n- Description" not in markdown


def test_markdown_report_preserves_message_line_breaks_while_escaping():
    incident = _incident(events=[_event(event_id=10, message="line *one*\r\nline _two_")])

    markdown = render_incident_report_markdown(incident)

    assert "line \\*one\\*\nline \\_two\\_" in markdown
