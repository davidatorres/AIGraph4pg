# AIGraph4pg Implementation 1 : Environment Variables

Per the [Twelve-Factor App methodology](https://12factor.net/config),
configuration is stored in environment variables.  

## Defined Variables

This reference implementation uses the following environment variables.
| Name | Description |
| --------------------------------- | --------------------------------- |
| AIG4PG_ENCRYPTION_SYMMETRIC_KEY | optional symmetric key for encryption/decryption |
| AIG4PG_LOG_LEVEL | See values in class LoggingLevelService - notset, debug, info, warning, error, or critical |
| AIG4PG_OPENAI_COMPLETIONS_DEP | The name of your Azure OpenAI completions deployment |
| AIG4PG_OPENAI_EMBEDDINGS_DEP | The name of your Azure OpenAI embeddings deployment |
| AIG4PG_OPENAI_KEY | The Key of your Azure OpenAI account |
| AIG4PG_OPENAI_URL | The URL of your Azure OpenAI account |
| AIG4PG_PG_FLEX_DB | Azure PostgreSQL Flex Server database |
| AIG4PG_PG_FLEX_PASS | Azure PostgreSQL Flex Server user password |
| AIG4PG_PG_FLEX_PORT | Azure PostgreSQL Flex Server port |
| AIG4PG_PG_FLEX_SERVER | Azure PostgreSQL Flex Server hostname |
| AIG4PG_PG_FLEX_USER | Azure PostgreSQL Flex Server user |
| AIG4PG_TRUNCATE_LLM_CONTEXT_MAX_NTOKENS |  |
| AZURE_COSMOSDB_PG_PASS | Optional.  Used by the psql.ps1/psql.sh scripts for Cosmos DB PostgreSQL |
| AZURE_COSMOSDB_PG_SERVER | Optional.  Used by the psql.ps1/psql.sh scripts for Cosmos DB PostgreSQL |
| AZURE_COSMOSDB_PG_USER | Optional.  Used by the psql.ps1/psql.sh scripts for Cosmos DB PostgreSQL |
| LOCAL_PG_PASS | Optional.  Used by the psql.ps1/psql.sh scripts for local PostgreSQL access |

## Setting these Environment Variables

The repo contains generated PowerShell script **set-env-vars-sample.ps1**
which sets all of these AIG4PG_ environment values.
You may find it useful to edit and execute this script rather than set them manually on your system


## python-dotenv

The [python-dotenv](https://pypi.org/project/python-dotenv/) library is used
in each subapplication of this implementation.
It allows you to define environment variables in a file named **`.env`**
and thus can make it easier to use this project during local development.

Please see the **dotenv_example** files in each subapplication for examples.

It is important for you to have a **.gitignore** entry for the **.env** file
so that application secrets don't get leaked into your source control system.
