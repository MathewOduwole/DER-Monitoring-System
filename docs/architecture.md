# Architecture Decisions

## Overview

I designed this system as a set of loosely coupled microservices, each with a single responsibility. The goal was to build something that feels production-ready while staying within the scope of the assignment.

## Service Separation

### Why a separate telemetry consumer?

The API service handles HTTP requests and should respond quickly. If it had to validate telemetry data and write it to the database synchronously, response times would increase under load. By publishing to Kafka and having a dedicated consumer process the events, the API can return a `202 Accepted` immediately.

This also means the consumer can be scaled independently. If telemetry volume grows, I can increase consumer replicas without affecting the API's ability to serve dashboard queries.

### Why not a shared ORM between API and consumer?

The API uses Flask-SQLAlchemy because it integrates naturally with Flask's request lifecycle. The telemetry consumer is a standalone Python process with no HTTP server, so I used raw SQLAlchemy with explicit session management. This keeps each service lean — they only import what they need.

## Database Design

### PostgreSQL over specialised time-series databases

For the scope of this project, PostgreSQL handles the telemetry workload well. The composite index on `(der_id, timestamp DESC)` makes the capped 14-day queries fast. If this were a production system with millions of readings per day, I'd consider TimescaleDB (which is a PostgreSQL extension, so the migration path is smooth).

### CHECK constraints in the database

I enforce the business rules (max 3 DERs per chart, max 14-day range) at the database level as well as the application level. This is a defence-in-depth approach — even if a bug in the application code bypasses validation, the database won't accept invalid data.

### JSONB for chart DER references

A normalised approach would use a join table (`chart_ders` with `chart_id` and `der_name`). I chose JSONB because:
- The max is 3 items, so the array is always small
- It simplifies queries — no joins needed to get the full chart config
- PostgreSQL's JSONB operations can query into the array if needed

## Kafka

### Why Kafka over simpler alternatives?

The assignment specified Kafka, but it's also a good fit here. The `der-telemetry` topic decouples data ingestion from processing. Benefits:
- **Durability**: Messages persist until consumed, so data isn't lost if the consumer restarts
- **Ordering**: Messages are keyed by DER name, so readings from the same DER are processed in order
- **Extensibility**: Additional consumers (alerting, analytics) can subscribe to the same topic without changing the API

### confluent-kafka over kafka-python

I chose the Confluent client because it wraps `librdkafka` (C library), which gives significantly better throughput and lower latency than the pure-Python `kafka-python` library. It's the recommended client for production use.

## Frontend

### Angular with standalone components

I used Angular's standalone component architecture (no NgModules) with lazy-loaded routes. This keeps the initial bundle size down and each component self-contained.

### Chart.js for visualisation

Chart.js with ng2-charts provides a good balance of functionality and simplicity. The line charts support multiple datasets (one per DER), which maps directly to the requirement of comparing up to 3 DERs on a single chart.

## Testing Strategy

### SQLite for test isolation

Tests use SQLite rather than requiring a running PostgreSQL instance. This means:
- Tests run in ~0.2 seconds
- No Docker dependency for running the test suite
- CI pipeline doesn't need a database service

The trade-off is that some PostgreSQL-specific features (JSONB CHECK constraints) aren't tested at the database level. These are covered by Marshmallow schema validation in the application layer, which is tested.

## Deployment

### Docker Compose for local development

All services start with a single `docker compose up -d`. Health checks with dependency conditions ensure PostgreSQL and Kafka are ready before the API and consumer start, avoiding startup race conditions.

### Helm for Kubernetes

The Helm chart is structured to deploy the same services to a Kubernetes cluster (Minikube for demo). Each service is a separate Deployment with appropriate resource limits, readiness probes, and service discovery via Kubernetes DNS.
