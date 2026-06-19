# Privacy Notes

Incident Co-Pilot v1 is a local/self-hosted incident timeline API. These notes describe what the current app stores and the privacy responsibilities of running it.

This is not a legal privacy policy.

## What Data the App Stores

The current v1 app stores:

- Incident title.
- Incident description.
- Severity.
- Status.
- Timeline event type.
- Timeline event message.
- Timestamps.
- Internal numeric IDs.

Free-text fields such as incident titles, incident descriptions, event types, and event messages may contain secrets, customer data, operational details, or personal data if users enter that data.

## Where Data Is Stored

Data is stored in the configured PostgreSQL database.

When using Docker Compose, PostgreSQL data is stored in the `postgres_data` volume unless that configuration is changed.

## Hosted Service

This repository does not provide a hosted Incident Co-Pilot service.

Maintainers do not receive data from self-hosted instances.

## AI and External Providers

Current v1 app code does not implement sending incident data to AI services or other external providers.

`OPENAI_API_KEY` configuration and `langchain` / `langchain-openai` dependencies exist for future optional AI work. Future AI features should document what data is sent to external providers and should require explicit configuration.

## Logs and Operational Data

Logs may contain operational errors and request metadata.

Avoid putting secrets in incident text, logs, environment files, shell history, screenshots, or bug reports.

## User Responsibility

Users should only store data approved for their local or self-hosted environment.

Users are responsible for securing PostgreSQL, backups, Docker volumes, host access, network access, and application access controls.
