# Incident List Pagination Strategy

## Status

- Proposed for v0.2.0.
- Strategy document only.
- Not implemented yet.

## Current Behavior

- `GET /api/v1/incidents` returns a bare array.
- The endpoint supports `status_filter` and `severity_filter`.
- Results are ordered newest first using `created_at DESC` and `id DESC`.
- No pagination metadata exists today.

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

## Proposed Request Examples

```http
GET /api/v1/incidents?limit=50&offset=0
GET /api/v1/incidents?status_filter=open&severity_filter=sev1&limit=25&offset=0
```

## Proposed Response Shape

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
- The change should be called out in `CHANGELOG.md` and `README.md` when implemented.
- Clients using the old bare-array response will need to read from `items`.

## Implementation Plan

Later implementation should:

- Add pagination query parameters to the route.
- Add an `IncidentListResponse` schema with `items`, `limit`, `offset`, and `total`.
- Update the usecase/service method signature.
- Update the repository port and SQLAlchemy implementation.
- Apply filters first, then ordering, then limit/offset.
- Add a count query for `total`.
- Update API tests, service tests, repository tests, OpenAPI metadata tests, README examples, and changelog.

## Test Plan

Implementation should cover:

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
