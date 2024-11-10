"""
This program is used for the development of the AIGraph4PG project
and not for users of the project.
Usage:
    python dev.py log_defined_env_vars
    python dev.py gen_dotenv_examples
    python dev.py gen_ps1_env_var_script
    python dev.py gen_docker_compose_fragment
    python dev.py gen_docker_requirements_txt
    python dev.py gen_environment_variables_md
    python dev.py gen_queries_json
    python dev.py gen_all
    python dev.py create_libraries_cypher_load_statements 999999
    python dev.py encrypt_your_env_values tmp/envvars.txt
Options:
  -h --help     Show this screen.
  --version     Show version.
"""

import json
import logging
import os
import sys
import time
import traceback
import zipfile

from datetime import datetime
from docopt import docopt
from dotenv import load_dotenv

from src.services.config_service import ConfigService
from src.services.logging_level_service import LoggingLevelService

from src.util.fs import FS
from src.util.template import Template
from src.util.sample_query import SampleQuery
from src.util.sample_queries import SampleQueries

logging.basicConfig(
    format="%(asctime)s - %(message)s", level=LoggingLevelService.get_level()
)


def print_options(msg):
    print("{} {}".format(os.path.basename(__file__), msg))
    arguments = docopt(__doc__, version=ConfigService.project_version())
    print(arguments)


def log_defined_env_vars():
    logging.info("log_defined_env_vars")
    ConfigService.log_defined_env_vars()


def gen_dotenv_examples():
    envvars = ConfigService.defined_environment_variables()
    samples = ConfigService.sample_environment_variable_values()
    sample_lines, actuals_lines = list(), list()

    for name in sorted(envvars.keys()):
        if "COSMOSDB_PG" in name:
            pass  # This project does not use the CosmosDB PostgreSQL API
        else:
            sample_value = samples[name]
            actual_value = ""
            try:
                actual_value = ConfigService.envvar(name, "")
            except:
                pass
            sample_lines.append('{}="{}"'.format(name, sample_value))
            actuals_lines.append('{}="{}"'.format(name, actual_value))
    FS.write_lines(sample_lines, "dotenv_example")
    FS.write_lines(actuals_lines, "tmp/dotenv_example")
    logging.info("Note: file dotenv_example contains sample values")
    logging.info(
        "Note: file tmp/dotenv_example contains your actual environment variable values"
    )


def gen_ps1_env_var_script():
    env_var_names = sorted(ConfigService.defined_environment_variables().keys())
    samples = ConfigService.sample_environment_variable_values()
    lines = list()
    lines.append(
        "# PowerShell script to set the necessary AIG4PG_ environment variables,"
    )
    lines.append("# generated by dev.py on {}".format(time.ctime()))
    lines.append("# Edit ALL of these generated values per your actual deployments.")
    lines.append("")
    lines.append('echo "Setting AIG4PG environment variables"')

    for name in env_var_names:
        value = ""
        if name in samples:
            value = samples[name]
        lines.append("")
        lines.append("echo 'setting {}'".format(name))
        lines.append(
            "[Environment]::SetEnvironmentVariable(|{}|, |{}|, |User|)".format(
                name, value
            ).replace("|", '"')
        )
    lines.append("")
    FS.write_lines(lines, "set-env-vars-sample.ps1")


def gen_docker_compose_fragment():
    env_var_names = sorted(ConfigService.defined_environment_variables().keys())
    excluded_env_vars = compose_excluded_envvars()
    filtered_env_var_names = list()
    compose_env_lines = list()

    for env_var_name in env_var_names:
        if env_var_name not in excluded_env_vars:
            filtered_env_var_names.append(env_var_name)

    for env_var_name in sorted(filtered_env_var_names):
        name_with_colon = env_var_name + ":"
        compose_env_lines.append(
            "      {:<35} ${}".format(name_with_colon, env_var_name)
        )

    FS.write_lines(compose_env_lines, "tmp/generated.compose.env")


def gen_docker_requirements_txt():
    """
    Automation to replace tedious manual editing of the requirements.txt
    file used to build the Docker image.
    """
    dev_requirements = FS.read_lines("requirements.txt")
    docker_lines = list()
    docker_lines.append("# Generated by dev.py on {}".format(time.ctime()))
    docker_lines.append(
        "# This File excludes Windows-specific Python libraries\n# from the Docker image."
    )
    docker_lines.append("")
    exclude_libs = "pywin32".split(",")
    for line in dev_requirements:
        stripped = line.strip()  # example: pywin32==308
        if (stripped.startswith("#")) or (len(line) == 0):
            pass
        else:
            lib_version_tokens = stripped.split("==")
            if len(lib_version_tokens) == 2:
                lib_name = lib_version_tokens[0]
                if lib_name not in exclude_libs:
                    docker_lines.append(line.strip())
                else:
                    docker_lines.append(
                        "# {}  <-- excluded from Docker image".format(line.strip())
                    )
            else:
                print("unexpected requirements.txt line: {}".format(line))

    FS.write_lines(docker_lines, "requirements-docker.txt")


def compose_excluded_envvars():
    """
    Return a list of the AIG4PG_xxx environment variable names
    that should be excluded from Docker compose.
    """
    vars = list()
    vars.append("AIG4PG_HOME")
    vars.append("AIG4PG_WEB_APP_PORT")
    vars.append("AIG4PG_WEB_APP_URL")
    return vars


def gen_envvars_master_entries():
    """generate a partial config file for my personal envvar solution - cj"""
    samples = ConfigService.sample_environment_variable_values()
    env_var_names = sorted(ConfigService.defined_environment_variables().keys())
    lines = list()
    for name in env_var_names:
        value = ConfigService.envvar(name, "")
        if len(value) == 0:
            if name in samples.keys():
                value = samples[name]
        padded = name.ljust(35)
        lines.append("{} ||| {}".format(padded, value))
    FS.write_lines(lines, "tmp/app-envvars-master.txt")


def gen_environment_variables_md():
    lines = list()
    lines.append("# AIGraph4pg Implementation 1 : Environment Variables")
    lines.append("")
    lines.append(
        "Per the [Twelve-Factor App methodology](https://12factor.net/config),"
    )
    lines.append("configuration is stored in environment variables.  ")
    lines.append("")
    lines.append("## Defined Variables")
    lines.append("")
    lines.append(
        "This reference implementation uses the following environment variables."
    )
    lines.append("| Name | Description |")
    lines.append(
        "| --------------------------------- | --------------------------------- |"
    )
    env_var_names = sorted(ConfigService.defined_environment_variables().keys())
    for name in env_var_names:
        desc = ConfigService.defined_environment_variables()[name]
        lines.append("| {} | {} |".format(name, desc))

    lines.append("")
    lines.append("## Setting these Environment Variables")
    lines.append("")
    lines.append(
        "The repo contains generated PowerShell script **set-env-vars-sample.ps1**"
    )
    lines.append("which sets all of these AIG4PG_ environment values.")
    lines.append(
        "You may find it useful to edit and execute this script rather than set them manually on your system"
    )
    lines.append("")

    lines.append("")
    lines.append("## python-dotenv")
    lines.append("")
    lines.append(
        "The [python-dotenv](https://pypi.org/project/python-dotenv/) library is used"
    )
    lines.append("in each subapplication of this implementation.")
    lines.append(
        "It allows you to define environment variables in a file named **`.env`**"
    )
    lines.append(
        "and thus can make it easier to use this project during local development."
    )
    lines.append("")
    lines.append(
        "Please see the **dotenv_example** files in each subapplication for examples."
    )
    lines.append("")
    lines.append(
        "It is important for you to have a **.gitignore** entry for the **.env** file"
    )
    lines.append(
        "so that application secrets don't get leaked into your source control system."
    )
    lines.append("")

    FS.write_lines(lines, "../docs/environment_variables.md")


def gen_queries_json():
    queries = list()

    queries.append(
        {
            "type": "sql",
            "name": "Count Library rows in table",
            "text": "select count(*) from libraries",
        }
    )

    queries.append(
        {
            "type": "cypher",
            "name": "Count Library vertices in graph",
            "text": """
SELECT * FROM ag_catalog.cypher('libraries1',
    $$ MATCH (lib:Library ) RETURN count(*) $$)
as (v agtype);""",
        }
    )
    queries.append(
        {
            "type": "cypher",
            "name": "Count Developer vertices in graph",
            "text": """
SELECT * FROM ag_catalog.cypher('libraries1',
    $$ MATCH (lib:Developer ) RETURN count(*) $$)
as (v agtype);""",
        }
    )
    FS.write_json(queries, "config/queries.json")


def gen_all():
    gen_dotenv_examples()
    gen_ps1_env_var_script()
    gen_docker_compose_fragment()
    gen_docker_requirements_txt()
    gen_environment_variables_md()
    gen_queries_json()


def encryption_example():
    logging.info("encryption_example")
    test_cases = [
        "",
        "hello earth",
        "867-5309",
        "8888fbdbb32943ad9874ceXX729f53bh",
        "jwonQQTexjIQvYTfX4Rx6LoVT5mCf8yYDorkAz8LrK4FsGzOa8L9At33Kzflj26xCS4JCiYr9swgXYDbV8pnqQ==",
        "https://en.wikipedia.org/wiki/Easter_Island",
    ]

    # Example of how to generate your own key
    fernet_key = ConfigService.generate_fernet_key()
    print("fernet_key: {}".format(fernet_key))

    key = ConfigService.symmetric_encryption_key()
    print("key: {}".format(key))

    for idx, value in enumerate(test_cases):
        encrypted = ConfigService.sym_encrypt(value)
        decrypted = ConfigService.sym_decrypt(encrypted)
        print("test_case {}:".format(idx))
        print("  value:     <{}>".format(value))
        print("  encrypted: <{}>".format(encrypted))
        print("  decrypted: <{}>".format(decrypted))
        if value == decrypted:
            print("  SUCCESS")
        else:
            print("  FAILURE")


def encrypt_your_env_values(infile):
    """
    Produce Windows PowerShell script tmp/encrypted_envvars.ps1
    to set the encrypted environment variables per your input text file.
    The input file contains lines with environment variable names, a colon,
    and their corresponding unencrypted values.

    You may want to encrypt the following environment values:
    AIG4PG_OPENAI_KEY
    AIG4PG_OPENAI_URL
    AIG4PG_PG_FLEX_SERVER
    AIG4PG_PG_FLEX_USER
    AIG4PG_PG_FLEX_PASS

    Please see the input text file validation logic below.
    """
    lines = FS.read_lines(infile)
    file_has_errors = False
    ps1_line_template = '[Environment]::SetEnvironmentVariable("{}", "{}", "User")'
    output_lines = list()
    today = datetime.today().strftime("%Y-%m-%d")
    output_lines.append(
        "# This script was generated on {} with the following command:".format(today)
    )
    output_lines.append("# python dev.py encrypt_your_env_values {}".format(infile))

    # First, validate the file:
    # Each line must contain three tokens - an environment variable name, a colon, and a value.
    # The colon must be surrounded by spaces.
    # The environment variable name in the first line must be AIG4PG_ENCRYPTION_SYMMETRIC_KEY,
    # and its corresponding value will be used for this encryption process.
    for idx, line in enumerate(lines):
        line = line.strip()
        tokens = line.split(" : ")
        if idx == 0:
            if tokens[0] != "AIG4PG_ENCRYPTION_SYMMETRIC_KEY":
                print(
                    "ERROR: first line must be AIG4PG_ENCRYPTION_SYMMETRIC_KEY : your-encryption-key"
                )
                file_has_errors = True
        if len(tokens) != 2:
            print(
                "ERROR: line {} has {} tokens, expected 2".format(idx + 1, len(tokens))
            )
            file_has_errors = True

    if file_has_errors == True:
        print("ERROR: file has errors, aborting, please correct the file and try again")
        return

    for idx, line in enumerate(lines):
        line = line.strip()
        tokens = line.split(" : ")
        if idx == 0:
            encryption_key = tokens[1].strip()
            print("using encryption_key: {}".format(encryption_key))
            os.environ["AIG4PG_ENCRYPTION_SYMMETRIC_KEY"] = encryption_key
            if ConfigService.symmetric_encryption_key() == encryption_key:
                print("Ok encryption_key has been set in ConfigService")
                line = ps1_line_template.format(
                    "AIG4PG_ENCRYPTION_SYMMETRIC_KEY", encryption_key
                )
                output_lines.append("")
                output_lines.append(line)
            else:
                print("ERROR: encryption_key has not been set in ConfigService")
                file_has_errors = True
                return
        else:
            if file_has_errors == False:
                env_var_name = tokens[0].strip()
                env_var_value = tokens[1].strip()
                encrypted = ConfigService.sym_encrypt(env_var_value)
                decrypted = ConfigService.sym_decrypt(encrypted)
                if env_var_value == decrypted:
                    ps1_line_template = (
                        '[Environment]::SetEnvironmentVariable("{}", "{}", "User")'
                    )
                    line = ps1_line_template.format(env_var_name, encrypted)
                    output_lines.append("")
                    output_lines.append("# original value {}".format(env_var_value))
                    output_lines.append(line)
                else:
                    print(
                        "ERROR: encryption/decryption mismatch for line {}".format(line)
                    )
                    file_has_errors = True

    if file_has_errors == False:
        FS.write_lines(output_lines, "tmp/encrypted_envvars.ps1")


def filter_files_list(files_list, suffix):
    filtered = list()
    for f in files_list:
        if f.endswith(suffix):
            filtered.append(f)
    return filtered


def create_libraries_cypher_load_statements(count):
    """ """
    data_dir = "../data/pypi/wrangled_libs"
    logging.info("load_libraries_table, data_dir: {}".format(data_dir))
    files_list = FS.list_files_in_dir(data_dir)
    filtered_files_list = filter_files_list(files_list, ".json")
    library_docs_list, developers = list(), dict()
    cypher_statements, edge_statements = list(), list()
    library_count, developer_count, exception_count = 0, 0, 0
    graphname = "libraries1"

    # Load the libraries documents into a list for subsequent iteration
    for file_idx, lib_filename in enumerate(filtered_files_list):
        if file_idx < count:
            fq_filename = "{}/{}".format(data_dir, lib_filename)
            logging.info("data_file {}: {}".format(file_idx, fq_filename))
            library_docs_list.append(FS.read_json(fq_filename))
    logging.info("library docs list count: {}".format(len(library_docs_list)))

    library_vertex_template = get_template("create_cypher_library_vertex.txt")
    developer_vertex_template = get_template("create_cypher_developer_vertex.txt")
    library_library_vertex_template = get_template("create_cypher_lib_lib_edge.txt")
    generic_edge_template = get_template("create_cypher_generic_edge.txt")

    # Collect the unique developers, and create their vertices
    for doc in library_docs_list:
        if "developers" in doc.keys():
            for dev in doc["developers"]:
                if dev in developers.keys():
                    pass  # already processed
                else:
                    developers[dev] = 1
                    values = dict()
                    values["graphname"] = graphname
                    values["name"] = dev
                    cypher = Template.render(developer_vertex_template, values)
                    cypher_statements.append(cypher.replace("\n", " ").strip())
                    developer_count = developer_count + 1
    logging.info("developer count: {}".format(len(developers)))

    # Collect the library vertices and their edges
    for doc in library_docs_list:
        try:
            libname = str(doc["name"]).replace("'", "").strip()
            values = dict()
            values["graphname"] = graphname
            values["name"] = libname
            values["libtype"] = str(doc["libtype"]).replace("'", "").strip()
            values["license"] = str(doc["license"]).replace("'", "").strip()[0:40]
            values["keywords"] = str(doc["keywords"]).replace("'", "").strip()
            values["release_count"] = int(doc["release_count"])
            print(values)
            cypher = Template.render(library_vertex_template, values)
            cypher_statements.append(cypher.replace("\n", " ").strip())
            library_count = library_count + 1

            if "dependency_ids" in doc.keys():
                for dep_libtype_libname in doc["dependency_ids"]:
                    dep_libname = dep_libtype_libname[5:]

                    values = dict()
                    values["graphname"] = graphname
                    values["lib1"] = libname
                    values["lib2"] = dep_libname
                    values["relname"] = "uses_lib"
                    cypher = Template.render(library_library_vertex_template, values)
                    edge_statements.append(cypher.replace("\n", " ").strip())

                    values = dict()
                    values["graphname"] = graphname
                    values["lib1"] = dep_libname
                    values["lib2"] = libname
                    values["relname"] = "used_by_lib"
                    cypher = Template.render(library_library_vertex_template, values)
                    edge_statements.append(cypher.replace("\n", " ").strip())

            if "developers" in doc.keys():
                for dev in doc["developers"]:
                    values = dict()
                    values["graphname"] = graphname
                    values["type1"] = "Developer"
                    values["type2"] = "Library"
                    values["attr1"] = "name"
                    values["val1"] = libname
                    values["attr2"] = "name"
                    values["val2"] = dev
                    values["relname"] = "developer_of"
                    cypher = Template.render(generic_edge_template, values)
                    edge_statements.append(cypher.replace("\n", " ").strip())

                    values = dict()
                    values["graphname"] = graphname
                    values["type1"] = "Library"
                    values["type2"] = "Developer"
                    values["attr1"] = "name"
                    values["val1"] = libname
                    values["attr2"] = "name"
                    values["val2"] = dev
                    values["relname"] = "developed_by"
                    cypher = Template.render(generic_edge_template, values)
                    edge_statements.append(cypher.replace("\n", " ").strip())

        except Exception as e:
            exception_count = exception_count + 1
            logging.error("error processing library name: {}".format(doc["name"]))
            logging.critical(str(e))
            logging.exception(e, stack_info=True, exc_info=True)

    # The output file thus has all of the vertices first, followed by the edges.
    for cypher in edge_statements:
        cypher_statements.append(cypher.strip())

    try:
        # The output file is large, too large for GitHub, so we write it
        # to a git-ignored tmporary file, then zip it to ../data/cypher/libraries.zip
        # for storage in GitHub.  It can be unzipped with 'jar xvf libraries.zip'.
        txt_file = "libraries.txt"
        zip_file = "../data/cypher/libraries.zip"
        FS.write_lines(cypher_statements, txt_file)
        with zipfile.ZipFile(zip_file, "w", zipfile.ZIP_DEFLATED) as z:
            z.write(txt_file)
    except Exception as e:
        logging.error("error creating output file or zip file")
        logging.critical(str(e))
        logging.exception(e, stack_info=True, exc_info=True)

    logging.info("Totals:")
    logging.info("  library_count:     {}".format(library_count))
    logging.info("  developer_count:   {}".format(len(developers)))
    logging.info("  edge_count:        {}".format(len(edge_statements)))
    logging.info("  exception_count:   {}".format(exception_count))
    logging.info("  cypher_statements: {}".format(len(cypher_statements)))

    # 2024-11-05 16:06:11,613 - file written: libraries.txt
    # 2024-11-05 16:06:11,790 - Totals:
    # 2024-11-05 16:06:11,791 -   library_count:     10855
    # 2024-11-05 16:06:11,791 -   developer_count:   10466
    # 2024-11-05 16:06:11,791 -   edge_count:        157024
    # 2024-11-05 16:06:11,792 -   exception_count:   0
    # 2024-11-05 16:06:11,792 -   cypher_statements: 178345


def get_template(template_name):
    return Template.get_template(os.getcwd(), template_name)


def ad_hoc_development():
    q = SampleQuery()
    q.set_name("Count the rows")
    q.set_type("sql")
    q.append_to_text("select * ")
    q.append_to_text("from t444;")
    print(q.get_data())
    print(q.is_valid())

    queries = SampleQueries.read_queries()
    FS.write_json(queries, "tmp/sample_queries.json")


if __name__ == "__main__":
    load_dotenv(override=True)

    if len(sys.argv) < 2:
        print_options("- no command-line args given")
        exit(1)
    else:
        try:
            func = sys.argv[1].lower()
            if func == "log_defined_env_vars":
                log_defined_env_vars()
            elif func == "gen_dotenv_examples":
                gen_dotenv_examples()
            elif func == "gen_ps1_env_var_script":
                gen_ps1_env_var_script()
            elif func == "gen_docker_compose_fragment":
                gen_docker_compose_fragment()
            elif func == "gen_docker_requirements_txt":
                gen_docker_requirements_txt()
            elif func == "gen_environment_variables_md":
                gen_environment_variables_md()
            elif func == "gen_queries_json":
                gen_queries_json()
            elif func == "gen_all":
                gen_all()
            elif func == "encryption_example":
                encryption_example()
            elif func == "encrypt_your_env_values":
                infile = sys.argv[2]
                encrypt_your_env_values(infile)
            elif func == "create_libraries_cypher_load_statements":
                count = int(sys.argv[2])
                create_libraries_cypher_load_statements(count)
            elif func == "ad_hoc":
                ad_hoc_development()
            else:
                print_options("- error - invalid function: {}".format(func))
        except Exception as e:
            logging.critical(str(e))
            logging.exception(e, stack_info=True, exc_info=True)
