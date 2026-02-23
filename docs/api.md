# API Documentation

Base URL: `http://localhost:5001`

## Health Check

### `GET /health`

Returns the health status of the API and its database connection.

**Response:**
```json
{
  "status": "healthy",
  "database": "healthy"
}
```

---

## DER Management

### `POST /api/ders` - Register a DER

**Request Body:**
```json
{
  "name": "Solar-Panel-01",
  "mrid_id": "SP-001",
  "location": "Building A Rooftop",
  "type": "solar"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| name | string | Yes | Unique name for the DER |
| mrid_id | string | Yes | Master Resource Identifier |
| location | string | No | Physical location |
| type | string | Yes | DER type (solar, wind, battery, generator) |

**Response (201):**
```json
{
  "id": 1,
  "name": "Solar-Panel-01",
  "mrid_id": "SP-001",
  "location": "Building A Rooftop",
  "type": "solar",
  "created_at": "2026-02-20T18:11:40.176654+00:00",
  "updated_at": "2026-02-20T18:11:40.176663+00:00"
}
```

**Error (409):** DER with that name already exists.

---

### `GET /api/ders` - List All DERs

**Response (200):** Array of DER objects.

---

### `PUT /api/ders/{der_name}` - Update a DER

**Request Body:** Any subset of `mrid_id`, `location`, `type`.

**Response (200):** Updated DER object.
**Error (404):** DER not found.

---

### `DELETE /api/ders/{der_name}` - Delete a DER

Deletes the DER and all associated telemetry data (CASCADE).

**Response (200):**
```json
{ "message": "DER 'Solar-Panel-01' deleted." }
```

---

### `GET /api/ders/{der_name}/data` - Get Time-Series Data

**Query Parameters:**

| Param | Type | Description |
|-------|------|-------------|
| start | ISO datetime | Start of range (default: 14 days ago) |
| end | ISO datetime | End of range (default: now) |

Maximum range is 14 days. If the requested range exceeds this, start is clamped.

**Response (200):** Array of telemetry readings.
```json
[
  {
    "id": 1,
    "der_id": 1,
    "active_power": 245.5,
    "reactive_power": 12.3,
    "voltage": 240.1,
    "timestamp": "2026-02-20T18:10:00+00:00"
  }
]
```

---

## Telemetry

### `POST /api/telemetry` - Submit Telemetry Event

Publishes a telemetry event to Kafka for asynchronous processing.

**Request Body:**
```json
{
  "der_name": "Solar-Panel-01",
  "active_power": 245.5,
  "reactive_power": 12.3,
  "voltage": 240.1,
  "timestamp": "2026-02-20T18:10:00+00:00"
}
```

**Response (202):**
```json
{ "message": "Telemetry event published." }
```

The event is published to the `der-telemetry` Kafka topic. The telemetry consumer service picks it up, validates it, and writes it to the database.

**Validation ranges:**
- Active Power: -10,000 to 10,000 W
- Reactive Power: -10,000 to 10,000 var
- Voltage: 0 to 500 V

---

## Chart Management

### `POST /api/charts` - Create a Chart

**Request Body:**
```json
{
  "name": "Solar Output This Week",
  "der_names": ["Solar-Panel-01", "Solar-Panel-02"],
  "start_date": "2026-02-13T00:00:00Z",
  "end_date": "2026-02-20T00:00:00Z"
}
```

**Constraints:**
- Maximum 3 DERs per chart
- Date range must not exceed 14 days
- All referenced DERs must exist

**Response (201):** Chart object.

---

### `GET /api/charts/{chart_id}` - Get Chart with Data

Returns the chart configuration along with telemetry series data for each DER.

**Response (200):**
```json
{
  "id": 1,
  "name": "Solar Output This Week",
  "der_names": ["Solar-Panel-01"],
  "start_date": "2026-02-13T00:00:00+00:00",
  "end_date": "2026-02-20T00:00:00+00:00",
  "series": {
    "Solar-Panel-01": [
      {
        "id": 1,
        "der_id": 1,
        "active_power": 245.5,
        "reactive_power": 12.3,
        "voltage": 240.1,
        "timestamp": "2026-02-13T08:00:00+00:00"
      }
    ]
  }
}
```

---

### `PUT /api/charts/{chart_id}` - Update a Chart

**Request Body:** Any subset of `name`, `der_names`, `start_date`, `end_date`.

---

### `DELETE /api/charts/{chart_id}` - Delete a Chart

**Response (200):**
```json
{ "message": "Chart deleted." }
```
