# AIGraph4pg - The Apache Age Extension

## Links

- [Apache Age Home Page](https://age.apache.org/)
- [Apache Age Quick Start](https://age.apache.org/getstarted/quickstart/)
- [Apache Age Manual](https://age.apache.org/age-manual/master/intro/overview.html)
- [Introducing support for Graph data in Azure Database for PostgreSQL](https://techcommunity.microsoft.com/t5/azure-database-for-postgresql/introducing-support-for-graph-data-in-azure-database-for/ba-p/4275628)
- [AGE types](https://age.apache.org/age-manual/master/intro/types.html)

### More Links

- [Cypher Query Language Reference,v9](https://s3.amazonaws.com/artifacts.opencypher.org/openCypher9.pdf)
- https://matheusfarias03.github.io/AGE-quick-guide/
- https://stackoverflow.com/questions/75178525/is-it-possible-to-create-a-graph-in-age-using-existing-table-in-the-database
- https://age.apache.org/age-manual/master/advanced/plpgsql.html
- https://age.apache.org/age-manual/master/advanced/sql_in_cypher.html

## Setup

```
dev=> CREATE EXTENSION IF NOT EXISTS age CASCADE;
CREATE EXTENSION

dev=> SELECT * FROM pg_extension;
  oid  | extname | extowner | extnamespace | extrelocatable | extversion |   extconfig   | extcondition
-------+---------+----------+--------------+----------------+------------+---------------+--------------
 14258 | plpgsql |       10 |           11 | f              | 1.0        |               |
 45797 | age     |       10 |        45796 | f              | 1.5.0      | {45798,45810} | {"",""}
(2 rows)

aigraph=> SELECT * FROM pg_extension;
  oid  | extname | extowner | extnamespace | extrelocatable | extversion |   extconfig   | extcondition
-------+---------+----------+--------------+----------------+------------+---------------+--------------
 14258 | plpgsql |       10 |           11 | f              | 1.0        |               |
 24759 | vector  |       10 |         2200 | t              | 0.7.0      |               |
 25080 | age     |       10 |        25079 | f              | 1.5.0      | {25081,25093} | {"",""}
(3 rows)
```
