# Operations Readiness Strategy

## Status

- M10 - Operational Readiness & Diagnostics is implemented and in v0.5.0 release prep.
- M10-PR1 added the operational readiness strategy.
- M10-PR2 implemented request ID middleware.
- M10-PR3 implemented central logging configuration and safe request-completion logs.
- M10-PR4 added operations documentation and release-checklist operational diagnostics checks.
- M10-PR5 found no release blockers during operational readiness inspection.
- This document reflects current request ID, logging, health/readiness, and operations documentation behavior.

## Problem

- The backend is runnable and release-healthy for the v0.5.0 release-prep milestone.
- Operational diagnostics now include request correlation, request-completion logs, and basic operations guidance.
- Requests can now be correlated across responses and request-completion logs.
- `LOG_LEVEL` is applied centrally to the backend package logger.
- Health checks exist, and basic troubleshooting guidance is documented.
- Better self-hosted debugging should come before larger AI, integration, or frontend surfaces.

## Goals

- Add request correlation with `X-Request-ID`.
- Add central logging configuration using `LOG_LEVEL`.
- Add safe request and error logging.
- Improve health and readiness troubleshooting guidance.
- Add operations/runbook documentation for self-hosted operation.
- Keep logs useful without leaking incident content, API keys, database URLs, request bodies, or secrets.

## Request ID Current Behavior

- Accepts `X-Request-ID` when supplied by the caller.
- Preserves non-blank caller-provided request IDs after trimming whitespace.
- Generates a request ID when `X-Request-ID` is missing, blank, or longer than 128 characters.
- Returns `X-Request-ID` on API responses, including success responses and error responses.
- Stores the request ID on `request.state.request_id` for future logging.
- Keeps API response bodies unchanged.

## Logging Current Behavior

- Uses Python standard-library logging.
- Applies `LOG_LEVEL` centrally to the backend package logger at app creation.
- Falls back to `INFO` for invalid `LOG_LEVEL` values.
- Does not force the root logger to `DEBUG`.
- Does not modify Uvicorn loggers.
- Emits one safe request-completion log per HTTP request.
- Request-completion logs include `request_id`, method, path, status code, and duration in milliseconds.
- Request-completion logs intentionally exclude query strings, request bodies, response bodies, request headers, response headers, API keys, authorization headers, database URLs, incident descriptions, and timeline messages.
- Request-completion logs cover successful responses, handled errors, auth `401` responses, validation `422` responses, and unhandled `500` responses.
- Keeps API response bodies unchanged.
- Keeps logging simple and avoids JSON logging, metrics, tracing, or external logging infrastructure.
- SQLAlchemy echo behavior remains tied to `DEBUG`; treat `DEBUG=true` as potentially sensitive because SQL logging can expose operational or incident data.

## Health/Readiness Current Behavior

- Keep `/health/live` cheap and database-free.
- Keep `/health/ready` focused on database connectivity and required table readiness.
- `docs/OPERATIONS.md` documents how to interpret readiness failures.
- The Docker healthcheck remains on liveness.

## Operations Docs Current Behavior

- `docs/OPERATIONS.md` covers environment variables, startup, migrations, health checks, log level, request IDs, Docker troubleshooting, and safe logging guidance.
- `docs/RELEASE_CHECKLIST.md` includes operational diagnostics smoke checks for request IDs, request-completion logs, and readiness after migrations.
- The operations docs warn that debug SQL logging can expose sensitive data.

## Out of Scope

- AI features.
- Slack, Jira, Zendesk, or other third-party integrations.
- Frontend work.
- Users, RBAC, OAuth, or JWT.
- Kubernetes, cloud, or platform deployment work.
- Metrics stacks, Prometheus, or distributed tracing services.
- Logging payloads, secrets, API keys, database URLs, or full incident content.
- Broad refactors or logging framework rewrites.

## Implemented PR Sequence

- M10-PR1 - Operational readiness strategy.
- M10-PR2 - Request ID middleware.
- M10-PR3 - Central logging configuration and safe request logs.
- M10-PR4 - Operations/runbook docs and release-checklist operational checks.
- M10-PR5 - Operational readiness release review.
- M10-PR6 - v0.5.0 release prep.
