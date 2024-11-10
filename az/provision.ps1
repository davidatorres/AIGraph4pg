# Provisions an Azure PostgreSQL Server using the Azure CLI.
# See https://learn.microsoft.com/en-us/cli/azure/get-started-with-azure-cli
# Chris Joakim, Microsoft

# Initialize filename variables
$config_json_file = ".\provision-config.json"

function cli_arg_present {
    param (
        [string[]] $cli_args,
        [string] $flag
    )
    foreach ($arg in $cli_args) {
        if ($arg -eq $flag) {
            return 1
        }
    }
    return 0
}

function read_config_json() {
    try {
        $jsonObject = Get-Content -Path $config_json_file | ConvertFrom-JSON
        return $jsonObject
    }
    catch {
        Write-Host "ERROR: missing or malformed content in $config_file"
        Write-Host "script terminating"
        exit
    }
}

if (cli_arg_present $args "help") {
    Write-Output 'Usage of this Script:'
    Write-Output '  .\provision.ps1 help                 # display this output showing script usage'
    Write-Output '  .\provision.ps1 display_config       # display your configuration values per file provision-config.json'
    Write-Output '  .\provision.ps1 delete_output_files  # delete the *.* files in the \tmp directory'
    Write-Output '  .\provision.ps1 capture_az_cli_help  # execute az cli commands with --help arg'
    Write-Output '  .\provision.ps1 provision            # Provision the Azure PostgreSQL Server'
    Write-Output '  .\provision.ps1 delete_output_files capture_az_cli_help  # execute both commands'
    exit
}

# Ensure the existence of the tmp directory for redirected output
New-Item -ItemType Directory -Force -ErrorAction SilentlyContinue -Path "tmp" > $null

# Read the configuration JSON file and display its settings
$configData = read_config_json
$azure_subscription    = $configData.azure_subscription
$azure_region          = $configData.azure_region
$resource_group        = $configData.resource_group
$pg_server_name        = $configData.pg_server_name
$pg_sku_name           = $configData.pg_sku_name
$pg_high_availability  = $configData.pg_high_availability
$pg_database_name      = $configData.pg_database_name
$pg_admin_user_name    = $configData.pg_admin_user_name
$pg_admin_user_pass    = $configData.pg_admin_user_pass
$az_verbose_flag       = $configData.az_verbose_flag
Write-Host "Your Configuration Values per file provision-config.json:"
Write-Host "  azure_subscription:   $azure_subscription"
Write-Host "  azure_region:         $azure_region"
Write-Host "  resource_group:       $resource_group"
Write-Host "  pg_server_name:       $pg_server_name"
Write-Host "  pg_sku_name:          $pg_sku_name"
Write-Host "  pg_high_availability: $pg_high_availability"
Write-Host "  pg_database_name:     $pg_database_name"
Write-Host "  pg_admin_user_name:   $pg_admin_user_name"
Write-Host "  pg_admin_user_pass:   $pg_admin_user_pass"
Write-Host "  az_verbose_flag:      $az_verbose_flag"
Write-Host ""

if (cli_arg_present $args "delete_output_files") {
    Write-Output 'deleting output \tmp files ...'
    Remove-Item ".\tmp\*.*" -Force -ErrorAction SilentlyContinue
}

if (cli_arg_present $args "capture_az_cli_help") {
    az login --help        > tmp\help_az_login.txt
    az account set --help  > tmp\help_az_account_set.txt
    az account show --help > tmp\help_az_account_show.txt
    az group create --help > tmp\help_az_group_create.txt
    az postgres flexible-server create --help > tmp\help_az_postgres_flexible_server_create.txt
}

if (cli_arg_present $args "provision") {
    Write-Output 'deleting \tmp files ...'
    Remove-Item ".\tmp\*.*" -Force -ErrorAction SilentlyContinue

    Write-Output 'az login ...'
    az login $az_verbose_flag

    Write-Output 'setting subscription ...'
    az account set --subscription $az_verbose_flag > .\tmp\account_set.json
    
    Write-Output 'az account show (subscription) ...'
    az account show $az_verbose_flag > .\tmp\account_show.json

    Write-Output 'az ad signed-in-user show ...'
    az ad signed-in-user show $az_verbose_flag > .\tmp\signed_in_user_show.json

    Write-Output 'az group create ...'
    az group create `
        --name $resource_group `
        --location $azure_region $az_verbose_flag > .\tmp\az_group_create.json

    Write-Output 'az postgres flexible-server create ...'
    az postgres flexible-server create `
    --resource-group $resource_group `
        --name $pg_server_name `
        --sku-name $pg_sku_name `
        --high-availability $pg_high_availability `
        --database-name $pg_database_name `
        --password-auth Enabled `
        --admin-user $pg_admin_user_name `
        --admin-password $pg_admin_user_pass `
        --public-access 0.0.0.0 $az_verbose_flag > .\tmp\az_pg_flex_create.json

    Write-Output 'az postgres flexible-server parameter set ...'
    az postgres flexible-server parameter set `
        --resource-group $resource_group `
        --server-name $pg_server_name `
        --subscription $azure_subscription `
        --name azure.extensions `
        --value AGE,VECTOR > .\tmp\az_pg_flex_enable_extensions.json

    # You can later reset the password with:
    # az postgres flexible-server update -n gbbcjpggraph1server -g gbbcjpggraph1 -p <new-password>
}
