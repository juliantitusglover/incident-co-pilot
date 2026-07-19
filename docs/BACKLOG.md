# Backlog

This backlog collects candidate issues for future work. It is a planning aid, not a commitment. GitHub issues can be created from this document when ready.

## Priority Legend

- `must-have`: needed for the next target release.
- `should-have`: valuable but not release-blocking.
- `could-have`: useful if capacity allows.
- `later`: intentionally deferred.
- `done`: completed in the noted milestone or workstream.

## v0.2.0 Candidate Backlog

These items are candidates for planning around v0.2.0. They are not guaranteed release contents.

### API Usability

- [done] Decide and document incident list pagination strategy. See [Pagination strategy](PAGINATION_STRATEGY.md).
- [done] Implement incident list pagination.
- [done] Document incident list sort order.
- [done] Add OpenAPI examples for status/severity filters and pagination.
- [done] Add README examples for paginated incident lists.

### Timeline Event Usability

- [done] Decide whether timeline events need read/list endpoints. See [Timeline event read strategy](TIMELINE_EVENT_READ_STRATEGY.md).
- [done] Add list timeline events endpoint.
- [done] Add get timeline event endpoint.
- [done] Add API docs/examples for timeline event reads.
- [done] Document timeline event ordering expectations.

### API Contract Clarity

- [should-have] Add request/response examples to OpenAPI metadata.
- [should-have] Add documented error examples for 400, 404, and 422.
- [could-have] Add small OpenAPI contract smoke check for example presence.
- [could-have] Review route tags and summary consistency after new endpoints.

### Operational Polish

- [should-have] Decide whether to centralize version sources.
- [could-have] Implement version-source centralization if the decision is clear.
- [could-have] Add demo/seed data script for local testing.
- [could-have] Improve Docker image build caching or size if needed.

## M8 Candidate Backlog

These items track API access-control work after v0.2.0. Completed items are marked `done`; future hardening remains marked `later`.

### Security/API Access

- [done] Add API access strategy documentation. See [API access strategy](API_ACCESS_STRATEGY.md).
- [done] Add `API_AUTH_ENABLED` and `API_KEY` settings.
- [done] Add API auth environment examples.
- [done] Add a `require_api_key` dependency.
- [done] Add unit tests for API key dependency behavior.
- [done] Protect incident and timeline event routes when API auth is enabled.
- [done] Add integration tests for route auth behavior.
- [done] Add OpenAPI security metadata coverage for protected incident routes.
- [done] Update README API auth documentation.
- [done] Update `SECURITY.md` API auth expectations.
- [done] Update API access strategy status after implementation.

### Future Security/API Access

- [later] Decide whether docs endpoints should be protected for exposed deployments.
- [later] Decide whether to support multiple API keys or key rotation workflow.
- [later] Decide whether to add users/RBAC.
- [later] Revisit broader production hardening.

## M9 Client-Ready API Contracts

These items track completed client-readiness API polish for the existing incident and timeline API.

### Client-Readiness API Polish

- [done] Add client-readiness API strategy documentation. See [API client-readiness strategy](API_CLIENT_READINESS_STRATEGY.md).
- [done] Add timeline event list pagination and a response envelope.
- [done] Polish OpenAPI auth and error response metadata for protected routes.
- [done] Sync README/API docs after contract changes land.

## M10 Operational Readiness & Diagnostics

These items track basic self-hosted diagnostics work for running, debugging, and supporting the existing backend.

### Operational Diagnostics

- [done] Add operational readiness strategy documentation. See [Operations readiness strategy](OPERATIONS_READINESS_STRATEGY.md).
- [done] Add request ID middleware using `X-Request-ID`.
- [done] Apply central logging configuration from `LOG_LEVEL`.
- [done] Add safe request and error logging without payloads or secrets.
- [done] Add health/readiness troubleshooting docs.
- [done] Add operations/runbook docs.
- [done] Add release-checklist operational diagnostics checks.
- [later] Revisit platform deployment guidance, metrics infrastructure, or distributed tracing only after basic diagnostics are in place.

## M11 Incident Reports & Timeline Export

These items track deterministic, non-AI incident report/export work for the v0.6.0 target release.

### Report/Export Planning

- [must-have] Add incident report/export strategy documentation. See [Incident reports strategy](INCIDENT_REPORTS_STRATEGY.md).
- [done] Add structured report JSON schema and `GET /api/v1/incidents/{incident_id}/report`.
- [done] Preserve timeline ordering as `created_at DESC, id DESC`.
- [done] Cover the no-events report case with empty `timeline_events` and count `0`.
- [done] Verify existing auth and `X-Request-ID` behavior on report routes.
- [done] Add deterministic Markdown export at `GET /api/v1/incidents/{incident_id}/report/markdown`.
- [done] Add OpenAPI examples and docs for report/export responses.
- [must-have] Complete report/export release review.
- [must-have] Prepare v0.6.0 release.

## Split-Needed Items

These items are intentionally too large and should be split before implementation.

### Authentication/API Keys

- Strategy note.
- API-key schema/design.
- Implementation.
- Tests.
- Docs.

### AI Incident Summaries

- Privacy/threat model.
- Summary input contract.
- Non-AI export/summary baseline.
- Provider integration.
- Tests/docs.

### Incident Workflow Metadata

- Schema design.
- Migration.
- API contract.
- Docs/examples.

### Frontend Dashboard

- UX sketch.
- API readiness.
- Frontend scaffold.
- Incident list screen.
- Incident detail screen.

## Later Ideas

- AI summaries.
- Slack, Jira, Zendesk, or PagerDuty integrations.
- Frontend dashboard.
- Hosted/cloud deployment options.
- Multi-user/RBAC.
- Notifications.
- Export/report generation.
- Release automation.

## Notes for Creating GitHub Issues

- Keep each issue small and testable.
- Link issues back to `ROADMAP.md` or this backlog.
- Include acceptance criteria.
- Include docs/test expectations.
- Do not combine unrelated feature tracks.
