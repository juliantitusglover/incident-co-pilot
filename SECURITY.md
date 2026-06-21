# Security Policy

Incident Co-Pilot 0.1.x is a lightweight, local/self-hosted incident timeline API. This policy describes how to report security issues and the current security expectations for this early version.

## Supported Versions

Security fixes are considered for:

- `main`
- `0.1.x`

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

## Secret Handling

Never commit `.env` files or real API keys.

If a secret is exposed, rotate it immediately and remove it from any public locations where it appeared.
