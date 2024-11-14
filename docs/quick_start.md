# AIGraph4pg - Quick Start Documentation

These instructions are intended to help you deploy Azure PaaS Services
run this reference application on your workstation.

## Recommended Skills

- Some programming language experience, especially with Python 3
  - See https://www.python.org/

- Some understanding of Python virtual environments
  - See https://realpython.com/python-virtual-environments-a-primer/

- Some understanding of Environment Variables

- Some command-line experience, Windows PowerShell or linux/macOS bash shell
  - https://learn.microsoft.com/en-us/powershell/scripting/overview?view=powershell-7.4 
  - https://support.apple.com/guide/terminal/welcome/mac

There will be several steps to execute in this Quick Start,
**it is not a "one-click" deploy**.

---

## Workstation Requirements

- **Windows 11** or recent **linux or macOS** desktop operating system
  - This solution is mostly Windows and PowerShell oriented, with *.ps1 scripts
  - But the *.sh scripts have been tested on macOS with the bash shell

- The **git** source-control system
  - Used here only to clone the public repository
  - See https://git-scm.com/

- The **Azure CLI** (i.e. - az)
  - See https://learn.microsoft.com/en-us/cli/azure/

- An **Azure Subscription**

- **Standard Python 3.12.x**
  - See https://www.python.org/downloads/
  - Not Conda or other distributions

- **Visual Studio Code (VSC)** or similar IDE/editor
  - See https://code.visualstudio.com/

- **A PostgreSQL client program, such as psql**
  - See https://www.postgresql.org/docs/current/app-psql.html

- **A local/desktop PostgreSQL database installation**
  - This is optional, but useful for learning the basics of PostgreSQL

- **Docker Desktop**
  - This is optional, used only for executing the public DockerHub image
  - macOS users on Apple Silicon (i.e. - m1 to m4) will have to build the Docker image for that platform

---

## Azure PaaS Services to Deploy

- **Azure PostgreSQL**
  - See the **az/** directory in this repo
  - Copy file **az/provision-config-example.json** to **az/provision-config.json**
    - az/provision-config.json is not in git source control, it is git-ignored for security purposes
  - Edit the **az/provision-config.json** per your subscription
    - The entry names are self-explanatory
  - Execute **az login**
    - See https://learn.microsoft.com/en-us/cli/azure/authenticate-azure-cli
  - Execute the **az/provision.ps1** script to provision your Azure PostgreSQL server
  - Alternatively, provision this manually in Azure Portal
    - Enable the VECTOR and AGE extensions
    - See https://learn.microsoft.com/en-us/azure/postgresql/flexible-server/concepts-extensions

- **Azure OpenAI**
  - Recommended, for this project, to provision this manually in Azure Portal
  - Create a **text-embedding-ada-002** model deployment, for embeddings and vector search
  - Create a **gpt-4o** model deployment, for generative AI of openCypher queries

---

## A Note on Windows PowerShell and macOS bash Terminal

The remaining instructions on this page describe how you should
execute **command-line** commands in either Windows PowerShell
or the macOS Terminal program with the bash shell.  These instructions
are primarily Windows-based, but macOS is supported, too.

In the remaining documentation on this page, the relative directory
location is shown for your reference.  For example, in Windows PowerShell, 
when you are in the **root directory** of the GitHub project you'll
see instructions like this:

```
aigraph4pg> some command in the root directory
```

Likewise, when you're in the **python directory** beneath the aigraph4pg 
directory, the instructions will look like this:

```
python> some command in the python directory
```

The project directory structure looks like this:

```
├── az
├── data
│   ├── cypher               <-- curated list of statements to populate the Apache AGE graph
│   └── pypi
│       └── wrangled_libs    <-- the curated libraries dataset, pre-vectorized
├── docs
│   └── img
└── python
    ├── docker               <-- Dockerfile and docker-compose.yml
    ├── sql                  <-- DDL and SQL files for psql and python logic
    ├── src                  <-- Python source code
    │   ├── models
    │   ├── services
    │   └── util
    ├── static               <-- static files used by the Web UI application
    ├── templates            <-- jinga2 text templates 
    ├── tests                <-- Unit tests built on the pytest framework
    ├── venv                 <-- The Python virtual environment, not in Git (git ignored)
    └── views                <-- Web UI HTML page templates
```

---

## Set the Environment Variables for this project

These generally begin with the previx **AIG4PG_** or **AZURE_**.

TODO - refine

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

--- 

## Clone the GitHub repo and create the Python Virtual Environment

These are one-time tasks in the use of this project.

### Clone the Repo

This will copy the code, scripts, and curated data files to your computer.

```
> cd some-parent-directory-on-your-computer

> git clone https://github.com/cjoakim/aigraph4pg.git

> cd aigraph4pg    <-- this is the project root directory
```

### Create the Python Virtual Environment

A Python Virtual Environment is an isolated location on your computer
containing a well-defined set of required libraries, defined in the 
**requirements.in** file.  The libraries are downloaded from [PyPi](https://pypi.org/).
The application code in this project then uses these Python libraries.

This is conceptually similar to NuGet (DotNet ecosystem), MavenCentral (Java ecocystem),
NPM (Node.js and JavaScript ecosystem), etc..

```
aigraph4pg> cd python       

python>                   <-- You'll primarily use this directory in this project

python> .\venv.ps1

python> pip list          <-- pip is the library installer program; you'll see smilar output below

Package                   Version
------------------------- -----------
aiofiles                  23.2.1
aiohappyeyeballs          2.4.3
aiohttp                   3.10.10
aiosignal                 1.3.1
annotated-types           0.7.0
anyio                     4.6.2.post1
asgiref                   3.8.1
attrs                     24.2.0
azure-core                1.31.0
azure-identity            1.19.0
azure-storage-blob        12.23.1
black                     24.10.0
build                     1.2.2.post1
certifi                   2024.8.30
cffi                      1.17.1
chardet                   5.2.0
charset-normalizer        3.4.0
click                     8.1.7
colorama                  0.4.6
coverage                  7.6.4
cryptography              43.0.3
defusedxml                0.7.1
distro                    1.9.0
dnspython                 2.7.0
docopt                    0.6.2
Faker                     26.1.0
fastapi                   0.115.3
fastapi_msal              2.1.6
frozenlist                1.5.0
h11                       0.14.0
h2                        4.1.0
hpack                     4.0.0
httpcore                  1.0.6
httpx                     0.27.2
Hypercorn                 0.17.3
hyperframe                6.0.1
idna                      3.10
iniconfig                 2.0.0
isodate                   0.7.2
itsdangerous              2.2.0
Jinja2                    3.1.4
jiter                     0.6.1
jsonschema                4.23.0
jsonschema-path           0.3.3
jsonschema-spec           0.2.4
jsonschema-specifications 2023.7.1
lazy-object-proxy         1.10.0
MarkupSafe                3.0.2
more-itertools            10.5.0
motor                     3.6.0
msal                      1.31.0
msal-extensions           1.2.0
multidict                 6.1.0
mypy-extensions           1.0.0
numpy                     1.26.4
openai                    1.52.2
openapi-core              0.18.2
openapi-schema-validator  0.6.2
openapi-spec-validator    0.7.1
packaging                 24.1
parse                     1.20.2
pathable                  0.4.3
pathspec                  0.12.1
pip                       24.3.1
pip-tools                 7.4.1
platformdirs              4.3.6
pluggy                    1.5.0
portalocker               2.10.1
prance                    23.6.21.0
priority                  2.0.0
propcache                 0.2.0
psycopg                   3.2.3
psycopg-binary            3.2.3
psycopg-pool              3.2.3
pycparser                 2.22
pydantic                  2.9.2
pydantic_core             2.23.4
pydantic-settings         2.6.0
PyJWT                     2.9.0
pymongo                   4.9.2
pyproject_hooks           1.2.0
pytest                    8.3.3
pytest-asyncio            0.24.0
pytest-cov                5.0.0
python-dateutil           2.9.0.post0
python-dotenv             1.0.1
python-multipart          0.0.15
pywin32                   308
PyYAML                    6.0.2
referencing               0.30.2
regex                     2023.12.25
requests                  2.32.3
rfc3339-validator         0.1.4
rpds-py                   0.20.0
ruamel.yaml               0.18.6
ruamel.yaml.clib          0.2.12
semantic-kernel           0.9.1b1
setuptools                75.3.0
six                       1.16.0
sniffio                   1.3.1
starlette                 0.41.2
tiktoken                  0.8.0
tqdm                      4.66.5
typing_extensions         4.12.2
tzdata                    2024.2
urllib3                   2.2.3
uvicorn                   0.32.0
Werkzeug                  3.0.6
wheel                     0.44.0
wsproto                   1.2.0
xmlformatter              0.2.6
yarl                      1.16.0
```

### Activate the Python Virtual Environment (venv)

**Each time** you navigate to the python directory of this project
and want to execute a python program you will need to **"activate"** the
virtual environment, as shown below:

Notice how when the Virtual Environment is activated your shell
prompt changes to have the **(venv)** prefix.
This is a useful visual cue.

#### Windows 11 PowerShell

```
PS ...\python>
PS ...\python> .\venv\Scripts\Activate.ps1
(venv) PS ...\python>
```

#### macOS bash shell

```
[~/aigraph4pg]$ cd python
[~/aigraph4pg/python]$ source venv/bin/activate
(venv) [~/aigraph4pg/python]$
```

---

## Prepare your Azure PostgreSQL Server

TODO

---

## Load Azure PostgreSQL with the Python Libraries Dataset

The dataset is a curated set of information on 10,000+ **Python Libraries**
from web crawling and other tools.  This dataset provides a foundation to
demonstrate both **traditional graph** as well as **vector search**
capabilities in Azure PostgreSQL.

The Python libraries have both dependencies and authors, and this graph
can be traversed.  Likewise, Python library data has rich text fields
(descriptions, keywords) that showcase vector search.

It is hoped that this dataset is relatable to an IT audience, particularly
application developers, and data scientists.

### main.py

This is the Python program (i.e. - *.py suffix) that implements the
**"console app"** in this project.  You can see its **help content**
by executing the following:

```
python> python .\main.py help

...
Usage:
    python main.py log_defined_env_vars
    python main.py list_pg_extensions_and_settings
    python main.py delete_define_libraries_table
    python main.py load_libraries_table
    python main.py create_libraries_table_vector_index sql/libraries_ivfflat_index.sql
    python main.py vector_search_similar_libraries flask 10
    python main.py vector_search_words word1 word2 word3 etc
    python main.py vector_search_words running calculator miles kilometers pace speed mph
    python main.py load_age_graph ../data/cypher/us_openflights.json
Options:
  -h --help     Show this screen.
  --version     Show version.
```

### main.py - delete_define_libraries_table

```
python> python .\main.py delete_define_libraries_table
```

### main.py - load_libraries_table

```
python> python .\main.py load_libraries_table
```

### main.py - vector_search_similar_libraries

```
python> python .\main.py vector_search_similar_libraries flask 10
```

### main.py - vector_search_words

```
python> python .\main.py vector_search_words web framework asynchronous swagger endpoints
```
