# Auto REST API

REST API for vehicles (`Auto`) built with FastAPI, SQLAlchemy 2, Pydantic and PostgreSQL (TLS).
Each vehicle has a 1:1 license plate (`Kennzeichen`) and 1:N maintenance records (`Wartung`).

## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Getting Started](#getting-started)
- [REST Interface](#rest-interface)
- [Configuration](#configuration)
- [Tests and Code Quality](#tests-and-code-quality)
- [Demonstration](#demonstration)

## Features

- CRUD for vehicles including license plate and maintenance records
- Search by brand (case-insensitive substring) and FIN (exact) with pagination
- Optimistic locking via `ETag` / `If-Match` and conditional reads via `If-None-Match`
- Errors as Problem Details (RFC 7807, `application/problem+json`)
- HTTPS with HTTP/2 (Uvicorn), PostgreSQL connection with `sslmode=verify-full`
- Test data is reloaded from CSV files on startup (development only)

## Architecture

```text
src/auto/
├── asgi_server.py      # Uvicorn start with TLS
├── fastapi_app.py      # FastAPI app, lifespan, exception handlers
├── config/             # app.toml reader, database URL and TLS settings
├── entity/             # SQLAlchemy ORM entities (Auto, Kennzeichen, Wartung)
├── repository/         # Data access: AutoRepository, Slice/Pageable, db_populate
├── service/            # DTOs, domain exceptions, AutoService, AutoWriteService
├── router/             # REST endpoints, Pydantic models, dependencies, problem details
└── resources/          # app.toml, TLS certificate and key, CSV test data
```

Requests pass through `router` → `service` → `repository`. The service layer owns the
sessions and transactions and returns DTOs, so the ORM entities never leave it.

## Prerequisites

- Python 3.13 or newer
- [uv](https://docs.astral.sh/uv/)
- Docker (for PostgreSQL)

## Getting Started

1. Set up PostgreSQL once as described in [postgres-setup/README.md](postgres-setup/README.md),
   then start it:

   ```shell
   cd postgres-setup
   docker compose up -d
   ```

2. Install the dependencies and start the server from the project root:

   ```shell
   uv sync
   uv run auto            # alternatively: uv run python -m auto
   ```

3. Open the interactive API documentation: <https://127.0.0.1:8000/docs>
   (accept the certificate warning of the self-signed certificate).

Liveness probe: `GET /health/liveness`.

## REST Interface

| Method | Path             | Description                                   | Success                          |
| ------ | ---------------- | --------------------------------------------- | -------------------------------- |
| GET    | `/rest/{id}`     | Read a vehicle; honors `If-None-Match`        | 200 with `ETag`, 304             |
| GET    | `/rest`          | Search with `marke`, `fin`, `page`, `size`    | 200 with pagination metadata     |
| POST   | `/rest`          | Create a vehicle with plate and maintenance   | 201 with `Location: /rest/{id}`  |
| PUT    | `/rest/{id}`     | Update master data; requires `If-Match`       | 204 with new `ETag`              |
| DELETE | `/rest/{id}`     | Delete a vehicle including its relations      | 204                              |

Error mapping:

| Status | Cause                                                              |
| ------ | ------------------------------------------------------------------ |
| 404    | Vehicle not found                                                  |
| 412    | Outdated version, or `If-Match` is not a version number            |
| 422    | Invalid payload, or the FIN already exists                         |
| 428    | `If-Match` header missing on PUT                                   |

Example:

```shell
curl -k -X POST https://127.0.0.1:8000/rest \
  -H "Content-Type: application/json" \
  -d '{
        "fin": "WXYZ1234567890123",
        "marke": "TESLA",
        "modell": "Model 3",
        "farbe": "W",
        "kennzeichen": {"kombination": "KA-TS 123", "ausstellungsdatum": "2026-02-01"},
        "wartungen": [{"beschreibung": "Inspektion", "kosten": "99.90"}]
      }'
```

`farbe` is one of `S` (black), `W` (white), `SI` (silver), `R` (red), `B` (blue).
The FIN has 17 characters without `I`, `O` and `Q`.

## Configuration

Settings live in [src/auto/resources/app.toml](src/auto/resources/app.toml): server binding,
database credentials and `[dev] db-populate`.

> **Warning:** with `db-populate = true` all rows of `auto`, `kennzeichen` and `wartung` are
> deleted and reloaded from `src/auto/resources/csv/` on every server start. Set it to
> `false` for anything but local development.

## Tests and Code Quality

The integration tests need the running PostgreSQL container.

```shell
uv run pytest          # tests, report.html and htmlcov/
uv run ruff check
uv run ruff format
uv run pyright
```

## Demonstration

Both the server and the test run reset the database to the CSV data on startup, so restart
the server right before the demo to start from a clean state.

1. **Start the database**

   ```shell
   cd postgres-setup && docker compose up -d && cd ..
   ```

2. **Automated tests** (covers GET, POST, PUT with optimistic locking, DELETE)

   ```shell
   uv run pytest
   ```

   Expect `10 passed`. Open `report.html` (test report) and `htmlcov/index.html` (coverage).

3. **Live demo in Swagger UI**: start `uv run auto` and open <https://127.0.0.1:8000/docs>.
   - `GET /rest/30`: nested license plate and maintenance records, `ETag` response header.
   - `GET /rest?marke=bmw`: search hits with `total_elements` and `total_pages`.
   - `POST /rest` with the example payload above: `201 Created` and `Location: /rest/1000`.
     Sending it a second time, or with a too short FIN, returns `422`.
   - `PUT /rest/1000` with the `ETag` from a GET as `If-Match`: `204`. Repeating the same
     request returns `412` because the version is outdated; without the header it is `428`.

4. **Proof in the database**: in the VS Code PostgreSQL extension, open the table `auto`
   (*Select Top 1000*). The new vehicle has ID 1000 and version 1 (vehicles loaded from
   the CSV files have version 0). *Visualize Schema* shows the 1:1 and 1:N relations.

5. **Code quality**

   ```shell
   uv run ruff check
   uv run pyright
   ```

   Both report no errors.
