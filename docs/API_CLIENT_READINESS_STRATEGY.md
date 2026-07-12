# API Client-Readiness Strategy

## Status

- Planning for M9.
- No runtime behavior is changed by this document.

## Problem

- `GET /api/v1/incidents` is already paginated and client-friendly.
- Incident lists use a response envelope with `items`, `limit`, `offset`, and `total`.
- `GET /api/v1/incidents/{incident_id}/events` currently returns a bare array and is unbounded.
- The timeline event list shape creates generated-client, frontend, and integration special cases.
- OpenAPI error and auth metadata is useful today, but can be clearer for client consumers.

## Goals

- Align the timeline event list with the incident list envelope style.
- Add `limit`, `offset`, and `total` to the timeline event list.
- Preserve auth-disabled local and development behavior.
- Improve OpenAPI metadata and examples for protected incident and timeline flows.
- Improve documented auth and error responses for client consumers.

## Proposed Timeline Event List Contract

Endpoint:

```http
GET /api/v1/incidents/{incident_id}/events
```

Response envelope:

```json
{
  "items": [],
  "limit": 50,
  "offset": 0,
  "total": 0
}
```

Contract details:

- `limit` defaults to `50`.
- `offset` defaults to `0`.
- `limit` has a maximum of `100`.
- Ordering remains `created_at DESC, id DESC`.
- `total` is the total matching event count for the incident before pagination.
- Missing incidents continue to return `404 {"detail": "Incident not found"}`.
- No extra filters are added in the first implementation.

## Compatibility Note

- This changes the timeline event list response from a bare array to an envelope.
- Because Incident Co-Pilot is still pre-1.0 and has no known public consumers, this is acceptable if documented clearly.
- Incident detail embedded events remain unchanged for now.

## Error/OpenAPI Polish

- Add explicit `401` metadata for protected routes.
- Keep `404` metadata for missing incidents and events.
- Add examples for timeline event list, read, create, and update responses where useful.
- Avoid full OpenAPI snapshots; prefer focused metadata assertions.

## Out of Scope

- AI features.
- Slack, Jira, Zendesk, or other third-party integrations.
- Frontend work.
- Users, RBAC, OAuth, or JWT authentication.
- Cursor pagination.
- Search.
- Broad refactors.
- Event date filters.
- Changing incident detail event embedding.

## Proposed PR Sequence

- M9-PR1 - Client-readiness API strategy.
- M9-PR2 - Timeline event list pagination.
- M9-PR3 - OpenAPI/error metadata polish.
- M9-PR4 - README/API docs sync.
- Optional release prep only if the milestone is substantial enough.
