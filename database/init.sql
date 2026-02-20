-- DER Monitoring System - Database Schema
-- I'm using PostgreSQL for its strong support for JSONB, time-zone-aware timestamps,
-- and CHECK constraints, all of which are central to this project's requirements.
-- This script runs on first container start via the Docker entrypoint.

CREATE TABLE IF NOT EXISTS ders (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    mrid_id VARCHAR(255) NOT NULL,
    location VARCHAR(255),
    type VARCHAR(100) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- I chose to keep telemetry in the same database rather than a dedicated time-series DB
-- to keep the stack simpler for this scope. The composite index on (der_id, timestamp DESC)
-- ensures efficient querying for the 14-day windows the API supports.
CREATE TABLE IF NOT EXISTS telemetry_data (
    id SERIAL PRIMARY KEY,
    der_id INTEGER NOT NULL REFERENCES ders(id) ON DELETE CASCADE,
    active_power DOUBLE PRECISION NOT NULL,
    reactive_power DOUBLE PRECISION NOT NULL,
    voltage DOUBLE PRECISION NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- I'm enforcing the business rules (max 3 DERs per chart, max 14-day range) at the database
-- level with CHECK constraints so the invariants hold regardless of which service writes.
CREATE TABLE IF NOT EXISTS charts (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    der_names JSONB NOT NULL DEFAULT '[]',
    start_date TIMESTAMP WITH TIME ZONE NOT NULL,
    end_date TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT max_three_ders CHECK (jsonb_array_length(der_names) <= 3),
    CONSTRAINT max_fourteen_days CHECK (end_date - start_date <= INTERVAL '14 days')
);

CREATE INDEX IF NOT EXISTS idx_telemetry_der_id ON telemetry_data(der_id);
CREATE INDEX IF NOT EXISTS idx_telemetry_timestamp ON telemetry_data(timestamp);
CREATE INDEX IF NOT EXISTS idx_telemetry_der_timestamp ON telemetry_data(der_id, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_ders_name ON ders(name);
