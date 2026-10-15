SET search_path TO auto;
SET default_tablespace = autospace;

CREATE TYPE farbe AS ENUM ('SCHWARZ', 'WEISS', 'SILBER', 'ROT', 'BLAU');

CREATE TABLE IF NOT EXISTS auto (
    id            INTEGER GENERATED ALWAYS AS IDENTITY(START WITH 1000) PRIMARY KEY,
    version       INTEGER NOT NULL DEFAULT 0,
    fin           TEXT NOT NULL UNIQUE,
    marke         TEXT NOT NULL,
    modell        TEXT NOT NULL,
    farbe         farbe,
    erzeugt       TIMESTAMP NOT NULL,
    aktualisiert  TIMESTAMP NOT NULL
);

CREATE INDEX IF NOT EXISTS auto_marke_idx ON auto(marke);

CREATE TABLE IF NOT EXISTS kennzeichen (
    id                 INTEGER GENERATED ALWAYS AS IDENTITY(START WITH 1000) PRIMARY KEY,
    kombination        TEXT NOT NULL,
    ausstellungsdatum  DATE NOT NULL,
    auto_id            INTEGER NOT NULL UNIQUE REFERENCES auto ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS kennzeichen_auto_id_idx ON kennzeichen(auto_id);

CREATE TABLE IF NOT EXISTS wartung (
    id            INTEGER GENERATED ALWAYS AS IDENTITY(START WITH 1000) PRIMARY KEY,
    beschreibung  TEXT NOT NULL,
    kosten        NUMERIC(10,2) NOT NULL,
    auto_id       INTEGER NOT NULL REFERENCES auto ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS wartung_auto_id_idx ON wartung(auto_id);

ALTER TYPE farbe OWNER TO auto;
ALTER TABLE auto OWNER TO auto;
ALTER TABLE kennzeichen OWNER TO auto;
ALTER TABLE wartung OWNER TO auto;

COPY auto FROM '/init/auto/csv/auto.csv' (FORMAT csv, QUOTE '"', DELIMITER ';', HEADER true);
COPY kennzeichen FROM '/init/auto/csv/kennzeichen.csv' (FORMAT csv, QUOTE '"', DELIMITER ';', HEADER true);
COPY wartung FROM '/init/auto/csv/wartung.csv' (FORMAT csv, QUOTE '"', DELIMITER ';', HEADER true);
