# Incident List Pagination Strategy

## Status

- Implemented during v0.2.0 development.
- Records the chosen strategy and implementation reference.

## Current Behavior

- `GET /api/v1/incidents` returns a paginated response envelope.
- The endpoint supports `status_filter` and `severity_filter`.
- Results are ordered newest first using `created_at DESC` and `id DESC`.
- Pagination metadata includes `items`, `limit`, `offset`, and `total`.
- `GET /api/v1/incidents/{incident_id}/events` now follows the same limit/offset envelope pattern for timeline event lists.

## Goals

- Keep incident listing usable as data grows.
- Keep the API simple for self-hosted users.
- Preserve deterministic ordering across pages.
- Make the response more useful for clients and future UI work.
- Avoid over-engineering cursor pagination too early.

## Chosen Strategy

Use limit/offset pagination.

Query parameters:

- `limit`: integer, default `50`, minimum `1`, maximum `100`.
- `offset`: integer, default `0`, minimum `0`.

Existing filters remain:

- `status_filter`
- `severity_filter`

Pagination applies after filters and stable ordering.

## Request Examples

```http
GET /api/v1/incidents?limit=50&offset=0
GET /api/v1/incidents?status_filter=open&severity_filter=sev1&limit=25&offset=0
```

## Response Shape

```json
{
  "items": [
    {
      "id": 1,
      "title": "Database Outage",
      "status": "investigating",
      "severity": "sev1",
      "created_at": "...",
      "updated_at": "..."
    }
  ],
  "limit": 50,
  "offset": 0,
  "total": 1
}
```

## Why an Envelope

- Avoids bare-array ambiguity.
- Gives clients pagination metadata.
- Makes room for future metadata without changing the top-level shape again.
- Supports future frontend and integration clients better.

## Why Not Cursor Pagination Yet

- More complex to design and document.
- Requires cursor encoding and decoding decisions.
- Less necessary for the current local/self-hosted maturity stage.
- Can be revisited if large datasets or high write volume become a real concern.

## Backward Compatibility

- This is a breaking response-shape change from v0.1.0.
- Since the project is still pre-1.0, this is acceptable if documented clearly.
- The change is called out in `CHANGELOG.md` and `README.md`.
- Clients using the old bare-array response will need to read from `items`.

## Implementation Reference

The implementation:

- Added pagination query parameters to the route.
- Added an `IncidentListResponse` schema with `items`, `limit`, `offset`, and `total`.
- Updated the usecase/service method signature.
- Updated the repository port and SQLAlchemy implementation.
- Applies filters first, then ordering, then limit/offset.
- Added a count query for `total`.
- Updated API tests, service tests, repository tests, OpenAPI metadata tests, README examples, and changelog.

## Test Plan

Coverage includes:

- Default pagination returns `limit` `50` and `offset` `0`.
- `limit` parameter works.
- `offset` parameter works.
- Limit max validation returns `422`.
- Limit below minimum returns `422`.
- Negative offset returns `422`.
- Filters combine with pagination.
- Ordering remains `created_at DESC`, `id DESC` across pages.
- `total` reflects filtered total, not just page count.
- Response envelope shape is documented in OpenAPI.

## Open Questions

- Should `total` always be included if count queries become expensive?
- Should future cursor pagination replace or coexist with limit/offset?
- Should additional date filters be added separately after pagination?
