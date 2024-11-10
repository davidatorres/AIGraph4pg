DROP TABLE IF EXISTS mini CASCADE;

CREATE TABLE mini1 ( id bigserial primary key, embedding vector(1536) );

CREATE TABLE mini2 ( id bigserial primary key, name VARCHAR(255) );


aigraph=> CREATE TABLE mini ( id bigserial primary key, embedding vector(1536) );
ERROR:  permission denied for schema ag_catalog
LINE 1: CREATE TABLE mini ( id bigserial primary key, embedding vect...
         