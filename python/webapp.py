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

    if len(query_text) > 10:
        logging.info("query_console - query_text: {}".format(query_text))
        results_list : list[str] = list()
        result_objects : list[dict] = list()
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
                        print("row: {} {} {}".format(row, len(row), str(type(row))))
                        result_objects.append(row)
                        results_list.append(str(row))
                    view_data["elapsed"] = "elapsed: {}".format(time.time() - start_time)
                    view_data["results_message"] = "Results:"
                    view_data["results"] = "\n".join(results_list)
                    view_data["query_text"] = query_text
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
# TODO - extract this logic to a util class

# 2024-11-14 16:38:39,677 - query_console - stmt: SELECT oid, extname, extversion FROM pg_extension;
# 2024-11-14 16:38:39,723 - query_console - stmt executed
# row: (14258, 'plpgsql', '1.0') 3 <class 'tuple'>
# row: (24760, 'vector', '0.7.0') 3 <class 'tuple'>
# row: (25081, 'age', '1.5.0') 3 <class 'tuple'>

# 2024-11-14 16:39:42,516 - query_console - stmt: SELECT * FROM ag_catalog.ag_graph;
# 2024-11-14 16:39:42,562 - query_console - stmt executed
# row: (106293, 'libraries1', 'libraries1') 3 <class 'tuple'>

# 2024-11-14 16:40:30,189 - query_console - stmt: select count(*) from libraries;
# 2024-11-14 16:40:30,235 - query_console - stmt executed
# row: (10761,) 1 <class 'tuple'>

# 2024-11-14 16:41:43,236 - query_console - stmt: select id, name, keywords from libraries limit 3
# 2024-11-14 16:41:43,289 - query_console - stmt executed
# row: (1, '2captcha-python', '') 3 <class 'tuple'>
# row: (2, '2to3', '2to3') 3 <class 'tuple'>
# row: (3, 'a2wsgi', '') 3 <class 'tuple'>

# 2024-11-14 16:42:22,834 - query_console - stmt: SELECT * FROM ag_catalog.cypher('libraries1',  $$ MATCH (n) RETURN count(n) as count $$)  as (v agtype);
# 2024-11-14 16:42:22,905 - query_console - stmt executed
# row: ('21312',) 1 <class 'tuple'>

# 2024-11-14 16:42:51,439 - query_console - stmt: SELECT * FROM ag_catalog.cypher('libraries1',  $$ MATCH (dev:Developer) RETURN dev limit 10 $$)  as (v agtype);
# 2024-11-14 16:42:51,487 - query_console - stmt executed
# row: ('{"id": 844424930131969, "label": "Developer", "properties": {"name": "info@2captcha.com"}}::vertex',) 1 <class 'tuple'>
# row: ('{"id": 844424930131970, "label": "Developer", "properties": {"name": "xoviat"}}::vertex',) 1 <class 'tuple'>

# row: ('[{"id": 1407374883553290, "label": "uses_lib", "end_id": 1125899906851581, "start_id": 1125899906842630, "properties": {}}::edge, {"id": 1407374883587559, "label": "uses_lib", "end_id": 1125899906851227, "start_id": 1125899906851581, "properties": {}}::edge, {"id": 1407374883586028, "label": "uses_lib", "end_id": 1125899906853118, "start_id": 1125899906851227, "properties": {}}::edge, {"id": 1407374883592102, "label": "uses_lib", "end_id": 1125899906851227, "start_id": 1125899906853118, "properties": {}}::edge, {"id": 1407374883586023, "label": "uses_lib", "end_id": 1125899906850362, "start_id": 1125899906851227, "properties": {}}::edge]',) 1 <class 'tuple'>
    try:
        # write the results to a tmp file for visual inspection
        fs_data, json_rows = dict(), list()
        fs_data["query_text"] = view_data["query_text"]
        fs_data["results_message"] = view_data["results_message"]
        fs_data["elapsed"] = view_data["elapsed"]
        fs_data["json_objects"] = []
        fs_data["result_objects"] = result_objects

        for t in result_objects:
            # t is a tup in various forms per the query
            json_row = list()
            json_rows.append(json_row)
            if type(t) == tuple:
                for elem in t:
                    if isinstance(elem, str):
                        if "::" in elem:
                            jstr = elem.split("::")[0].strip()
                            obj = json.loads(elem.split("::")[0])
                            print("obj: {} {}".format(obj, type(obj)))
                            json_row.append(obj)
                        else:
                            json_row.append(elem)
                    else:
                        json_row.append(elem)
            else:
                json_row.append(elem)
        fs_data["json_objects"] = json_rows
    except Exception as e2:
        logging.warning(str(e2))
        logging.warning(traceback.format_exc())
    FS.write_json(fs_data, "tmp/search_{}.json".format(int(time.time())))


def query_console_view_data(query_text=""):
    """
    Return an initial dict with the fields necessary for the
    query_console.html view.
    """
    view_data = dict()
    queries = SampleQueries.read_queries()
    view_data["sample_queries"] = queries
    view_data["query_text"] = query_text
    view_data["results_message"] = ""
    view_data["results"] = ""
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
