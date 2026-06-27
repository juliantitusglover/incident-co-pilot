# Backlog

This backlog collects candidate issues for future work. It is a planning aid, not a commitment. GitHub issues can be created from this document when ready.

## Priority Legend

- `must-have`: needed for the next target release.
- `should-have`: valuable but not release-blocking.
- `could-have`: useful if capacity allows.
- `later`: intentionally deferred.

## v0.2.0 Candidate Backlog

These items are candidates for planning around v0.2.0. They are not guaranteed release contents.

### API Usability

- [must-have] Decide and document incident list pagination strategy.
- [must-have] Implement incident list pagination.
- [must-have] Document incident list sort order.
- [should-have] Review status/severity filter naming and OpenAPI examples.
- [should-have] Add README examples for filtered incident lists.

### Timeline Event Usability

- [must-have] Decide whether timeline events need read/list endpoints.
- [should-have] If approved, add list timeline events endpoint.
- [should-have] If approved, add get timeline event endpoint.
- [should-have] Add API docs/examples for timeline event reads.
- [could-have] Document timeline event ordering expectations.

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

### Security Posture Planning

- [should-have] Write an API access/security strategy note.
- [should-have] Decide between local-only guidance, reverse-proxy auth guidance, or future API-key auth.
- [later] Implement API-key auth only after strategy is approved.

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
