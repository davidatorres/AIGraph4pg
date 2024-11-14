-- Delete/Define the libraries table.

DROP TABLE IF EXISTS libraries CASCADE;

CREATE TABLE libraries (
    id                   bigserial primary key,
    name                 VARCHAR(30),
    description          VARCHAR(1024),
    keywords             VARCHAR(255),
    license              VARCHAR(255),
    release_count        INTEGER,
    package_url          VARCHAR(100),
    project_url          VARCHAR(100),
    embedding            vector(1536),
    metadata             JSONB
);