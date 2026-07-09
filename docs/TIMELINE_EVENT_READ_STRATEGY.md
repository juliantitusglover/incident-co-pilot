# Timeline Event Read/List Strategy

## Status

- Proposed for v0.2.0 development.
- Strategy document only.
- Not implemented yet.

## Current Behavior

- Events can be created, updated, and deleted through nested incident routes.
- Events can be read indirectly through `GET /api/v1/incidents/{incident_id}`.
- No dedicated event list or single-event read routes exist today.
- Incident detail includes nested events, but dedicated event ordering should be made explicit.

## Goals

- Improve API symmetry for timeline event management.
- Let clients fetch an incident timeline without fetching the full incident detail payload.
- Support direct links/edit screens for one timeline event.
- Keep the v0.2.0 change small and easy to test.
- Avoid adding timeline event pagination before there is evidence it is needed.

## Chosen Strategy

- Add dedicated nested read routes in a later implementation PR:
  - `GET /api/v1/incidents/{incident_id}/events`
  - `GET /api/v1/incidents/{incident_id}/events/{event_id}`
- Keep the routes nested under incidents.
- Do not add broad event search/filtering.
- Do not add new event metadata fields.
- Do not add pagination in the initial implementation.

## Proposed Response Shapes

For list:

```json
[
  {
    "id": 1,
    "incident_id": 1,
    "occurred_at": "2026-06-28T13:40:00+01:00",
    "event_type": "update",
    "message": "Investigation started",
    "created_at": "2026-06-28T13:45:35.344353+01:00",
    "updated_at": "2026-06-28T13:45:35.344353+01:00"
  }
]
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
- This matches the current repository ordering.
- It is deterministic and gives clients newest updates first.
- If oldest-first timeline display is needed later, that should be a separate explicit API decision.

## Pagination Decision

- Do not paginate timeline events in the first read/list implementation.
- Timelines are scoped to a single incident and are expected to be smaller than the global incident list.
- If timelines become large later, consider reusing the incident list envelope shape:
  - `items`
  - `limit`
  - `offset`
  - `total`

## Error Behavior

- Missing incident:
  - `404 {"detail": "Incident not found"}`
- Missing event under an existing incident:
  - `404 {"detail": "Event not found"}`
- Event belonging to another incident:
  - `404 {"detail": "Event not found"}`
- This preserves scoped nested-resource behavior and avoids leaking cross-incident event existence.

## Implementation Plan

Later implementation should:

- Add API contract tests for list and get event routes.
- Add or expose usecase `list_events(incident_id)` that validates incident existence.
- Reuse existing `get_event(incident_id, event_id)` usecase if suitable.
- Add GET list route returning `list[TimelineEventRead]`.
- Add GET single route returning `TimelineEventRead`.
- Add OpenAPI metadata for summaries, descriptions, response schemas, and 404s.
- Update README examples.
- Update CHANGELOG.

## Test Plan

Implementation should cover:

- List events returns `200` with ordered events.
- List events for missing incident returns `404 Incident not found`.
- Get event returns `200` with `TimelineEventRead`.
- Get event for missing incident returns `404 Incident not found`.
- Get missing event under existing incident returns `404 Event not found`.
- Get event belonging to another incident returns `404 Event not found`.
- OpenAPI includes both routes, schema refs, and 404 docs.

## Open Questions

- Should future clients ever need oldest-first ordering?
- Should event list pagination be added if timelines become large?
- Should incident detail nested event ordering be aligned explicitly with the dedicated list endpoint?
