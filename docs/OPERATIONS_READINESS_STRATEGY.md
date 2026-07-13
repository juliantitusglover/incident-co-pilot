# Operations Readiness Strategy

## Status

- Planning for M10 - Operational Readiness & Diagnostics.
- No runtime behavior is changed by this document.

## Problem

- The backend is runnable and release-healthy after v0.4.0.
- Operational diagnostics are still thin.
- Requests cannot be correlated across responses, logs, and errors.
- `LOG_LEVEL` is configured but not centrally applied by the application.
- Health checks exist, but troubleshooting guidance is limited.
- Better self-hosted debugging should come before larger AI, integration, or frontend surfaces.

## Goals

- Add request correlation with `X-Request-ID`.
- Add central logging configuration using `LOG_LEVEL`.
- Add safe request and error logging.
- Improve health and readiness troubleshooting guidance.
- Add operations/runbook documentation for self-hosted operation.
- Keep logs useful without leaking incident content, API keys, database URLs, request bodies, or secrets.

## Request ID Plan

- Accept `X-Request-ID` when supplied by the caller.
- Generate a request ID when the header is missing.
- Return `X-Request-ID` on every response.
- Store the request ID on request state or an equivalent per-request context for later logging.
- Cover successful responses and error responses.
- Do not change API response bodies in the first request-ID PR unless that is explicitly chosen later.

## Logging Plan

- Apply `LOG_LEVEL` centrally.
- Add safe request completion logs with method, path, status, duration, and request ID.
- Do not log request or response bodies.
- Do not log API keys, authorization headers, database URLs, incident descriptions, or timeline messages.
- Keep logging simple and avoid external logging infrastructure.

## Health/Readiness Plan

- Keep `/health/live` cheap and database-free.
- Keep `/health/ready` focused on database connectivity and required table readiness.
- Document how to interpret readiness failures.
- Keep the Docker healthcheck on liveness unless there is a deliberate reason to change it.

## Operations Docs Plan

- Later add `docs/OPERATIONS.md` or a similar runbook.
- Cover environment variables, startup, migrations, health checks, log level, request IDs, Docker troubleshooting, and safe logging guidance.
- Warn that debug SQL logging can expose sensitive data.

## Out of Scope

- AI features.
- Slack, Jira, Zendesk, or other third-party integrations.
- Frontend work.
- Users, RBAC, OAuth, or JWT.
- Kubernetes, cloud, or platform deployment work.
- Metrics stacks, Prometheus, or distributed tracing services.
- Logging payloads, secrets, API keys, database URLs, or full incident content.
- Broad refactors or logging framework rewrites.

## Proposed PR Sequence

- M10-PR1 - Operational readiness strategy.
- M10-PR2 - Request ID middleware.
- M10-PR3 - Central logging configuration and safe request logs.
- M10-PR4 - Operations/runbook docs and release-checklist operational checks.
- Optional release prep if the milestone is substantial enough.
