import csv
import json
import logging
import os
import traceback

from typing import Iterator


from src.util.sample_query import SampleQuery
from src.util.fs import FS

# This class reads file "config/sample_queries.txt" and
# returns a list of the parsed queries.  This is used in
# the UI to get the query text from a selected query name.
# Chris Joakim, Microsoft


class SampleQueries:

    @classmethod
    def read_queries(cls, filename="config/sample_queries.txt") -> list[SampleQuery]:
        """
        Read and parse the sample_queries.txt file and return
        a list of SampleQuery objects.
        """
        queries, in_text = list(), 0
        try:
            lines = FS.read_lines(filename)
            logging.warning(
                "SampleQueries#read_queries {} lines read from {}".format(
                    len(lines), filename
                )
            )
            curr_query = SampleQuery()
            for line in lines:
                stripped, rstripped = line.strip(), line.rstrip()

                if stripped == "":  # skip blank lines
                    pass
                elif stripped.startswith("#"):  # skip comment lines
                    pass
                elif rstripped.startswith("--name "):
                    curr_query.set_name(rstripped[7:])
                    in_text = 0
                elif rstripped.startswith("--type "):
                    curr_query.set_type(rstripped[7:])
                    in_text = 0
                elif rstripped.startswith("--text"):
                    in_text = 1
                elif rstripped.startswith("--end"):
                    in_text = 0
                    if curr_query.is_valid():
                        queries.append(curr_query.get_data())
                    else:
                        logging.warning(
                            "SampleQueries#read_queries invalid query: {}".format(
                                curr_query.get_data()
                            )
                        )
                    curr_query = SampleQuery()
                elif in_text > 0:
                    curr_query.append_to_text(rstripped)
        except Exception as e:
            logging.error(
                "SampleQueries#read_queries error on file: {}".format(filename)
            )
            logging.info(str(e))
            logging.error("Stack trace:\n%s", traceback.format_exc())

        logging.warning(
            "SampleQueries#read_queries returning {} queries".format(len(queries))
        )
        return queries
