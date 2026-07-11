# API Access Strategy

## Status

- Proposed for M8 development.
- Strategy document only.
- Not implemented yet.

## Current Posture

- Incident Co-Pilot is currently a self-hosted unauthenticated API.
- Business endpoints can read, create, update, and delete incident data if the backend is reachable.
- Health endpoints and OpenAPI docs are public.
- The project does not currently have users, sessions, RBAC, OAuth, or JWT authentication.
- An empty auth router namespace exists, but it does not protect any route.

## Risk

- If the backend is exposed beyond a trusted local or private network, anyone who can reach it can access incident data.
- Incident data may include operational, customer, or sensitive details.
- Reverse proxy and network controls help, but they are easy to misconfigure.

## Chosen Strategy

- Add optional shared API key authentication in a later implementation PR.
- Use the `X-API-Key` request header.
- Keep authentication disabled by default for local development.
- When authentication is enabled, require the configured API key for protected business endpoints.
- Keep the implementation dependency-free and easy to test.
- Treat this as basic self-hosted access control, not full production identity or security.

## Proposed Configuration

```dotenv
API_AUTH_ENABLED=false
API_KEY=
```

Behavior:

- If `API_AUTH_ENABLED=false`, protected routes behave as they do today.
- If `API_AUTH_ENABLED=true` and `API_KEY` is configured, protected routes require `X-API-Key`.
- If `API_AUTH_ENABLED=true` but `API_KEY` is empty, startup or requests should fail safely. Confirm the exact failure mode during implementation.

## Protected Endpoints

All `/api/v1/incidents` routes should require `X-API-Key` when API authentication is enabled:

- `GET /api/v1/incidents`
- `POST /api/v1/incidents`
- `GET /api/v1/incidents/{incident_id}`
- `PATCH /api/v1/incidents/{incident_id}`
- `DELETE /api/v1/incidents/{incident_id}`
- `GET /api/v1/incidents/{incident_id}/events`
- `POST /api/v1/incidents/{incident_id}/events`
- `GET /api/v1/incidents/{incident_id}/events/{event_id}`
- `PATCH /api/v1/incidents/{incident_id}/events/{event_id}`
- `DELETE /api/v1/incidents/{incident_id}/events/{event_id}`

## Public Endpoints

These endpoints should remain public in the first API key implementation:

- `GET /health/live`
- `GET /health/ready`
- `/docs`
- `/redoc`
- `/openapi.json`

Exposed deployments may still restrict docs endpoints at the reverse proxy.

## Why Not JWT/User Accounts Yet

- No user model exists.
- JWT or user accounts would require storage, password/session/security policy decisions, migrations, and a larger test/docs burden.
- They are not necessary for the first self-hosted access-control boundary.

## Why Not Reverse Proxy Only

- Reverse proxy access control is useful and still recommended for exposed deployments.
- Reverse proxy guidance alone does not protect users who accidentally expose the app directly.
- A simple in-app API key is a safer baseline for the current self-hosted project stage.

## Implementation Plan

Later implementation PRs should:

- Add `API_AUTH_ENABLED` and `API_KEY` settings.
- Add environment examples.
- Add a `require_api_key` dependency.
- Attach the dependency to the incident router or router include.
- Add an OpenAPI API key security scheme.
- Add tests for disabled, missing, wrong, and correct keys.
- Confirm health endpoints remain public.
- Update README curl examples and `SECURITY.md`.

## Test Plan

Later test coverage should verify:

- Auth disabled: existing incident tests pass without headers.
- Auth enabled and missing key: protected endpoints are rejected.
- Auth enabled and wrong key: protected endpoints are rejected.
- Auth enabled and correct `X-API-Key`: protected endpoints work.
- Health endpoints remain public.
- OpenAPI documents API key security for incident routes.
- OpenAPI does not mark health routes as protected.

## Open Questions

- Should `API_AUTH_ENABLED=true` with empty `API_KEY` fail at startup or reject every protected request with a clear server configuration error?
- Should docs endpoints eventually be disabled or protected for exposed deployments?
- Should future releases support key rotation or multiple API keys?
- Should future releases add proper users/RBAC?
