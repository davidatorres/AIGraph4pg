#!/bin/bash

# Helper script to execute the psql command-line shell utility.
# It uses your environment variables to determine the host, user,
# and password per a given environment name arg.
#
# This script can be used to connect to a local PostgreSQL server,
# an Azure PostgreSQL Flex server, or an Azure Cosmos DB/PostgreSQL
# server (i.e. - Citus).
#
# Execute the following command in a bash terminal to see script usage:
# (venv) PS ...\python> ./pg.sh help
#
# .\pg.ps1 flex dev
# .\pg.ps1 flex dev libraries2.sql
#
# Chris Joakim, Microsoft

ENVNAME="$1"
DBNAME="$2"
INFILE="$3"
DBSERVER=""
DBPORT="5432"
DBUSER=""
DBPASS=""
SSL=""
VALID_ENV="0"

echo "ENVNAME:  $ENVNAME"
echo "DBNAME:   $DBNAME"
echo "INFILE:   $INFILE"

if [[ "$ENVNAME" == "local" ]]; then
    VALID_ENV="1"
    DBSERVER="localhost"
    DBUSER=$USER
    DBPASS="$LOCAL_PG_PASS"

elif [[ "$ENVNAME" == "flex" ]]; then
    VALID_ENV="1"
    DBSERVER="$AIG4PG_PG_FLEX_SERVER"
    DBUSER="$AIG4PG_PG_FLEX_USER"
    DBPASS="$AIG4PG_PG_FLEX_PASS"
    sslmode="sslmode=require"

elif [[ "$ENVNAME" == "cosmos" ]]; then
    VALID_ENV="1"
    DBSERVER="$AZURE_COSMOSDB_PG_SERVER"
    DBUSER="$AZURE_COSMOSDB_PG_USER"
    DBPASS="$AZURE_COSMOSDB_PG_PASS"
    sslmode="sslmode=require"

else
    echo "unknown env_name $env_name, terminating"
    echo ""
    echo "Usage:"
    echo "./psql.sh <env> <db> where <env> is local, flex, or cosmos"
    echo "./psql.sh local dev"
    echo "./psql.sh local dev"
    echo "./psql.sh local <db> <your-batch-sql-filename>"
    echo "./psql.sh local dev sql\query_all_extensions.sql > tmp\query_all_extensions.txt"
    echo "./psql.sh flex dev"
    echo "./psql.sh flex aigraph <your-batch-sql-filename>"
    echo "./psql.sh cosmos citus"
    echo "./psql.sh cosmos citus <your-batch-sql-filename>"
    echo ""
    exit 0
fi

if [[ $VALID_ENV == "1" ]]; then
    echo "DBSERVER: $DBSERVER"
    echo "DBPORT:   $DBPORT"
    echo "DBNAME:   $DBNAME"
    echo "DBUSER:   $DBUSER"
    echo "DBPASS:   $DBPASS"
    echo "SSL:      $SSL"

    if [[ "$INFILE" ]]; then
        echo "Invoking psql in batch mode with infile: $INFILE"
        echo "$DBPASS" | pbcopy
        psql_args="--file=$INFILE --host=$DBSERVER --port=$DBPORT --dbname=$DBNAME --username=$DBUSER --password $SSL"
        echo $psql_args
        psql "$psql_args"
        echo "" | pbcopy
    else
        echo "Unvoking psql in interactive mode"
        echo "$DBPASS" | pbcopy
        psql_args="--host=$DBSERVER --port=$DBPORT --dbname=$DBNAME --username=$DBUSER --password $SSL"
        echo $psql_args
        psql $psql_args
        echo "" | pbcopy 
    fi
fi
