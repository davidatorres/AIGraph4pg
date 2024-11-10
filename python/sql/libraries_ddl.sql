DROP TABLE IF EXISTS libraries CASCADE;

CREATE TABLE libraries (
    id                   bigserial primary key,
    name                 VARCHAR(255),
    libtype              VARCHAR(10),
    description          TEXT,
    keywords             TEXT,
    license              TEXT,
    release_count        INTEGER,
    package_url          VARCHAR(255),
    project_url          VARCHAR(255),
    docs_url             VARCHAR(255),
    release_url          VARCHAR(255),
    requires_python      VARCHAR(255),
    classifiers          JSONB,
    project_urls         JSONB,
    developers           JSONB,
    embedding            vector(1536)
);