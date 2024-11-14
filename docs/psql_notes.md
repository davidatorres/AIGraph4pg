# AIGraph4pg - psql command-line client notes

These are my notes on using the psql client program; they may be useful to you.

[See the PostgreSQL psql docs](https://www.postgresql.org/docs/current/app-psql.html)

## The psql client program, usage notes

### Invoking psql

See the **psql.ps1** and **psql.sh** scripts in the python/ directory of this repo.

```
.\psql.ps1 flex postgres   # Windows PowerShell
.\psql.ps1 flex dev        # Windows PowerShell

- or -

./psql.sh flex postgres    # linux and macOS bash
./psql.sh flex dev         # linux and macOS bash
```

In the above examples, flex is the environment name,
and postgres/dev are the databases to connect to.
**The environment name can be either local, flex, or cosmos**.
The flex environment is intended to connect to your Azure PostgreSQL Flex server.

The above scripts work with the following environment variables
to connect to the given environment name:

```
local:
  LOCAL_PG_PASS

flex:
  AIG4PG_PG_FLEX_SERVER
  AIG4PG_PG_FLEX_USER
  AIG4PG_PG_FLEX_PASS

cosmos:
  AZURE_COSMOSDB_PG_SERVER_FULL_NAME
  AZURE_COSMOSDB_PG_ADMIN_ID
  AZURE_COSMOSDB_PG_ADMIN_PW
```

### Commands once in the interactive psql shell

```
postgres=> \conninfo
You are connected to database "postgres" as user "chjoakim" on host "xxx.postgres.database.azure.com" ...

postgres=> create role <user> with createdb login password '<secret>';
postgres=> alter user <user>  with password '<new-password>';

postgres=> create database <database-name> owner <user>;
postgres=> create database dev owner chjoakim;
postgres=> create database aigraph owner chjoakim;

postgres=> destroydb <database-name>;

\connect dev

dev=> CREATE EXTENSION IF NOT EXISTS vector CASCADE;

dev=> SELECT * FROM pg_extension;
dev=> SELECT * FROM pg_available_extensions;
dev=> SELECT * FROM pg_settings;

dev=> SELECT column_name, data_type, character_maximum_length FROM information_schema.columns WHERE table_name = 'libraries';

dev=> insert into customers (customer_id, customer_name, phone, birth_date, balance) values (5, 'sam', '867-5309', '1988-01-01', 0.0);

dev=> explain analyze select ... your query...;

dev=> select * FROM information_schema.columns WHERE table_schema = '<schema-name>'
dev=> select * FROM information_schema.columns WHERE table_schema = '<schema-name>' AND table_name = '<table-name>';
```

---

### pgvector Examples

#### Delete define a table with JSONB and vector columns

```
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
```

#### Create a ivfflat vector index

```
SET ivfflat.probes = 5;
CREATE INDEX idx_libraries_ivfflat_embedding
ON     libraries
USING  ivfflat (embedding vector_cosine_ops)
WITH  (lists = 50);
```

#### Vector Search

```
select id, name, keywords
from  libraries
order by embedding <-> '{}'
limit 10;
```

---

### Apache AGE Commands

```
dev=> CREATE EXTENSION IF NOT EXISTS age CASCADE;

dev=> select * from pg_available_extensions;

dev=> show azure.extensions;
 azure.extensions
------------------
 VECTOR,AGE
(1 row)

SET search_path = ag_catalog, "$user", public;
show search_path;

dev=> SELECT ag_catalog.create_graph('graph1');
dev=> SELECT ag_catalog.create_graph('libraries2');

dev=> SELECT * FROM ag_catalog.drop_graph('graph_name', true);   # true/false to cascade

dev=> SELECT * FROM ag_catalog.ag_graph;
 graphid |  name  | namespace
---------+--------+-----------
   46938 | graph1 | graph1
(1 row)

dev=> SELECT * FROM cypher('graph1', $$ CREATE (kb:Actor {name: 'Kevin Bacon'}) $$) as (e agtype);
dev=> SELECT * FROM cypher('graph1', $$ CREATE (kb:GBB {name: 'Chris Joakim'}) $$) as (v agtype);
```

---

### Common Commands

```
command            description
-----------------  ----------------------------------------------
\q                 quit the client program
\l                 list databases
\c dbname          use the given database
\connect dbname    use the given database
\conninfo          display connection info; server, ip, port, db
\copy              see example below
\d                 list tables, or "List of relations"
\d                 show tables
\d customers       describe the customers table
\d+ customers      describe the customers table with details
\det               list foreign tables
\df                list functions
\df *load*         list functions with wildcard
\dn                list schemas
\di                list indexes
\di *lib*          list indexes with wildcard
\dt                show all the tables in db
\dt *.*            show all the tables in system & db
\dT                list of data types
\di                list indexes
\di *libraries*    list indexes with wildcard
\du                list roles
\dv                list views
\dx                list extensions
\?                 show the list of \postgres commands
\h                 show the list of SQL commands (i.e. - help)
\h command         show syntax on this SQL command (i.e. - help)
\pset pager 0      Turn output pagination off
\pset pager 1      Turn output pagination on
\set               list the settings
\set HISTSIZE 600  change a setting value
\timing on|off     Toggle the display of execution ms
\x on              Turn on mysql-like \G output
\x off             Turn off mysql-like \G output
```

See https://quickref.me/postgres.html


```
    \COPY libraries2 FROM '/Users/chjoakim/github/AIGraph4pg/data/data/pypi/libraries.tsv' WITH (FORMAT CSV, DELIMITER E'\t');

cat .\load_libraries1.txt | grep rows | Measure-Object -line
178270
```