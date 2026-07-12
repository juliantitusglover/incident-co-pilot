# Timeline Event Read/List Strategy

## Status

- Implemented during v0.2.0 development.
- This document records the strategy that was chosen and implemented.
- Dedicated timeline event read/list routes are now available.
- M9-PR2 added pagination to the dedicated timeline event list route.

## Current Behavior

- Events can be created, updated, and deleted through nested incident routes.
- Events can be read indirectly through `GET /api/v1/incidents/{incident_id}`.
- Dedicated event list and single-event read routes are now available:
  - `GET /api/v1/incidents/{incident_id}/events`
  - `GET /api/v1/incidents/{incident_id}/events/{event_id}`
- The dedicated event list returns a paginated envelope with `items`, `limit`, `offset`, and `total`.
- Incident detail includes nested events as a plain list, and its ordering is aligned with the dedicated event list route.

## Goals

- Improve API symmetry for timeline event management.
- Let clients fetch an incident timeline without fetching the full incident detail payload.
- Support direct links/edit screens for one timeline event.
- Keep the v0.2.0 change small and easy to test.
- Keep timeline event pagination simple and consistent with incident list pagination.

## Implemented Strategy

- Add dedicated nested read routes:
  - `GET /api/v1/incidents/{incident_id}/events`
  - `GET /api/v1/incidents/{incident_id}/events/{event_id}`
- Keep the routes nested under incidents.
- Do not add broad event search/filtering.
- Do not add new event metadata fields.
- Add limit/offset pagination to the dedicated list route.

## Response Shapes

For list:

```json
{
  "items": [
    {
      "id": 1,
      "incident_id": 1,
      "occurred_at": "2026-06-28T13:40:00+01:00",
      "event_type": "update",
      "message": "Investigation started",
      "created_at": "2026-06-28T13:45:35.344353+01:00",
      "updated_at": "2026-06-28T13:45:35.344353+01:00"
    }
  ],
  "limit": 50,
  "offset": 0,
  "total": 1
}
```

For single event:

```json
{
  "id": 1,
  "incident_id": 1,
  "occurred_at": "2026-06-28T13:40:00+01:00",
  "event_type": "update",
  "message": "Investigation started",
  "created_at": "2026-06-28T13:45:35.344353+01:00",
  "updated_at": "2026-06-28T13:45:35.344353+01:00"
}
```

## Ordering

- Dedicated event list should return events ordered by `created_at DESC, id DESC`.
- Incident detail nested events use the same `created_at DESC, id DESC` ordering.
- This matches the current repository ordering.
- It is deterministic and gives clients newest updates first.
- If oldest-first timeline display is needed later, that should be a separate explicit API decision.

## Pagination Decision

- The dedicated timeline event list now reuses the incident list envelope shape:
  - `items`
  - `limit`
  - `offset`
  - `total`
- `limit` defaults to `50`, has a minimum of `1`, and has a maximum of `100`.
- `offset` defaults to `0` and has a minimum of `0`.
- `total` is the total matching event count for the incident before pagination.
- No timeline event filters are added yet.

## Error Behavior

- Missing incident:
  - `404 {"detail": "Incident not found"}`
- Missing event under an existing incident:
  - `404 {"detail": "Event not found"}`
- Event belonging to another incident:
  - `404 {"detail": "Event not found"}`
- This preserves scoped nested-resource behavior and avoids leaking cross-incident event existence.

## Implementation Reference

Implementation included:

- API contract tests for list and get event routes.
- Usecase `list_events(incident_id, limit, offset)` that validates incident existence.
- Existing `get_event(incident_id, event_id)` usecase reused for single-event reads.
- GET list route returning a timeline event list envelope.
- GET single route returning `TimelineEventRead`.
- OpenAPI metadata for summaries, descriptions, response schemas, and 404s.
- CHANGELOG entry.

## Test Coverage

Implementation coverage includes:

- List events returns `200` with ordered events inside a pagination envelope.
- List events validates `limit` and `offset`.
- List events for missing incident returns `404 Incident not found`.
- Get event returns `200` with `TimelineEventRead`.
- Get event for missing incident returns `404 Incident not found`.
- Get missing event under existing incident returns `404 Event not found`.
- Get event belonging to another incident returns `404 Event not found`.
- Incident detail returns nested events ordered by `created_at DESC, id DESC`.
- OpenAPI includes both routes, schema refs, and 404 docs.

## Open Questions

- Should future clients ever need oldest-first ordering?
- Should timeline event filters be added separately if clients need them?
