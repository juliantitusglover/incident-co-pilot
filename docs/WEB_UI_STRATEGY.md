# Minimal Web UI Strategy

## Status

- M12-PR2 scaffold is implemented.
- Target release: v0.7.0.
- v0.6.0 Incident Reports & Timeline Export is complete.
- `frontend/` now contains a minimal Vite React TypeScript scaffold.
- The scaffold has `dev`, `typecheck`, `build`, and `preview` scripts.
- No product screens or API calls exist yet.
- Docker Compose frontend integration and frontend CI remain deferred.
- M12-PR3 incident list/create remains next.

## Goal

- Add a small browser UI for existing backend capabilities.
- Make Incident Co-Pilot usable without curl/OpenAPI.
- Keep the first UI local/self-hosted and minimal.

## Non-Goals

- Users/RBAC/OAuth/JWT login.
- AI summaries.
- Slack/Jira/Zendesk integrations.
- Realtime updates or WebSockets.
- Complex design system or component library.
- Charts or analytics.
- Frontend Docker Compose integration unless later justified.
- Deployment platform, Kubernetes, or cloud hosting work.
- Backend schema changes unless a concrete UI blocker appears.
- New backend features beyond existing API calls.

## Recommended Stack

- Vite.
- React.
- TypeScript.
- Small hand-written API client.
- No component library initially.
- No Tailwind initially unless a later PR explicitly chooses it.
- No generated API client initially.

## Existing API Contracts The UI Will Call

- `GET /api/v1/incidents`
- `POST /api/v1/incidents`
- `GET /api/v1/incidents/{incident_id}`
- `GET /api/v1/incidents/{incident_id}/events`
- `POST /api/v1/incidents/{incident_id}/events`
- `GET /api/v1/incidents/{incident_id}/report`
- `GET /api/v1/incidents/{incident_id}/report/markdown`

Incident and timeline event lists return paginated envelopes with `items`, `limit`, `offset`, and `total`.

Report JSON returns `incident`, `timeline_events`, `timeline_order`, and `timeline_event_count`.

Markdown reports return `text/markdown`.

When API authentication is enabled, protected API calls use the `X-API-Key` header.

## Minimal UX Scope

- Incident list.
- Create incident form.
- Incident detail view.
- Timeline event list.
- Add timeline event form.
- Report panel for JSON and Markdown.
- Copy Markdown.
- Download Markdown if simple.
- Loading states.
- Empty states.
- Error states.
- `401`/auth hint.

## Frontend Configuration

- Use `VITE_API_BASE_URL`, defaulting to `http://localhost:8000` for local development.
- Let users enter an optional API key in browser UI/settings and store it locally, likely in `localStorage`.
- Do not commit real API keys.
- Avoid `VITE_API_KEY` except possibly as local-dev-only documentation later.
- The existing `CORS_ORIGINS=http://localhost:5173` examples fit Vite local development.

## Testing And Validation Strategy

- Run `npm run typecheck`.
- Run `npm run build`.
- Add unit tests later if the scaffold shape makes them useful.
- Add a manual browser smoke checklist.
- Keep backend tests green.
- Add frontend CI after scaffold scripts exist.

## Docker And Deployment Strategy

- Local dev first: backend and frontend can run in separate terminals.
- Defer a Docker Compose frontend service until needed.
- Do not introduce production hosting assumptions in M12.

## M12 PR Sequence

- M12-PR1 - Minimal Web UI strategy.
- M12-PR2 - Vite React TypeScript scaffold. Complete.
- M12-PR3 - Incident list and create incident.
- M12-PR4 - Incident detail and timeline event list/create.
- M12-PR5 - Report JSON/Markdown panel.
- M12-PR6 - Frontend docs, release checklist, and manual browser smoke review.
- M12-PR7 - Prepare v0.7.0 release.

## Risks

- Frontend scope creep.
- API key handling without real user accounts.
- CORS/API base URL drift.
- Docker/CI expansion too early.
- Manually duplicating backend contracts in frontend types.
- Designing beyond the first usable local UI.
