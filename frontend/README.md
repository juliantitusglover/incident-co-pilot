# Incident Co-Pilot Frontend

Minimal Vite React TypeScript scaffold for the Incident Co-Pilot web UI.

## Prerequisites

- Node.js 20.19 or newer
- npm

## Setup

```bash
npm install
npm run dev
```

The local frontend dev server runs at http://localhost:5173.

The backend API is expected at http://localhost:8000 for local development.

## Validation

```bash
npm run typecheck
npm run build
npm run preview
```

This scaffold does not make API calls yet. Incident list, create, detail,
timeline, and report screens will be added in later M12 PRs.

Do not commit API keys or real secrets.
