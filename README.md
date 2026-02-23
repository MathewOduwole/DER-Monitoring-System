# DER Monitoring System

A microservices application for monitoring and managing Distributed Energy Resources (DERs) in real-time. Built with Flask, Angular, Apache Kafka, and PostgreSQL.

## Architecture

The system is composed of five services orchestrated via Docker Compose:

```
CLIENT LAYER          Angular Web App  |  Data Simulation Script (Python)
                              |
                         HTTP / REST
                              |
API LAYER              Flask API Service
                       - DER Management (CRUD)
                       - Telemetry Event Publishing
                       - Chart Management
                       - Time-series Data Query
                      /                \
               Publish Events      Read/Write
                    /                    \
MESSAGE QUEUE      Apache Kafka      DATA LAYER     PostgreSQL
(der-telemetry)        |             - DER Table
                  Consume Events     - Telemetry Table
                       |             - Chart Configs
PROCESSING LAYER  Telemetry Consumer -----> Write Telemetry Data
                  - Event Processing
                  - Data Validation
```

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Backend API | Python / Flask |
| Frontend | Angular 21 + Angular Material |
| Database | PostgreSQL 16 |
| Message Queue | Apache Kafka |
| Containerisation | Docker |
| Orchestration | Kubernetes (Minikube) |
| Package Manager | Helm |
| CI/CD | GitHub Actions |
| Charts | Chart.js / ng2-charts |

## Quick Start

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and Docker Compose
- Python 3.13+ (for the simulation script)

### Start All Services

```bash
git clone https://github.com/MathewOduwole/DER-Monitoring-System.git
cd DER-Monitoring-System

docker compose up -d
```

This starts PostgreSQL, Kafka, Zookeeper, the Flask API, the telemetry consumer, and the Angular frontend.

| Service | URL |
|---------|-----|
| Web Dashboard | http://localhost:4200 |
| API | http://localhost:5001 |
| API Health Check | http://localhost:5001/health |

### Run the Data Simulator

```bash
python -m venv .venv
source .venv/bin/activate
pip install requests

# Register 3 DERs and stream telemetry every 5 seconds
python scripts/simulate_der_data.py --ders 3 --interval 5

# Backfill 24 hours of historical data first
python scripts/simulate_der_data.py --ders 3 --interval 5 --backfill-hours 24
```

### Stop All Services

```bash
docker compose down
```

## API Endpoints

### DER Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/ders` | List all registered DERs |
| `POST` | `/api/ders` | Register a new DER |
| `PUT` | `/api/ders/{der_name}` | Update a DER |
| `DELETE` | `/api/ders/{der_name}` | Delete a DER and its telemetry |
| `GET` | `/api/ders/{der_name}/data` | Get time-series data (max 14 days) |

### Telemetry

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/telemetry` | Submit a telemetry event (publishes to Kafka) |

### Chart Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/charts` | List all saved charts |
| `POST` | `/api/charts` | Create a chart (max 3 DERs, 14-day window) |
| `GET` | `/api/charts/{chart_id}` | Get chart with telemetry data |
| `PUT` | `/api/charts/{chart_id}` | Update a chart |
| `DELETE` | `/api/charts/{chart_id}` | Delete a chart |

### Example Requests

**Register a DER:**
```bash
curl -X POST http://localhost:5001/api/ders \
  -H "Content-Type: application/json" \
  -d '{"name": "Solar-Panel-01", "mrid_id": "SP-001", "location": "Rooftop A", "type": "solar"}'
```

**Submit Telemetry:**
```bash
curl -X POST http://localhost:5001/api/telemetry \
  -H "Content-Type: application/json" \
  -d '{"der_name": "Solar-Panel-01", "active_power": 245.5, "reactive_power": 12.3, "voltage": 240.1, "timestamp": "2026-02-20T12:00:00Z"}'
```

**Create a Chart:**
```bash
curl -X POST http://localhost:5001/api/charts \
  -H "Content-Type: application/json" \
  -d '{"name": "Solar Output", "der_names": ["Solar-Panel-01"], "start_date": "2026-02-19T00:00:00Z", "end_date": "2026-02-20T00:00:00Z"}'
```

## Testing

```bash
# API tests (31 tests)
cd services/api
pip install -r requirements.txt
FLASK_ENV=testing python -m pytest tests/ -v

# Telemetry processor tests (8 tests)
cd services/telemetry
pip install -r requirements.txt pytest
python -m pytest tests/ -v
```

## Kubernetes Deployment (Minikube)

```bash
# Start Minikube
minikube start

# Build images inside Minikube's Docker
eval $(minikube docker-env)
docker compose build

# Deploy with Helm
helm install der-monitor ./helm/der-monitoring

# Access the web app
minikube service web --url
```

## Project Structure

```
DER-Monitoring-System/
├── services/
│   ├── api/              # Flask REST API
│   │   ├── app/
│   │   │   ├── models/   # SQLAlchemy models
│   │   │   ├── routes/   # API endpoints
│   │   │   ├── services/ # Business logic
│   │   │   ├── schemas/  # Request validation
│   │   │   └── kafka/    # Kafka producer
│   │   └── tests/        # pytest test suite
│   └── telemetry/        # Kafka consumer service
│       ├── app/
│       │   ├── consumer.py
│       │   └── processor.py
│       └── tests/
├── web/                  # Angular frontend
├── scripts/              # Data simulation
├── database/             # SQL schema
├── helm/                 # Kubernetes Helm charts
├── .github/workflows/    # CI/CD pipeline
└── docker-compose.yml
```

## Design Decisions

- **PostgreSQL over a time-series DB**: I chose to keep telemetry in PostgreSQL rather than introducing TimescaleDB or InfluxDB to keep the stack simpler. The composite index on `(der_id, timestamp DESC)` makes 14-day window queries efficient for this scale.

- **Kafka for event decoupling**: Telemetry goes through Kafka rather than being written directly to the database. This keeps the API responsive and allows the processing pipeline to scale independently.

- **Separate telemetry consumer**: Running the Kafka consumer as its own service means it can be scaled horizontally and doesn't compete with HTTP request handling for resources.

- **JSONB for chart DER references**: Using a JSONB array for `der_names` avoids a join table, keeping the schema lean. The max-3 constraint is enforced at both the database (CHECK) and application (Marshmallow) levels.

- **Flask app factory pattern**: Allows the application to be instantiated with different configurations, which is essential for running tests against an isolated SQLite database.

- **SQLite for tests**: Tests use SQLite so they run fast with zero infrastructure dependencies, while production uses PostgreSQL.
