# Incident Reports & Timeline Export Strategy

## Status

- M11-PR2 structured JSON report endpoint is implemented.
- M11-PR3 Markdown export endpoint is implemented.
- OpenAPI examples and docs remain planned for M11-PR4.
- Target release: v0.6.0.
- v0.5.0 operational readiness is complete.

## Goal

- Add deterministic, non-AI incident report/export capability.
- Make incident data easier to review, share, and use after an incident.
- Provide structured JSON and Markdown export surfaces.

## Non-Goals

- AI-generated summaries.
- LLM calls.
- Root-cause inference.
- Impact, duration, action-item, owner, or customer-impact fields not represented in the current domain.
- Slack, Jira, Zendesk, or other third-party integrations.
- Frontend work.
- PDF generation.
- Background jobs.
- A new auth model.
- Users, RBAC, OAuth, or JWT.
- New database tables unless a future concrete requirement proves they are necessary.
- Metrics or tracing.
- Broad refactors.

## Available Source Data

Existing incident fields:

- `id`
- `title`
- `description`
- `severity`
- `status`
- `created_at`
- `updated_at`
- `events`

Existing status values:

- `open`
- `investigating`
- `mitigated`
- `resolved`

No `resolved_at` field exists yet.

Existing timeline event fields:

- `id`
- `incident_id`
- `occurred_at`
- `event_type`
- `message`
- `created_at`
- `updated_at`

Timeline ordering preserves the current API ordering: `created_at DESC, id DESC`.

## Structured JSON Endpoint

Endpoint:

```text
GET /api/v1/incidents/{incident_id}/report
```

The report endpoint lives under the existing incidents router. It inherits the existing API key auth behavior used by incident and timeline event routes when `API_AUTH_ENABLED=true`.

Request IDs and safe request-completion logging apply automatically through the existing middleware. No special report-specific logging is needed.

Missing incidents use the existing `404` response shape:

```json
{
  "detail": "Incident not found"
}
```

The route is declared before `GET /api/v1/incidents/{incident_id}` so FastAPI does not treat `report` as an `incident_id`.

## JSON Response Shape

Implemented response shape:

```json
{
  "incident": {
    "id": 1,
    "title": "Database Outage",
    "description": "Production DB is down",
    "status": "investigating",
    "severity": "sev1",
    "created_at": "2026-01-23T12:00:00Z",
    "updated_at": "2026-01-23T12:05:00Z"
  },
  "timeline_events": [
    {
      "id": 2,
      "incident_id": 1,
      "occurred_at": "2026-01-23T12:01:00Z",
      "event_type": "update",
      "message": "Restarting the primary node.",
      "created_at": "2026-01-23T12:02:00Z",
      "updated_at": "2026-01-23T12:02:00Z"
    }
  ],
  "timeline_order": "created_at_desc_id_desc",
  "timeline_event_count": 1
}
```

Incidents with no timeline events return an empty `timeline_events` list and `timeline_event_count` of `0`.

Avoid unsupported fields:

- `resolved_at`
- `owner`
- `impact`
- `duration`
- `root_cause`
- `customer_impact`
- `action_items`
- generated summaries

## Markdown Export Endpoint

Endpoint:

```text
GET /api/v1/incidents/{incident_id}/report/markdown
```

The Markdown export endpoint is implemented as a separate endpoint so the structured JSON contract stays clean and presentation text remains deterministic. Markdown output is non-AI and does not include generated summaries, analysis, root-cause inference, PDF export, or unsupported incident fields.

The endpoint returns `text/markdown` and reuses the existing report data-loading path. The renderer accepts an already loaded incident, does not query the database, does not sort timeline events, and preserves the loaded timeline event ordering.

Markdown output uses existing incident and timeline fields only. It includes:

- Incident heading and supported incident fields.
- `timeline_order` as `created_at_desc_id_desc`.
- `timeline_event_count`.
- Timeline event sections.
- `_No timeline events recorded._` when no timeline events exist.

Markdown rendering uses `datetime.isoformat()` for datetimes, enum values such as `sev1` and `investigating`, and minimal Markdown escaping for user-authored `title`, `description`, `event_type`, and `message` fields.

The endpoint lives under the existing incidents router. It inherits existing API key auth behavior, `X-Request-ID` response headers, and safe request-completion logging through the existing middleware.

## M11 PR Sequence

- M11-PR1 - Incident report/export strategy.
- M11-PR2 - Structured incident report JSON endpoint. Implemented.
- M11-PR3 - Markdown report export. Implemented.
- M11-PR4 - OpenAPI examples and docs.
- M11-PR5 - Report/export release review.
- M11-PR6 - Prepare v0.6.0 release.

## Current Test Coverage

- Report success returns incident plus timeline events.
- Missing incident returns `404`.
- Timeline ordering uses `created_at DESC, id DESC`.
- Incident with no timeline events returns empty `timeline_events` and count `0`.
- Markdown export returns `text/markdown`.
- Markdown export includes the no-events message when no timeline events exist.
- Markdown export preserves loaded event ordering and escapes user-authored Markdown-sensitive fields.
- Auth-enabled missing key returns `401`.
- Response includes `X-Request-ID`.
- Minimal OpenAPI metadata covers report auth, error responses, and Markdown media type.
- Richer OpenAPI examples and docs remain planned for M11-PR4.
