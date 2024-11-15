import os
import pytest

from src.util.query_result_parser import QueryResultParser
from src.services.config_service import ConfigService

# pytest -v tests/test_query_result_parser.py


def test_non_tuples_tuple():
    for value in [None, 1, 3.14, 'hello', [], {}]:
        qrp = QueryResultParser()
        result = qrp.parse(value)
        assert result == None

def test_parse_count_tuple():
    qrp = QueryResultParser()
    result = qrp.parse((10761,))
    assert result == 10761

def test_parse_two_numeric_tuple():
    qrp = QueryResultParser()
    result = qrp.parse((0, 1, 1, 2, 3, 5, 8, 13, 21, 34,))
    assert result == [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]

def test_parse_two_str_tuple():
    qrp = QueryResultParser()
    result = qrp.parse(('Azure Cosmos DB', 'Azure PostgreSQL',))
    assert result == ['Azure Cosmos DB', 'Azure PostgreSQL']

def test_parse_mixed_tuple():
    qrp = QueryResultParser()
    loc = {'lat': 35.50988920032978, 'lon': -80.83487017080188}
    result = qrp.parse((28036,'Davidson','NC',loc))
    assert result == [28036,'Davidson','NC',loc]

def test_parse_simple_str_one_tuple():
    qrp = QueryResultParser()
    result = qrp.parse(('Azure PostgreSQL',))
    assert result == 'Azure PostgreSQL'

def test_parse_single_result_vertex():
    qrp = QueryResultParser()
    arg = ('{"id": 844424930131969, "label": "Developer", "properties": {"name": "info@2captcha.com"}}::vertex',)
    result = qrp.parse(arg)
    print('test result: {}'.format(result))
    assert result['id'] == 844424930131969
    assert result['label'] == "Developer"
    assert result['properties']['name'] == "info@2captcha.com"


# Example tuples returned from PostgreSQL queries:
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
