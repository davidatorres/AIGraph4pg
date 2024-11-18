

CREATE TABLE IF NOT EXISTS volumes(
	id text primary key unique,
	volume_number int,
	reporter_slug text,
	data jsonb
);


CREATE TABLE IF NOT EXISTS cases_metadata(
	id text primary key unique,
	data jsonb
);

CREATE TABLE IF NOT EXISTS cases(
	id text primary key unique,
	data jsonb
);

