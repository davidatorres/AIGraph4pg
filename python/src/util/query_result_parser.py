# This class implements a simple key-based counter, often used
# for data exploration and wrangling.
# Chris Joakim, Microsoft

import json
import logging
import traceback
import sys

class QueryResultParser:
    """
    Instances of this class parse the results of Azure PostgreSQL 
    and Apache AGE queries.
    """

    def __init__(self):
        self.data = {}

    def parse(self, query_result:tuple) -> list:
        """
        psycopg cursor.execute() returns a tuple of tuples, which
        this method parses into a list of objects.
        The Apache AGE tuples contain odd strings that contain
        string values like '::vertex' and '::edge' that are handled here.
        """
        print('parse() {} {}'.format(query_result, str(type(query_result))))
        try:
            if isinstance(query_result, tuple):
                if len(query_result) == 1:
                    elem = query_result[0]
                    print('1elem: {} {}'.format(elem, str(type(elem))))
                    if isinstance(elem, str):
                        colon_pair_count = elem.count('::')
                        if colon_pair_count == 1:
                            return self.parse_single_colonpair_result(elem)
                        else:
                            return elem
                    else:
                        return elem
                else:
                    return list(query_result)
        except Exception as e:
            logging.error('AgeResultParser - exception:', str(e))
            logging.error(traceback.format_exc())
        return None

    def parse_single_colonpair_result(self, s):
        tokens = s.strip().split('::')
        leftpart = tokens[0]
        jstr = leftpart
        # if leftpart.startswith('{'):
        #     jstr = leftpart + '}'
        # elif leftpart.startswith('['):
        #     jstr = leftpart + ']'
        print("jstr: {}".format(jstr))
        try:
            return json.loads(jstr)
        except Exception as e:
            return dict
    

# row: (14258, 'plpgsql', '1.0') 3 <class 'tuple'>
# row: (24760, 'vector', '0.7.0') 3 <class 'tuple'>
# row: (25081, 'age', '1.5.0') 3 <class 'tuple'>
# row: (106293, 'libraries1', 'libraries1') 3 <class 'tuple'>
# row: (10761,) 1 <class 'tuple'>
# row: (1, '2captcha-python', '') 3 <class 'tuple'>
# row: (2, '2to3', '2to3') 3 <class 'tuple'>
# row: (3, 'a2wsgi', '') 3 <class 'tuple'>
# row: ('21312',) 1 <class 'tuple'>
# row: ('{"id": 844424930131969, "label": "Developer", "properties": {"name": "info@2captcha.com"}}::vertex',) 1 <class 'tuple'>
# row: ('{"id": 844424930131970, "label": "Developer", "properties": {"name": "xoviat"}}::vertex',) 1 <class 'tuple'>
# row: ('[{"id": 1407374883553290, "label": "uses_lib", "end_id": 1125899906851581, "start_id": 1125899906842630, "properties": {}}::edge, {"id": 1407374883587559, "label": "uses_lib", "end_id": 1125899906851227, "start_id": 1125899906851581, "properties": {}}::edge, {"id": 1407374883586028, "label": "uses_lib", "end_id": 1125899906853118, "start_id": 1125899906851227, "properties": {}}::edge, {"id": 1407374883592102, "label": "uses_lib", "end_id": 1125899906851227, "start_id": 1125899906853118, "properties": {}}::edge, {"id": 1407374883586023, "label": "uses_lib", "end_id": 1125899906850362, "start_id": 1125899906851227, "properties": {}}::edge]',) 1 <class 'tuple'>
