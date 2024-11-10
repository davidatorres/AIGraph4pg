#!/bin/bash

python wrangle_openflights.py all_parse_csv_files

python wrangle_openflights.py extract_us_data

python wrangle_openflights.py create_cypher_load_statements
