# API Client-Readiness Strategy

## Status

- Implemented during M9.
- Prepared for the v0.4.0 release.
- M9-PR2 implemented timeline event list pagination.
- M9-PR3 implemented OpenAPI/auth/error metadata polish without runtime behavior changes.
- M9-PR4 completed README/API docs sync without runtime behavior changes.

## Problem

- `GET /api/v1/incidents` is already paginated and client-friendly.
- Incident lists use a response envelope with `items`, `limit`, `offset`, and `total`.
- `GET /api/v1/incidents/{incident_id}/events` now uses the same envelope style.
- The timeline event list changed from a bare array to an envelope in M9-PR2.
- OpenAPI error and auth metadata is useful today, but can be clearer for client consumers.

## Goals

- Align the timeline event list with the incident list envelope style.
- Add `limit`, `offset`, and `total` to the timeline event list.
- Preserve auth-disabled local and development behavior.
- Improve OpenAPI metadata and examples for protected incident and timeline flows.
- Improve documented auth and error responses for client consumers.

## Implemented Timeline Event List Contract

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

- M9-PR2 changed the timeline event list response from a bare array to an envelope.
- Because Incident Co-Pilot is still pre-1.0 and has no known public consumers, this is acceptable if documented clearly.
- Incident detail embedded events remain unchanged for now.

## Implemented Error/OpenAPI Polish

- Added explicit `401` metadata for protected incident and timeline routes.
- Documented the API key auth error example as `{"detail": "Invalid or missing API key"}`.
- Kept health routes public in OpenAPI metadata with no `401` response metadata.
- Added a concrete timeline event list response example for the paginated envelope.
- Improved the timeline event list description to mention pagination and `created_at DESC, id DESC` ordering.
- Kept runtime auth behavior and exception handlers unchanged.

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
- M9-PR2 - Timeline event list pagination. Done.
- M9-PR3 - OpenAPI/error metadata polish. Done.
- M9-PR4 - README/API docs sync. Done.
- M9-PR6 - v0.4.0 release prep. Done.
