"""
Usage:
    python main.py log_defined_env_vars
    python main.py list_pg_extensions_and_settings
    python main.py delete_define_libraries_table
    python main.py delete_define_libraries2_table
    python main.py delete_define_airports_table
    python main.py load_libraries_table
    python main.py create_libraries_table_vector_index sql/libraries_ivfflat_index.sql
    python main.py vector_search_similar_libraries flask 10
    python main.py vector_search_words word1 word2 word3 etc
    python main.py vector_search_words running calculator miles kilometers pace speed mph
    python main.py load_age_graph ../data/cypher/us_openflights.txt
    python main.py load_age_graph ../data/cypher/libraries.txt
Options:
  -h --help     Show this screen.
  --version     Show version.
"""

import asyncio
import json
import logging
import os
import sys
import traceback

import psycopg
import psycopg_pool

from docopt import docopt
from dotenv import load_dotenv

from src.services.ai_service import AiService
from src.services.config_service import ConfigService
from src.services.logging_level_service import LoggingLevelService

from src.util.fs import FS

logging.basicConfig(
    format="%(asctime)s - %(message)s", level=LoggingLevelService.get_level()
)


def print_options(msg):
    """
    Use the docopt python library to display the script
    usage comments at the top of this module.
    """
    print("{} {}".format(os.path.basename(__file__), msg))
    arguments = docopt(__doc__, version="1.0.0")
    print(arguments)


def log_defined_env_vars():
    """
    Log to the console the set of environment variables that are
    defined in class ConfigService.
    """
    logging.info("log_defined_env_vars")
    ConfigService.log_defined_env_vars()


def get_pg_connection_str():
    """
    Create and return the connection string for your Azure
    PostgreSQL database per the AIG4PG_xxx environment variables.
    """
    db = ConfigService.postgresql_database()
    user = ConfigService.postgresql_user()
    password = ConfigService.postgresql_password()
    host = ConfigService.postgresql_server()
    port = ConfigService.postgresql_port()
    return "host={} port={} dbname={} user={} password={} ".format(
        host, port, db, user, password
    )


async def initialze_pool() -> psycopg_pool.AsyncConnectionPool:
    """
    Create and open a psycopg_pool.AsyncConnectionPool
    which is used throughout this module.
    """
    logging.info("initialze_pool...")
    conn_str = get_pg_connection_str()
    conn_str_tokens = conn_str.split("password")
    logging.info(
        "initialze_pool, conn_str: {} password=<omitted>".format(conn_str_tokens[0])
    )
    pool = psycopg_pool.AsyncConnectionPool(conninfo=conn_str, open=False)
    logging.info("initialze_pool, pool created: {}".format(pool))
    await pool.open()
    await pool.check()
    logging.info("initialze_pool, pool opened")
    return pool


async def close_pool(pool):
    """
    Close the psycopg_pool.AsyncConnectionPool.
    """
    if pool is not None:
        logging.info("close_pool, closing...")
        await pool.close()
        logging.info("close_pool, closed")


async def execute_query(pool, sql) -> list:
    """
    Execute the given SQL query and return the results
    as a list of tuples.
    """
    results_list = list()
    async with pool.connection() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute(sql)
            results = await cursor.fetchall()
            for row in results:
                results_list.append(row)
    return results_list


async def list_pg_extensions_and_settings(pool: psycopg_pool.AsyncConnectionPool):
    """
    Query several tables such as pg_extension, and
    pg_available_extensions and display the resulting rows.
    """
    queries = list()
    queries.append("SELECT * FROM pg_extension")
    queries.append("SELECT * FROM pg_available_extensions")
    # queries.append("SELECT * FROM pg_settings")

    for query in queries:
        rows = await execute_query(pool, query)
        for row in rows:
            logging.info(row)


async def delete_define_table(
        pool: psycopg_pool.AsyncConnectionPool,
        ddl_filename: str,
        tablename: str):

    ddl = FS.read(ddl_filename)
    logging.info(ddl)

    async with pool.connection() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute(ddl)

    validation_queries = list()
    validation_queries.append(
        "select * FROM information_schema.tables WHERE table_schema='public';"
    )
    validation_queries.append(
        "SELECT column_name, data_type, character_maximum_length FROM information_schema.columns WHERE table_name = '{}';".format(
            tablename)
    )
    for validation_query in validation_queries:
        logging.info("==========")
        logging.info("validation_query: {}".format(validation_query))
        rows = await execute_query(pool, validation_query)
        for row in rows:
            logging.info(row)

async def load_libraries_table(pool: psycopg_pool.AsyncConnectionPool):
    data_dir = "../data/pypi/wrangled_libs"
    logging.info("load_libraries_table, data_dir: {}".format(data_dir))
    files_list = FS.list_files_in_dir(data_dir)
    filtered_files_list = filter_files_list(files_list, ".json")
    rows_loaded_count, exceptions_count = 0, 0

    logging.info("data files count: {}".format(len(filtered_files_list)))

    async with pool.connection() as conn:
        async with conn.cursor() as cursor:
            for file_idx, data_filename in enumerate(filtered_files_list):
                fq_filename = None
                try:
                    fq_filename = "{}/{}".format(data_dir, data_filename)
                    logging.info("data_file {}: {}".format(file_idx, fq_filename))
                    doc = FS.read_json(fq_filename)
                    sql = build_insert_library_sql(doc)
                    if sql is not None:
                        await cursor.execute("BEGIN transaction;")
                        await cursor.execute(sql)
                        await cursor.execute("COMMIT transaction;")
                        rows_loaded_count = rows_loaded_count + 1
                except Exception as e:
                    exceptions_count = exceptions_count + 1
                    logging.error("Error processing file: {}".format(fq_filename))
                    logging.info(str(e))
                    await cursor.execute("ROLLBACK transaction;")

    logging.info(
        "load_libraries_table, rows_loaded_count: {}".format(rows_loaded_count)
    )
    logging.info("load_libraries_table, exceptions_count:  {}".format(exceptions_count))


def filter_files_list(files_list, suffix):
    filtered = list()
    for f in files_list:
        if f.endswith(suffix):
            filtered.append(f)
    return filtered


def build_insert_library_sql(doc) -> str | None:
    try:
        sql_parts = list()
        sql_parts.append("INSERT INTO libraries (")
        sql_parts.append(",".join(libraries_column_names(False)))
        sql_parts.append(") ")
        sql_parts.append("VALUES (")
        sql_parts.append(quoted_attr_value(doc, "name"))
        sql_parts.append(",")
        sql_parts.append(quoted_attr_value(doc, "libtype"))
        sql_parts.append(",")
        sql_parts.append(quoted_attr_value(doc, "description"))
        sql_parts.append(",")
        sql_parts.append(quoted_attr_value(doc, "keywords"))
        sql_parts.append(",")
        sql_parts.append(quoted_attr_value(doc, "license"))
        sql_parts.append(",")
        sql_parts.append(str(doc["release_count"]))
        sql_parts.append(",")
        sql_parts.append(quoted_attr_value(doc, "package_url"))
        sql_parts.append(",")
        sql_parts.append(quoted_attr_value(doc, "project_url"))
        sql_parts.append(",")
        sql_parts.append(quoted_attr_value(doc, "docs_url"))
        sql_parts.append(",")
        sql_parts.append(quoted_attr_value(doc, "release_url"))
        sql_parts.append(",")
        sql_parts.append(quoted_attr_value(doc, "requires_python"))
        sql_parts.append(",")
        sql_parts.append(quoted_attr_value(doc, "classifiers", True))
        sql_parts.append(",")
        sql_parts.append(quoted_attr_value(doc, "project_urls", True))
        sql_parts.append(",")
        sql_parts.append(quoted_attr_value(doc, "developers", True))
        sql_parts.append(",")
        sql_parts.append(quoted_attr_value(doc, "embedding", True))
        sql_parts.append(");")
        return "".join(sql_parts)
    except Exception as e:
        logging.info(str(e))
        logging.info(traceback.format_exc())
        return None


def quoted_attr_value(doc, attr, jsonb=False):
    if attr in doc.keys():
        if jsonb:
            return "'{}'".format(json.dumps(doc[attr]))
        else:
            return "'{}'".format(str(doc[attr]).replace("'", ""))
    else:
        if attr == "embedding":
            return "[]"
        else:
            return "'?'"


def libraries_column_names(include_id=True):
    names = list()
    if include_id == True:
        names.append("id")
    names.append("name")
    names.append("libtype")
    names.append("description")
    names.append("keywords")
    names.append("license")
    names.append("release_count")
    names.append("package_url")
    names.append("project_url")
    names.append("docs_url")
    names.append("release_url")
    names.append("requires_python")
    names.append("classifiers")
    names.append("project_urls")
    names.append("developers")
    names.append("embedding")
    return names


async def create_libraries_table_vector_index(
    pool: psycopg_pool.AsyncConnectionPool, index_filename
):
    # See https://learn.microsoft.com/en-us/azure/postgresql/flexible-server/how-to-optimize-performance-pgvector#indexing

    logging.info(
        "create_libraries_table_vector_index, index_filename: {}".format(index_filename)
    )
    ddl = FS.read(index_filename)
    logging.info(ddl)

    if True:
        async with pool.connection() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(ddl)

    validation_queries = list()
    validation_queries.append("select * FROM pg_indexes WHERE tablename = 'libraries';")
    for validation_query in validation_queries:
        logging.info("==========")
        logging.info("validation_query: {}".format(validation_query))
        rows = await execute_query(pool, validation_query)
        for row in rows:
            logging.info(row)


async def vector_search_similar_libraries(
    pool: psycopg_pool.AsyncConnectionPool, libname: str, count: int
):
    """
    First execute a traditional SELECT to find the given library.
    Then use its embedding to find the other similar libraries via a vector search query.
    """
    logging.info(
        "vector_search_similar_libraries, library_name: {}, count: {}".format(
            libname, count
        )
    )
    sql = "select id, name, embedding from libraries where name = '{}' limit 1;".format(
        libname
    )
    logging.info(sql)

    results = await execute_query(pool, sql)
    if (results is not None) and (len(results) > 0):
        embedding = results[0][2]
        sql = vector_query_sql(embedding, count)
        results = await execute_query(pool, sql)
        for row in results:
            logging.info(row)
    else:
        logging.info("No results found for library: {}".format(libname))


def vector_query_sql(embedding, count):
    return """
select id, name, keywords
from  libraries
order by embedding <-> '{}'
limit {};
    """.format(
        embedding, count
    ).strip()


async def vector_search_words(pool: psycopg_pool.AsyncConnectionPool):

    words = sys.argv[2:]
    logging.info("vector_search_words: {}".format(words))
    # await asyncio.sleep(0.1)
    try:
        # Call Azure OpenAI to generate an embedding for the given CLI words.
        embedding = None
        ai_svc = AiService()
        resp = ai_svc.generate_embeddings(" ".join(words))
        embedding = resp.data[0].embedding
        if (embedding is not None) and (len(embedding) == 1536):
            sql = vector_query_sql(embedding, 12)
            results = await execute_query(pool, sql)
            for row in results:
                logging.info(row)
    except Exception as e:
        logging.critical(str(e))


async def load_age_graph(pool: psycopg_pool.AsyncConnectionPool, infile: str):
    cypher_statements = FS.read_lines(infile)
    print("cypher_statements read; count: {}".format(len(cypher_statements)))

    # SET search_path = ag_catalog, "$user", public;
    # SELECT ag_catalog.create_graph('usair1');
    # SELECT * FROM ag_catalog.ag_graph;

    async with pool.connection() as conn:
        async with conn.cursor() as cursor:
            for idx, sql in enumerate(cypher_statements):
                try:
                    if idx == 0:
                        set_path = set_age_search_path_sql()
                        logging.info("setting path: {}".format(set_path))
                        await cursor.execute("BEGIN transaction;")
                        await cursor.execute(set_path)
                        await cursor.execute("COMMIT transaction;")
                        logging.info("path set, awaiting 10 seconds...")
                        await asyncio.sleep(10)
                    print("executing: {} {}".format(idx, sql))
                    await cursor.execute("BEGIN transaction;")
                    await cursor.execute(sql)
                    await cursor.execute("COMMIT transaction;")
                    print("ok: {} {}".format(idx, sql))
                except Exception as e:
                    logging.error("Error processing idx: {} sql: {}".format(idx, sql))
                    logging.info(str(e))
                    await cursor.execute("ROLLBACK transaction;")


async def load_age_graph_libraries(pool: psycopg_pool.AsyncConnectionPool, infile: str):
    cypher_statements = FS.read_json(infile)
    for cypher in cypher_statements:
        sql = cypher_sql("g1", cypher)
        print(sql)

    async with pool.connection() as conn:
        async with conn.cursor() as cursor:
            for idx, cypher_stmt in enumerate(cypher_statements):
                if idx < 3:
                    sql = None
                    try:
                        logging.info("idx: {}, cypher_stmt {}".format(idx, cypher_stmt))
                        sql = cypher_sql("g1", cypher_stmt)
                        print(sql)
                        if True:
                            await cursor.execute("BEGIN transaction;")
                            await cursor.execute(sql)
                            await cursor.execute("COMMIT transaction;")
                    except Exception as e:
                        logging.error("Error processing sql: {}".format(sql))
                        logging.info(str(e))
                        await cursor.execute("ROLLBACK transaction;")


def set_age_search_path_sql():
    return 'SET search_path = ag_catalog, "$user", public;'


async def example_async_method(pool: psycopg_pool.AsyncConnectionPool):
    await asyncio.sleep(0.1)


async def async_main():
    """
    This is the asyncronous main logic, called from the entry point
    of this module with "asyncio.run(async_main())".

    This project chose to demonstrate asyncronous programming
    rather than synchronous programming as it is more performant
    and production-oriented.
    """
    try:
        pool = await initialze_pool()
        if len(sys.argv) < 2:
            print_options("- no command-line args given")
        else:
            func = sys.argv[1].lower()
            logging.info("func: {}".format(func))
            if func == "log_defined_env_vars":
                log_defined_env_vars()
            elif func == "list_pg_extensions_and_settings":
                await list_pg_extensions_and_settings(pool)

            elif func == "delete_define_libraries_table":
                await delete_define_table(
                    pool, "sql/libraries_ddl.sql", "libraries")
            elif func == "delete_define_libraries2_table":
                await delete_define_table(
                    pool, "sql/libraries2_ddl.sql", "libraries2")
            elif func == "delete_define_airports_table":
                await delete_define_table(
                    pool, "sql/airports_ddl.sql", "airports")
                
            elif func == "load_libraries_table":
                await load_libraries_table(pool)
            elif func == "create_libraries_table_vector_index":
                index_filename = sys.argv[2].lower()
                await create_libraries_table_vector_index(pool, index_filename)
            elif func == "vector_search_similar_libraries":
                library_name = sys.argv[2].lower()
                count = int(sys.argv[3])
                await vector_search_similar_libraries(pool, library_name, count)
            elif func == "vector_search_words":
                library_name = sys.argv[2].lower()
                await vector_search_words(pool)
            elif func == "load_age_graph":
                infile = sys.argv[2]
                await load_age_graph(pool, infile)
            else:
                print_options("- unknown command-line arg: {}".format(func))
    except Exception as e:
        logging.critical(str(e))
        logging.exception(e, stack_info=True, exc_info=True)
        logging.error("Stack trace:\n%s", traceback.format_exc())

    finally:
        if pool is not None:
            logging.info("closing pool...")
            await pool.close()
            logging.info("pool closed")


if __name__ == "__main__":
    load_dotenv(override=True)
    if os.name.lower() != "nt":
        logging.info("Not running on Windows")
    else:
        logging.info("Running on Windows, setting WindowsSelectorEventLoopPolicy")
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(async_main())
