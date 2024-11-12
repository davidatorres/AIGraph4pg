DROP TABLE IF EXISTS airports CASCADE;

CREATE TABLE airports (
    id                 bigserial primary key,
    name               VARCHAR(255),
    city               VARCHAR(60),
    country            VARCHAR(60),
    iata               VARCHAR(4),
    icao               VARCHAR(4),
    timezone           VARCHAR(60),
    timezone_offset    NUMERIC(3, 1),
    latitude           NUMERIC(19, 15),
    longitude          NUMERIC(19, 15),
    altitude           INTEGER,
    metadata           JSONB
);