# This is the entry-point for this web application, built with the
# FastAPI web framework
#
# Chris Joakim

import asyncio
import json
import logging
import textwrap
import time
import traceback
import sys

import psycopg
import psycopg_pool

from dotenv import load_dotenv

from fastapi import FastAPI, Request, Response, Form, status
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# next three lines for authentication with MSAL
from fastapi import Depends
from starlette.middleware.sessions import SessionMiddleware

# Pydantic models defining the "shapes" of requests and responses
from src.models.webservice_models import PingModel
from src.models.webservice_models import LivenessModel
from src.models.webservice_models import AiConvFeedbackModel

# Services with Business Logic
from src.services.ai_service import AiService
from src.services.config_service import ConfigService
from src.services.logging_level_service import LoggingLevelService
from src.util.fs import FS
from src.util.query_result_parser import QueryResultParser
from src.util.sample_queries import SampleQueries

# standard initialization
load_dotenv(override=True)
logging.basicConfig(
    format="%(asctime)s - %(message)s", level=LoggingLevelService.get_level()
)
ConfigService.print_defined_env_vars()
logging.error("project_version: {}".format(ConfigService.project_version()))

if sys.platform == "win32":
    logging.warning("Windows platform detected, setting WindowsSelectorEventLoopPolicy")
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
else:
    logging.warning(
        "platform is {}, not Windows.  Not setting event_loop_policy".format(
            sys.platform
        )
    )

POOL = None


def get_database_connection_string():
    db = ConfigService.postgresql_database()
    user = ConfigService.postgresql_user()
    password = ConfigService.postgresql_password()
    host = ConfigService.postgresql_server()
    port = ConfigService.postgresql_port()
    conn_str = "host={} port={} dbname={} user={} password={}".format(
        host, port, db, user, password
    )
    logging.info(
        "get_database_connection_string: {} password=<omitted>".format(
            conn_str.split("password")[0]
        )
    )
    return conn_str


async def initialize_async_services():
    global POOL
    try:
        conn_str = get_database_connection_string()
        POOL = psycopg_pool.AsyncConnectionPool(conninfo=conn_str, open=False)
        logging.info("initialze_pool, pool created: {}".format(POOL))
        await POOL.open()
        await POOL.check()
        logging.info("initialize_async_services, POOL opened")
    except Exception as e:
        logging.error("initialize_async_services - exception: {}".format(str(e)))
        logging.error(traceback.format_exc())


event_loop = None
try:
    event_loop = asyncio.get_running_loop()
except:
    pass
logging.error("event_loop: {}".format(event_loop))

if event_loop is not None:
    # this path is for running in a Docker container with uvicorn
    logging.error("asyncio event_loop is not None")
    task = asyncio.create_task(initialize_async_services())
else:
    # this path is for running as a Python script
    logging.error("asyncio event_loop is None")
    asyncio.run(initialize_async_services())


app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
views = Jinja2Templates(directory="views")
logging.error("webapp.py started")


@app.get("/ping")
async def get_ping() -> PingModel:
    resp = dict()
    resp["epoch"] = str(time.time())
    return resp


@app.get("/liveness")
async def get_liveness(req: Request, resp: Response) -> LivenessModel:
    """
    Return a LivenessModel indicating the health of this web app.
    This endpoint may be invoked by a container orchestrator, such as
    Azure Container Apps (ACA) or Azure Kubernetes Service (AKS).
    The implementation validates the environment variable and url configuration.
    """
    alive = True  # TODO - implement a real liveness check

    if alive == True:
        resp.status_code = status.HTTP_200_OK
    else:
        resp.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    liveness_data = dict()
    liveness_data["alive"] = alive
    liveness_data["rows_read"] = 0
    liveness_data["epoch"] = time.time()
    liveness_data["version"] = ConfigService.project_version()
    logging.info("liveness_check: {}".format(liveness_data))
    return liveness_data


@app.get("/")
async def get_home(req: Request):
    view_data = dict()
    return views.TemplateResponse(request=req, name="home.html", context=view_data)


@app.get("/about")
async def get_about(req: Request):
    view_data = dict()
    view_data["project_version"] = ConfigService.project_version()
    return views.TemplateResponse(request=req, name="about.html", context=view_data)


@app.get("/sample_queries")
async def get_sample_queries(req: Request):
    return SampleQueries.read_queries()


# ---


@app.get("/query_console")
async def get_query_console(req: Request):
    view_data = query_console_view_data()
    return views.TemplateResponse(
        request=req, name="query_console.html", context=view_data
    )


@app.post("/query_console")
async def post_query_console(req: Request):
    global POOL
    form_data = await req.form()
    logging.info("/query_console form_data: {}".format(form_data))
    query_text = form_data.get("query_text").strip()
    view_data = query_console_view_data(query_text)
    qrp = QueryResultParser()

    if len(query_text) > 10:
        logging.info("query_console - query_text: {}".format(query_text))
        results_tuples: list[str] = list()
        result_objects = list()
        start_time = time.time()
        try:
            conn_str = get_database_connection_string()
            async with await psycopg.AsyncConnection.connect(
                conn_str, autocommit=True
            ) as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute(
                        'SET search_path = "$user", ag_catalog, public;'
                    )
                    stmt = query_text.replace("\r\n", "")
                    logging.info("query_console - stmt: {}".format(stmt))

                    # odd logic here to warmup the cursor to load the extension, set path, etc
                    try:
                        await cursor.execute(stmt)
                    except Exception as e0:
                        pass

                    await cursor.execute(stmt)
                    logging.info("query_console - stmt executed")

                    async for row in cursor:
                        logging.info(
                            "row: {} {} {}".format(len(row), str(type(row)), row)
                        )
                        result_objects.append(qrp.parse(row))
                        results_tuples.append(str(row))
                    view_data["elapsed"] = "elapsed: {}".format(
                        time.time() - start_time
                    )
                    view_data["results_message"] = "Results as JSON and python tuples:"
                    view_data["results"] = "\n".join(results_tuples)
                    view_data["query_text"] = query_text
                    view_data["json_results"] = json.dumps(
                        result_objects, sort_keys=False, indent=2
                    )
                    write_query_results_to_file(view_data, result_objects)
        except Exception as e:
            logging.critical((str(e)))
            view_data["results_message"] = "Error:"
            view_data["results"] = str(e)
            view_data["query_text"] = query_text

    return views.TemplateResponse(
        request=req, name="query_console.html", context=view_data
    )


def write_query_results_to_file(view_data, result_objects):
    """
    Write the query results to a JSON file for visual inspection.
    """
    try:
        fs_data = dict()
        fs_data["query_text"] = view_data["query_text"]
        fs_data["results_message"] = view_data["results_message"]
        fs_data["elapsed"] = view_data["elapsed"]
        fs_data["result_objects"] = result_objects
    except Exception as e2:
        logging.warning(str(e2))
        logging.warning(traceback.format_exc())
    FS.write_json(fs_data, "tmp/query_{}.json".format(int(time.time())))


def query_console_view_data(query_text=""):
    """
    Return an initial dict with all fields necessary for the
    query_console.html view.
    """
    view_data = dict()
    queries = SampleQueries.read_queries()
    view_data["sample_queries"] = queries
    view_data["query_text"] = query_text
    view_data["results_message"] = ""
    view_data["results"] = ""
    view_data["json_results"] = ""
    view_data["elapsed"] = ""
    return view_data


# ---


@app.get("/vector_search_console")
async def get_vector_search_console(req: Request):
    view_data = vector_search_view_data()
    return views.TemplateResponse(
        request=req, name="vector_search_console.html", context=view_data
    )


@app.post("/vector_search_console")
async def post_vector_search_console(req: Request):
    form_data = await req.form()
    logging.info("/vector_search_console form_data: {}".format(form_data))
    search_text = form_data.get("search_text")
    embedding = None
    logging.debug("vector_search_console - search_text: {}".format(search_text))
    view_data = vector_search_view_data(search_text)
    results_obj = dict()

    # First, get the embedding - either from the DB or from the AI service
    if search_text.startswith("text:"):
        text = search_text[5:]
        logging.info(f"post_vector_search_console; text: {text}")
        try:
            logging.info("vectorize: {}".format(text))
            ai_svc = AiService()
            ai_svc_resp = ai_svc.generate_embeddings(text)
            embedding = ai_svc_resp.data[0].embedding
        except Exception as e:
            view_data["results_message"] = "Error calling the AiService: {}".format(
                str(e)
            )
            logging.critical((str(e)))
            logging.exception(e, stack_info=True, exc_info=True)
    else:
        # Lookup the given library in the libraries table, and get its embedding
        try:
            words = search_text.strip().split()
            if len(words) > 0:
                libname = words[0]
                embedding = await lookup_library_embedding(libname)
        except Exception as e:
            view_data["results_message"] = "Error reading the database; {}".format(
                str(e)
            )
            logging.critical((str(e)))
            logging.exception(e, stack_info=True, exc_info=True)

    # Next, execute the vector search vs the DB using the embedding
    if embedding is not None:
        view_data["embedding_message"] = "Embedding, {} dimensions:".format(
            len(embedding)
        )
        view_data["embedding"] = json.dumps(embedding, sort_keys=False, indent=2)
        results_list = await execute_vector_search(embedding)
        view_data["results_message"] = "Vector Search Results, {} rows:".format(
            len(results_list)
        )
        view_data["results"] = json.dumps(results_list, sort_keys=False, indent=2)
    else:
        view_data["embedding_message"] = "No embedding found or created"
        view_data["embedding"] = ""
        view_data["results"] = ""

    return views.TemplateResponse(
        request=req, name="vector_search_console.html", context=view_data
    )


def vector_search_view_data(search_text="flask"):
    """Return an initial dict with the fields necessary for the vector_search_console.html view."""
    view_data = dict()
    view_data["search_text"] = search_text
    view_data["results_message"] = ""
    view_data["results"] = ""
    view_data["embedding_message"] = ""
    view_data["embedding"] = ""
    return view_data


async def lookup_library_embedding(libname) -> list[float] | None:
    """Lookup the given library in the libraries table, and get its embedding."""
    embedding = None
    try:
        conn_str = get_database_connection_string()
        async with await psycopg.AsyncConnection.connect(
            conn_str, autocommit=True
        ) as conn:
            async with conn.cursor() as cursor:
                sql = "select id, embedding from libraries where name = '{}' offset 0 limit 1".format(
                    libname
                )
                await cursor.execute(sql)
                async for row in cursor:
                    embedding = json.loads(
                        row[1]
                    )  # column 0 is the id, column 1 is the embedding
                    logging.info(
                        "lookup_library_embedding; embedding: {}".format(
                            str(type(embedding))
                        )
                    )
    except Exception as e:
        logging.critical((str(e)))
        logging.exception(e, stack_info=True, exc_info=True)
    return embedding


def libraries_vector_search_sql(embeddings, limit=10):
    return (
        """
select name, keywords, description
 from libraries
 order by embedding <-> '{}'
 offset 0 limit 10;
    """.format(
            embeddings
        )
        .replace("\n", " ")
        .strip()
    )


async def execute_vector_search(embedding) -> list:
    """Execute a vector search with the given embedding value."""
    result_list = list()
    try:
        conn_str = get_database_connection_string()
        sql = libraries_vector_search_sql(embedding)
        # async with POOL.connection() as conn:
        async with await psycopg.AsyncConnection.connect(
            conn_str, autocommit=True
        ) as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(sql)
                async for row in cursor:
                    result_list.append(row)
    except Exception as e:
        logging.critical((str(e)))
        logging.exception(e, stack_info=True, exc_info=True)
    return result_list


# ---


@app.get("/opencypher_gen_console")
async def get_opencypher_gen_console(req: Request):
    view_data = opencypher_gen_console_view_data()
    return views.TemplateResponse(
        request=req, name="opencypher_gen_console.html", context=view_data
    )


@app.post("/opencypher_gen_console")
async def post_opencypher_gen_console(req: Request):
    form_data = await req.form()
    logging.info("/opencypher_gen_console form_data: {}".format(form_data))
    view_data = opencypher_gen_console_view_data()
    natural_language = form_data.get("natural_language")
    cypher = form_data.get("cypher")

    if natural_language is not None:
        view_data["natural_language"] = natural_language
        # TODO - call the AI service to generate the Cypher

    elif cypher is not None:
        view_data["cypher"] = cypher
        # TODO - execute the given cypher query

    return views.TemplateResponse(
        request=req, name="opencypher_gen_console.html", context=view_data
    )


def opencypher_gen_console_view_data(query_text=""):
    """
    Return an initial dict with all fields necessary for the
    opencypher_gen_console.html view.
    """
    view_data = dict()
    view_data["natural_language"] = ""
    view_data["cypher"] = ""
    view_data["results_message"] = ""
    view_data["results"] = ""
    view_data["elapsed"] = ""
    return view_data
