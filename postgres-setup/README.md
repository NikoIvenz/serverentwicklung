"# PostgreSQL Installation and Configuration Guide (Project: Auto)

## Table of Contents

- [1. Create Named Volumes](#1-create-named-volumes)
- [2. Initialize Named Volumes](#2-initialize-named-volumes)
- [3. Initial Startup Without TLS & Copy Certificates](#3-initial-startup-without-tls--copy-certificates)
- [4. Regular Startup With TLS & Create Database/Tables](#4-regular-startup-with-tls--create-databasetables)
- [5. PostgreSQL Extension for VS Code (DB Browser)](#5-postgresql-extension-for-vs-code-db-browser)
- [6. Useful Administration Commands](#6-useful-administration-commands)

---

## 1. Create Named Volumes

First, create the Docker _Named Volumes_ for:
- `pg_data`: database files and TLS certificates in the server data directory
- `pg_tablespace`: custom tablespace (`autospace`)
- `pg_init`: SQL scripts, CSV test data, as well as the TLS certificate and private key

```shell
docker volume create pg_data
docker volume create pg_tablespace
docker volume create pg_init
```

---

## 2. Initialize Named Volumes

Using a temporary container running with root privileges (`-u 0`), copy the SQL scripts, CSV files, and TLS certificates from the local `./init` directory into the `pg_init` volume, create the `/tablespace/auto` directory inside the `pg_tablespace` volume, and set the required Linux file permissions (`postgres:postgres` ownership and `chmod 400`):

```shell
# Run inside the directory containing compose.yml:
docker run -v pg_init:/init -v pg_tablespace:/tablespace -v ./init:/tmp/init:ro --rm -it -u 0 --entrypoint '' postgres:18 /bin/bash -c "cp -r /tmp/init/* /init && mkdir -p /tablespace/auto && chown -R postgres:postgres /init /tablespace && chmod 400 /init/*/sql/* /init/*/csv/* /init/tls/* && ls -lR /init"
```

---

## 3. Initial Startup Without TLS & Copy Certificates

Because the `/var/lib/postgresql` directory must be structured during the very first database initialization (`initdb`), PostgreSQL must not look for `server.crt` and `server.key` on its initial run.

1. In `compose.yml`, **temporarily comment out** the `command:` key (including the lines for `--ssl=on`) using `#`.
2. Start the container in the background so the database directory gets initialized:
   ```shell
   docker compose up -d
   ```
3. Copy `server.crt` and `server.key` from `/init/tls` into the PostgreSQL 18 data directory (`/var/lib/postgresql/18/docker`) and restrict read permissions (`400`) to the `postgres` user:
   ```shell
   docker compose exec postgres bash -c "cd /var/lib/postgresql/18/docker && cp /init/tls/* . && chown postgres:postgres server.* && chmod 400 server.*"
   ```
4. Stop and remove the container:
   ```shell
   docker compose down
   ```
5. In `compose.yml`, **uncomment** the `command:` section (remove `#`) to enable TLS.

---

## 4. Regular Startup With TLS & Create Database/Tables

1. Start the PostgreSQL container with TLS enabled:
   ```shell
   docker compose up -d
   ```
2. Create the database `auto`, database user `auto`, tablespace `autospace`, and schema `auto`, and load the 3 tables (`auto`, `kennzeichen`, `wartung`) along with the CSV test data:
   ```shell
   docker compose exec postgres psql --dbname=postgres --username=postgres --file=/init/auto/sql/create-db.sql
   docker compose exec postgres psql --dbname=auto --username=auto --file=/init/auto/sql/create-schema.sql
   docker compose exec postgres psql --dbname=auto --username=postgres --file=/init/auto/sql/create-tables.sql
   ```

---

## 5. PostgreSQL Extension for VS Code (DB Browser)

### Configure Connection
1. Click the **PostgreSQL icon** in the VS Code sidebar and select **+ Add Connection** (_+ Verbindung hinzufügen_).
2. In the **Parameters** tab, enter the following values:
   - **SERVER NAME:** `localhost`
   - **USER NAME:** `postgres`
   - **PASSWORD:** `p` (check _Save Password_ / _Kennwort speichern_)
   - **DATABASE NAME:** `auto` (or `postgres`)
3. Click **Advanced** (_Erweitert_), expand the **SSL** menu, and configure:
   - **SSL MODE:** `require`
   - **SSL CERTIFICATE FILENAME:** select `init/tls/server.crt`
   - **SSL KEY FILENAME:** select `init/tls/server.key`
4. Close the _Advanced_ dialog (`X`), click **Test Connection** (_Verbindung testen_), and save via **Save & Connect**.

### Visualize Database Schema
Right-click the `auto` database in the connection tree and select **Visualize Schema** (_Schema visualisieren_) to graphically inspect the 1:1 relationship (`auto` <-> `kennzeichen`) and 1:N relationship (`auto` <-> `wartung`).

---

## 6. Useful Administration Commands

Verify that the server is running with TLS enabled and inspect the created tables and records:

```shell
docker compose exec postgres psql --dbname=auto --username=auto -c "SHOW ssl;"
docker compose exec postgres psql --dbname=auto --username=auto -c "\dt"
docker compose exec postgres psql --dbname=auto --username=auto -c "SELECT * FROM auto;"
```
"
