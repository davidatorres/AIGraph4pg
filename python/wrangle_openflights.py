"""
This program is used for the development of the AIGraph4PG project
and the curation of the OpenFlights dataset. It is not intended for
users of the project.  However, it may provide you and example
of how to transform your raw data into openCypher statements used
to load an Apache AGE graph.
Usage:
    python wrangle_openflights.py all_parse_csv_files
    python wrangle_openflights.py extract_us_data
    python wrangle_openflights.py create_cypher_load_statements
Options:
  -h --help     Show this screen.
  --version     Show version.
"""

import logging
import os
import sys
import traceback
import zipfile

from docopt import docopt
from dotenv import load_dotenv

from src.services.config_service import ConfigService
from src.services.logging_level_service import LoggingLevelService

from src.util.fs import FS
from src.util.template import Template

logging.basicConfig(
    format="%(asctime)s - %(message)s", level=LoggingLevelService.get_level()
)


def print_options(msg):
    print("{} {}".format(os.path.basename(__file__), msg))
    arguments = docopt(__doc__, version="1.0.0")
    print(arguments)


def all_parse_csv_files():
    """
    Read the CSV files, normalize their values, and save as similarly named JSON files.
    """
    logging.info("all_parse_csv_files")
    data_dir = "../data/openflights/"
    data_files = FS.list_files_in_dir(data_dir)
    for file in data_files:
        if file.endswith(".csv"):
            outfile_name = "{}{}".format(data_dir, file.replace(".csv", ".json"))
            outfile_docs = list()
            fq_name = "{}{}".format(data_dir, file)
            print("processing file {}".format(fq_name))
            row_objects = FS.read_csv_as_dicts(fq_name)
            for row in row_objects:
                for key in row.keys():
                    value = row[key]
                    if value == "\\N":
                        row[key] = ""
                outfile_docs.append(row)
                # print(json.dumps(row))
            FS.write_json(outfile_docs, outfile_name)


def extract_us_data():
    """
    Extract the US airports, airlines, and routes from above parsed JSON files.
    """
    all_airports = FS.read_json("../data/openflights/airports.json")
    all_airlines = FS.read_json("../data/openflights/airlines.json")
    all_routes = FS.read_json("../data/openflights/routes.json")
    us_airports = dict()
    us_airlines = dict()
    us_routes = dict()
    print("all_airports: {}".format(len(all_airports)))
    print("all_airlines: {}".format(len(all_airlines)))
    print("all_routes: {}".format(len(all_routes)))

    # collect the US airports into a dict
    for a in all_airports:
        if has_required_fields(
            a,
            "airport_id,name,city,country,iata,latitude,longitude,altitude,tz_offset,tz",
        ):
            if a["country"].lower().strip() == "united states":
                iata = a["iata"]
                if len(iata) > 2:
                    us_airports[iata] = a
    FS.write_json(us_airports, "../data/openflights/us_airports.json")

    # collect the US-to-US routes into a dict, key is source:dest:airline
    for r in all_routes:
        if has_required_fields(
            r, "airline,airline_id,source_airport,dest_airport,stops,equipment"
        ):
            source, dest, airline = r["source_airport"], r["dest_airport"], r["airline"]
            if source in us_airports.keys():
                if dest in us_airports.keys():
                    if len(airline.strip()) > 1:
                        key = "{}:{}:{}".format(source, dest, airline)
                        us_routes[key] = r
                        us_airlines[airline] = dict()  # populate shortly
    FS.write_json(us_routes, "../data/openflights/us_routes.json")

    # collect the above-identified US airlines into a dict
    for a in all_airlines:
        iata = a["iata"]
        if iata in us_airlines.keys():
            us_airlines[iata] = a
    FS.write_json(us_airlines, "../data/openflights/us_airlines.json")

    print("us_airports: {}".format(len(us_airports)))
    print("us_airlines: {}".format(len(us_airlines)))
    print("us_routes: {}".format(len(us_routes)))


def has_required_fields(obj, comma_delim_field_names):
    fields = comma_delim_field_names.split(",")
    if obj is None:
        return False
    else:
        for f in fields:
            if f not in obj.keys():
                return False
            else:
                if len(obj[f]) < 1:
                    return False
    return True


def create_cypher_load_statements():
    airports = FS.read_json("../data/openflights/us_airports.json")
    airlines = FS.read_json("../data/openflights/us_airlines.json")
    routes = FS.read_json("../data/openflights/us_routes.json")
    print("us_airports read: {}".format(len(airports)))
    print("us_airlines read: {}".format(len(airlines)))
    print("us_routes read:   {}".format(len(routes)))
    print("documents read:   {}".format(len(routes) + len(airports) + len(airlines)))
    graphname = "usair1"
    cypher_statements = list()
    # cypher_statements.append('SET search_path = ag_catalog, "$user", public;')

    # jinga2 templates are used here due to the punctuation complexity
    # of the generated SELECT/openCypher statements
    airline_vertex_template = get_template("create_cypher_airline_vertex.txt")
    airport_vertex_template = get_template("create_cypher_airport_vertex.txt")
    route_edge_template = get_template("create_cypher_route_edge.txt")

    for iata in airlines.keys():
        try:
            a = airlines[iata]
            values = dict()
            values["graphname"] = graphname
            values["iata"] = str(a["iata"]).replace("'", "").strip()
            values["name"] = str(a["name"]).replace("'", "").strip()
            values["airline_id"] = str(a["airline_id"]).replace("'", "").strip()
            cypher = Template.render(airline_vertex_template, values)
            cypher_statements.append(cypher.replace("\n", " ").strip())
        except Exception as e:
            print("exception on airline: {}".format(a))
            print(str(e))
            print(traceback.format_exc())

    for iata in airports.keys():
        try:
            a = airports[iata]
            values = dict()
            values["graphname"] = graphname
            values["iata"] = str(a["iata"]).replace("'", "").strip()
            values["name"] = str(a["name"]).replace("'", "").strip()
            values["airport_id"] = str(a["airport_id"]).replace("'", "").strip()
            values["city"] = str(a["city"]).replace("'", "").strip()
            values["country"] = str(a["country"]).replace("'", "").strip()
            values["tz"] = str(a["tz"]).replace("'", "").strip()
            values["tz_offset"] = float(str(a["tz_offset"]).replace("'", "").strip())
            values["latitude"] = float(str(a["latitude"]).replace("'", "").strip())
            values["longitude"] = float(str(a["longitude"]).replace("'", "").strip())
            values["altitude"] = int(str(a["altitude"]).replace("'", "").strip())
            cypher = Template.render(airport_vertex_template, values)
            cypher_statements.append(cypher.replace("\n", " ").strip())
        except Exception as e:
            print("exception on airport: {}".format(a))
            print(str(e))
            print(traceback.format_exc())

    for route_key in sorted(routes.keys()):
        source, dest, airline = route_key.split(":")
        try:
            values = dict()
            values["graphname"] = graphname
            values["iata1"] = str(source).replace("'", "").strip()
            values["iata2"] = str(dest).replace("'", "").strip()
            values["airline"] = str(airline).replace("'", "").strip()
            cypher = Template.render(route_edge_template, values)
            cypher_statements.append(cypher.replace("\n", " ").strip())
        except Exception as e:
            print("exception on airport: {}".format(a))
            print(str(e))
            print(traceback.format_exc())

    try:
        # The output file is large, too large for GitHub, so we write it
        # to a git-ignored tmporary file, then zip it to ../data/cypher/us_openflights.zip
        # for storage in GitHub.  It can be unzipped with 'jar xvf us_openflights.zip'.
        txt_file = "us_openflights.txt"
        zip_file = "../data/cypher/us_openflights.zip"
        FS.write_lines(cypher_statements, txt_file)
        print("cypher statements count: {}".format(len(cypher_statements)))
        with zipfile.ZipFile(zip_file, "w", zipfile.ZIP_DEFLATED) as z:
            z.write(txt_file)
    except Exception as e:
        logging.error("error creating output file or zip file")
        logging.critical(str(e))
        logging.exception(e, stack_info=True, exc_info=True)

    # us_airports read: 1132
    # us_airlines read: 71
    # us_routes read:   10471
    # documents read:   11674
    # 2024-11-05 16:09:34,084 - file written: us_openflights.txt
    # cypher statements count: 11674


def get_template(template_name):
    return Template.get_template(os.getcwd(), template_name)


if __name__ == "__main__":
    load_dotenv(override=True)

    if len(sys.argv) < 2:
        print_options("- no command-line args given")
        exit(1)
    else:
        try:
            func = sys.argv[1].lower()
            if func == "all_parse_csv_files":
                all_parse_csv_files()
            elif func == "extract_us_data":
                extract_us_data()
            elif func == "create_cypher_load_statements":
                create_cypher_load_statements()
            else:
                print_options("- error - invalid function: {}".format(func))
        except Exception as e:
            logging.critical(str(e))
            logging.exception(e, stack_info=True, exc_info=True)
