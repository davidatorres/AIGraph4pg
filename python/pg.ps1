# Helper script to execute the psql command-line shell utility.
# It uses your environment variables to determine the host, user,
# and password per a given environment name arg.
#
# This script can be used to connect to a local PostgreSQL server,
# an Azure PostgreSQL Flex server, or an Azure Cosmos DB/PostgreSQL
# server (i.e. - Citus).
#
# Execute the following command in PowerShell to see script usage:
# (venv) PS ...\python> .\pg.ps1 help
#
# Chris Joakim, Microsoft

param(
    [Parameter()]
    [String]$env_name  = "",
    [String]$db_name   = "aigraph",
    [String]$psql_file = ""
)

$h=""
$p="5432"
$user="<user>"
$pass="<pass>"
$ssl=""
$win_user=$Env:UserName
$valid_env="false"

if ('local' -eq $env_name) {
    $valid_env="true"
    $h="localhost"
    $user=$win_user
    $pass=$Env:LOCAL_PG_PASS
}
elseif ('flex' -eq $env_name)
{
    $valid_env="true"
    $h=$Env:AIG4PG_PG_FLEX_SERVER
    $user=$Env:AIG4PG_PG_FLEX_USER
    $pass=$Env:AIG4PG_PG_FLEX_PASS
    $ssl="sslmode=require"
}
elseif ('cosmos' -eq $env_name)
{
    $valid_env="true"
    if ('citus' -ne $db_name) {
        Write-Output "WARNING: 'citus' is the only allowed database name for Azure Cosmos DB / PostgreSQL"
    }
    $h=$env:AZURE_COSMOSDB_PG_SERVER
    $user=$env:AZURE_COSMOSDB_PG_USER
    $pass=$env:AZURE_COSMOSDB_PG_PASS
    $ssl="sslmode=require"
}
else {
    Write-Output "unknown env_name $env_name, terminating"
    Write-Output ""
    Write-Output "Usage:"
    Write-Output ".\psql.ps1 <env> <db> where <env> is local, flex, or cosmos"
    Write-Output ".\psql.ps1 local dev"
    Write-Output ".\psql.ps1 local dev"
    Write-Output ".\psql.ps1 local <db> <your-batch-sql-filename>"
    Write-Output ".\psql.ps1 local dev sql\query_all_extensions.sql > tmp\query_all_extensions.txt"
    Write-Output ".\psql.ps1 flex dev sql\query_all_extensions.sql > tmp\query_all_extensions.txt"
    Write-Output ".\psql.ps1 flex dev libraries1.sql > tmp\load_libraries1.txt ; date"
    Write-Output ".\psql.ps1 flex"
    Write-Output ".\psql.ps1 flex aigraph sql\libraries_ddl.sql"
    Write-Output ".\psql.ps1 cosmos citus"
    Write-Output ".\psql.ps1 cosmos citus <your-batch-sql-filename>"
    Write-Output ""
    Exit
}

if ('true' -eq $valid_env) {
    if ("" -eq $psql_file) {
        Write-Output "interactive psql - connecting to host: $h, db: $db_name, user: $user"
        if ("nodb" -eq $db_name) {
            $psql_args="host=$h port=$p user=$user password=$pass $ssl"
        }
        else {
            $psql_args="host=$h port=$p dbname=$db_name user=$user password=$pass $ssl"
        }
        psql "$psql_args"
    }
    else {
        Write-Output "batch psql - connecting to host: $h, db: $db_name, user: $user, using file: $psql_file"
        $psql_args="host=$h port=$p dbname=$db_name user=$user password=$pass $ssl"
        psql -f $psql_file "$psql_args"
    }
}

# SET AUTOCOMMIT { = | TO } { ON | OFF }
# -b, --echo-errors        echo failed commands
# -e, --echo-queries       echo commands sent to server
# cat .\load_libraries1.txt | grep rows | Measure-Object -line

