# AIGraph4pg - PostgreSQL Local Windows 11 Setup

This process is intended to help you setup and run PostgreSQL
on your local Windows computer/laptop in order to explore core
PostgreSQL.

However, vector search, pg_bouncer, and Apache AGE functionality
is not intended to be executed locally for this AIGraph4pg project.
Use Azure PostgreSQL Flex Server for this functionality.

## Installation Steps

- Uninstall current PostgreSQL, if any
- Ensure the installation and data directories don't exist
  - C:\Program Files\PostgreSQL
  - C:\Program Files\PostgreSQL\16\data
- Empty the Recycle Bin 
- Reboot
- Download the Installer program
  - See https://www.postgresql.org/download/windows/
  - Download page https://www.enterprisedb.com/downloads/postgres-postgresql-downloads
  - Download file postgresql-16.4-2-windows-x64.exe
- Install PostgreSQL with the Installer
  - be sure to set a password for user 'postgres' in the installation dialog
- Reboot, the PostgreSQL service should be running
- Execute the following DIR command to see the installed command-line tools
  - note that these include psql, pg_dump, and pg_restore
```
dir 'C:\Program Files\PostgreSQL\16\bin' | grep pg
```

- In PowerShell, execute the following to display the current user (i.e. - chjoakim):
```
> $Env:UserName
chjoakim
```

- Also in PowerShell, execute the following to login as postgres (i.e. - superuser)
```
> psql --username postgres

Then respond to the prompt and enter the password you set above
```

- In the psql shell created above, create a user, and databases owned by the user
  - for the user id, use the value returned by $Env:UserName above
```
postgres=# create role chjoakim with createdb login password '<secret>';
CREATE ROLE

postgres=# create database dev owner chjoakim;
CREATE DATABASE

postgres=# create database aigraph owner chjoakim;
CREATE DATABASE

postgres=# exit
```

- Also in PowerShell, execute the following script to test connectivity
to the two databases created above

```
> .\psql.ps1 local dev
interactive psql - connecting to host: localhost, db: dev, user: chjoakim
psql (16.4)
WARNING: Console code page (437) differs from Windows code page (1252)
         8-bit characters might not work correctly. See psql reference
         page "Notes for Windows users" for details.
Type "help" for help.

dev=>

dev=> exit
```

```
> .\psql.ps1 local aigraph
interactive psql - connecting to host: localhost, db: aigraph, user: chjoakim
psql (16.4)
WARNING: Console code page (437) differs from Windows code page (1252)
         8-bit characters might not work correctly. See psql reference
         page "Notes for Windows users" for details.
Type "help" for help.

aigraph=>

aigraph=> exit
```