# PowerShell script to set the necessary AIG4PG_ environment variables,
# generated by dev.py on Sun Nov 10 08:51:47 2024
# Edit ALL of these generated values per your actual deployments.

echo "Setting AIG4PG environment variables"

echo 'setting AIG4PG_ENCRYPTION_SYMMETRIC_KEY'
[Environment]::SetEnvironmentVariable("AIG4PG_ENCRYPTION_SYMMETRIC_KEY", "", "User")

echo 'setting AIG4PG_LOG_LEVEL'
[Environment]::SetEnvironmentVariable("AIG4PG_LOG_LEVEL", "info", "User")

echo 'setting AIG4PG_OPENAI_COMPLETIONS_DEP'
[Environment]::SetEnvironmentVariable("AIG4PG_OPENAI_COMPLETIONS_DEP", "gpt4", "User")

echo 'setting AIG4PG_OPENAI_EMBEDDINGS_DEP'
[Environment]::SetEnvironmentVariable("AIG4PG_OPENAI_EMBEDDINGS_DEP", "embeddings", "User")

echo 'setting AIG4PG_OPENAI_KEY'
[Environment]::SetEnvironmentVariable("AIG4PG_OPENAI_KEY", "", "User")

echo 'setting AIG4PG_OPENAI_URL'
[Environment]::SetEnvironmentVariable("AIG4PG_OPENAI_URL", "", "User")

echo 'setting AIG4PG_PG_FLEX_DB'
[Environment]::SetEnvironmentVariable("AIG4PG_PG_FLEX_DB", "", "User")

echo 'setting AIG4PG_PG_FLEX_PASS'
[Environment]::SetEnvironmentVariable("AIG4PG_PG_FLEX_PASS", "", "User")

echo 'setting AIG4PG_PG_FLEX_PORT'
[Environment]::SetEnvironmentVariable("AIG4PG_PG_FLEX_PORT", "5432", "User")

echo 'setting AIG4PG_PG_FLEX_SERVER'
[Environment]::SetEnvironmentVariable("AIG4PG_PG_FLEX_SERVER", "", "User")

echo 'setting AIG4PG_PG_FLEX_USER'
[Environment]::SetEnvironmentVariable("AIG4PG_PG_FLEX_USER", "", "User")

echo 'setting AIG4PG_TRUNCATE_LLM_CONTEXT_MAX_NTOKENS'
[Environment]::SetEnvironmentVariable("AIG4PG_TRUNCATE_LLM_CONTEXT_MAX_NTOKENS", "0", "User")

echo 'setting AZURE_COSMOSDB_PG_PASS'
[Environment]::SetEnvironmentVariable("AZURE_COSMOSDB_PG_PASS", "", "User")

echo 'setting AZURE_COSMOSDB_PG_SERVER'
[Environment]::SetEnvironmentVariable("AZURE_COSMOSDB_PG_SERVER", "", "User")

echo 'setting AZURE_COSMOSDB_PG_USER'
[Environment]::SetEnvironmentVariable("AZURE_COSMOSDB_PG_USER", "", "User")

echo 'setting LOCAL_PG_PASS'
[Environment]::SetEnvironmentVariable("LOCAL_PG_PASS", "", "User")

