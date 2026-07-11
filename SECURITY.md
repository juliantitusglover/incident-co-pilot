# Security Policy

Incident Co-Pilot 0.2.x is a lightweight, local/self-hosted incident timeline API. This policy describes how to report security issues and the current security expectations for this early version.

## Supported Versions

Security fixes are considered for:

- `main`
- `0.2.x`

There is no backport commitment yet for older versions or release branches.

## Reporting a Vulnerability

Do not open public GitHub issues for vulnerabilities.

Use GitHub private vulnerability reporting if it is enabled for this repository, or contact the maintainer privately.

When reporting a vulnerability, include:

- The affected version or commit.
- A clear description of the impact.
- Reproduction steps.
- A suggested fix, if known.

Do not include real secrets, tokens, customer incident data, production database URLs, or sensitive exploit details in public issues, pull requests, screenshots, logs, or discussions.

## Response Expectations

The maintainer will make a best-effort attempt to acknowledge vulnerability reports within 7 days.

This is not a formal SLA.

## Security Scope and Caveats

Incident Co-Pilot's current self-hosted version is not production-hardened.

Users are responsible for deployment security, including:

- Network exposure.
- Secret management.
- PostgreSQL access controls.
- Database backups.
- Host and container security.
- TLS and reverse proxy configuration if deployed beyond local development.
- Authentication and authorization controls around any exposed instance.

## API Key Authentication

Incident Co-Pilot includes optional shared API key authentication for the incident and timeline event API routes.

This is basic self-hosted access control. It is not user accounts, sessions, RBAC, OAuth, or JWT authentication.

If you enable API key authentication:

- Set `API_AUTH_ENABLED=true`.
- Set `API_KEY` to a long random secret.
- Send the key on protected API requests with the `X-API-Key` header.
- Keep `API_KEY` secret and never commit real `.env` values.

For deployments exposed beyond local development, still use TLS, reverse proxy controls, network restrictions, PostgreSQL hardening, host/container security, and backups.

Key rotation is manual for now: change `API_KEY` in the runtime environment and restart or redeploy the service.

## Secret Handling

Never commit `.env` files or real API keys.

If a secret is exposed, rotate it immediately and remove it from any public locations where it appeared.
