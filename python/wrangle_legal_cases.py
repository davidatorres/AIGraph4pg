"""
Usage:
    python wrangle_legal_cases.py wrangle_step1 <cases-sql-infile>
    python wrangle_legal_cases.py wrangle_step1 /Users/cjoakim/Downloads/cases.sql
    python wrangle_legal_cases.py wrangle_step2 <iterations>
    python wrangle_legal_cases.py wrangle_step2 10
    python wrangle_legal_cases.py wrangle_step3 <infile>
    python wrangle_legal_cases.py wrangle_step3 tmp/iteration_5.json
Options:
  -h --help     Show this screen.
  --version     Show version.
"""

import asyncio
import json
import logging
import os
import sys
import time
import traceback

import psycopg_pool

from docopt import docopt
from dotenv import load_dotenv

from src.services.ai_service import AiService
from src.services.config_service import ConfigService
from src.services.logging_level_service import LoggingLevelService

from src.util.cite_parser import CiteParser
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


def wrangle_step1(cases_sql_infile: str):
    """
    Read the cases.sql file, parse the JSON in each line, and calculate
    each case url and its citations.  
    """
    infile = "/Users/cjoakim/Downloads/cases.sql"
    print("wrangle_step1, reading infile: {}".format(cases_sql_infile))
    data_lines_read, json_parse_ok, json_parse_fail = 0, 0, 0
    case_id_name_dict = dict()  # key is the case id, value is the case name
    seeds = initial_seeds()
    start_time = time.time()

    if len(seeds.keys()) < 7:
        print("Error: seeds length: {}".format(len(seeds)))
        return
    print("seeds: {} {}".format(len(seeds), sorted(seeds.keys())))

    with open(cases_sql_infile, "r", encoding='ISO-8859-1') as file:  # cp1252 is the default encoding for Windows.  ISO-8859-1
        for line in file:
            stripped = line.strip()
            if len(stripped) > 10:
                tokens = stripped.split("\t")
                if len(tokens) == 3:
                    try:
                        data_lines_read = data_lines_read + 1
                        if data_lines_read < 999999:
                            if data_lines_read % 1000 == 0:
                                print("data lines read: {}".format(data_lines_read))
                            id, json_str, embeddings = tokens[0].strip(), tokens[1].strip(), tokens[2].strip()
                            try:
                                case_doc = json.loads(json_str)
                                json_parse_ok = json_parse_ok + 1
                                id = str(case_doc['id'])
                                calculate_url(case_doc)
                                collect_cites_to(case_doc)
                                metadata = dict()
                                metadata['id'] = id
                                metadata['name_abbreviation'] = case_doc['name_abbreviation']
                                metadata['__case_url'] = case_doc['__case_url']
                                metadata['__citations'] = case_doc['__citations']
                                case_id_name_dict[id] = metadata
                                # Write the original seed documents to better understand the data
                                if id in seeds.keys():
                                    outfile = "tmp/{}.json".format(id)
                                    FS.write_json(case_doc, outfile)
                            except Exception as jpe:
                                json_parse_fail = json_parse_fail + 1
                    except Exception as e:
                        print("Exception: {}".format(e))
                        print(traceback.format_exc())
                        print("Exception line {} {} tokens: {} prefix: |{}|".format(
                            data_lines_read, len(stripped), len(tokens), stripped[0:40]))


    elapsed_time = time.time() - start_time
    print("data lines read: {}".format(data_lines_read))
    print("elapsed time: {} seconds".format(elapsed_time))
    print("json_parse_ok: {} json_parse_fail: {}".format(json_parse_ok, json_parse_fail))

    FS.write_json(case_id_name_dict, 'tmp/case_id_name_dict.json')
    print("case_id_name_dict size: {}".format(len(case_id_name_dict.keys())))

    # flip the above case_id_name_dict to use the '__case_url' as the key
    case_url_dict = dict()
    for id in case_id_name_dict.keys():
        metadata = case_id_name_dict[id]
        case_url = metadata['__case_url']
        case_url_dict[case_url] = metadata
    FS.write_json(case_url_dict, 'tmp/case_url_dict.json')
    print("case_url_dict size: {}".format(len(case_url_dict.keys())))


def initial_seeds():
    infile = "../data/legal_cases/case_seeds_edited.txt"
    lines = FS.read_lines(infile)
    seeds = dict()
    for line in lines:
        tokens = line.split("|")
        if len(tokens) > 1:
            id = tokens[0].strip()
            seeds[id] = tokens[1].strip()
    return seeds

def calculate_url(case_doc):
    """
    Calculate the url for the case document like:
    https://static.case.law/wash/184/cases/0560-01.json
    Populate the '__case_url' in the given case_doc.
    """
    try:
        url_key = '__case_url'
        case_doc[url_key] = '?'
        if 'file_name' in case_doc.keys():  # this is expected
            file_name = case_doc['file_name'].strip()
            if 'citations' in case_doc.keys():
                cite = case_doc['citations'][0]['cite']
                cite_parser = CiteParser()
                url = cite_parser.parse(cite, file_name)
                if url is not None:
                    case_doc[url_key] = url
    except Exception as e:
        pass


def collect_cites_to(case_doc):
    citations = list()
    citations_key = "__citations"
    case_doc[citations_key] = citations
    cite_parser = CiteParser()

    try:
        for citation in case_doc['cites_to']:
            cite = citation['cite']
            url = cite_parser.parse(cite, None)
            if url is not None:
                citations.append(url)
    except Exception as e:
        pass

def wrangle_step2(iteration_count: int):
    print("wrangle_step2, iteration_count: {}".format(iteration_count))

    case_id_name_dict = FS.read_json('tmp/case_id_name_dict.json')
    case_url_dict = FS.read_json('tmp/case_url_dict.json')
    collected_metadata = dict()

    for n in range(iteration_count):
        print("iteration: {}".format(n))
        if n == 0:
            seeds = initial_seeds()
            for seed in seeds:
                print("seed: {}".format(seed))
                if seed in case_id_name_dict.keys():
                    meta = case_id_name_dict[seed]
                    meta['iteration'] = n
                    meta['citations_gathered'] = 1
                    url = meta['__case_url']
                    collected_metadata[url] = meta
                    for url in meta['__citations']:
                        if url not in collected_metadata.keys():
                            if url in case_url_dict.keys():
                                citation_meta = case_url_dict[url]
                                citation_meta['iteration'] = n + 1
                                citation_meta['citations_gathered'] = 0  # not yet gathered
                                collected_metadata[url] = citation_meta
        else:
            for collected_url in collected_metadata.keys():
                print("collected_url: {}".format(collected_url))


def wrangle_step3(infile:str):
    print("wrangle_step3, reading infile: {}".format(infile))




if __name__ == "__main__":
    load_dotenv(override=True)
    logging.basicConfig(
        format="%(asctime)s - %(message)s", level=LoggingLevelService.get_level()
    )
    #ConfigService.log_defined_env_vars()

    if len(sys.argv) < 2:
        print_options("Error: invalid command-line")
        exit(1)
    else:
        try:
            func = sys.argv[1].lower()
            if func == "wrangle_step1":
                cases_sql_infile = sys.argv[2]
                wrangle_step1(cases_sql_infile)
            elif func == "wrangle_step2":
                iteration_count = int(sys.argv[2])
                wrangle_step2(iteration_count)
            elif func == "wrangle_step3":
                infile = sys.argv[2]
                wrangle_step3(infile)
            else:
                print_options("Error: invalid function: {}".format(func))
        except Exception as e:
            logging.critical(str(e))
            logging.exception(e, stack_info=True, exc_info=True)
