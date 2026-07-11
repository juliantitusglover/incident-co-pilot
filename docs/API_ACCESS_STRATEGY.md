# API Access Strategy

## Status

- Implemented during M8 development.
- Records the chosen API access-control strategy and implementation reference.
- Optional API key authentication is available for incident and timeline event API routes.

## Current Posture

- Incident Co-Pilot is a self-hosted API with optional shared API key authentication.
- API key authentication is disabled by default for local development.
- When API key authentication is enabled, protected business endpoints require `X-API-Key`.
- Health endpoints and OpenAPI docs remain public.
- The project does not currently have users, sessions, RBAC, OAuth, or JWT authentication.

## Risk

- If the backend is exposed beyond a trusted local or private network with API key authentication disabled, anyone who can reach it can access incident data.
- Incident data may include operational, customer, or sensitive details.
- Shared API key authentication reduces accidental direct exposure risk, but it is not full production identity/security.
- Reverse proxy and network controls still help and are still recommended for exposed deployments.

## Chosen Strategy

- Use optional shared API key authentication.
- Use the `X-API-Key` request header.
- Keep authentication disabled by default for local development.
- When authentication is enabled, require the configured API key for protected business endpoints.
- Keep the implementation dependency-free and easy to test.
- Treat this as basic self-hosted access control, not full production identity or security.

## Configuration

```dotenv
API_AUTH_ENABLED=false
API_KEY=
```

Behavior:

- If `API_AUTH_ENABLED=false`, protected routes behave as they do today.
- If `API_AUTH_ENABLED=true` and `API_KEY` is configured, protected routes require `X-API-Key`.
- If `API_AUTH_ENABLED=true` but `API_KEY` is empty, protected requests fail safely with a server configuration error.

## Protected Endpoints

All `/api/v1/incidents` routes require `X-API-Key` when API authentication is enabled:

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

These endpoints remain public in the first API key implementation:

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

## Implementation Reference

Implementation included:

- `API_AUTH_ENABLED` and `API_KEY` settings.
- Root and backend environment examples.
- A reusable `require_api_key` dependency.
- Router-level protection for incident and nested timeline event routes.
- An OpenAPI API key security scheme for protected incident routes.
- Unit tests for config and dependency behavior.
- Integration tests for protected route behavior.
- OpenAPI metadata tests for protected incident routes and public health routes.
- README and `SECURITY.md` usage/security documentation.

## Test Coverage

Coverage verifies:

- Auth disabled: existing incident tests pass without headers.
- Auth enabled and missing key: protected endpoints are rejected.
- Auth enabled and wrong key: protected endpoints are rejected.
- Auth enabled and correct `X-API-Key`: protected endpoints work.
- Health endpoints remain public.
- OpenAPI documents API key security for incident routes.
- OpenAPI does not mark health routes as protected.

## Open Questions

- Should docs endpoints eventually be disabled or protected for exposed deployments?
- Should future releases support key rotation or multiple API keys?
- Should future releases add proper users/RBAC?
