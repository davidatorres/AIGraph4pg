import os
import sys
import pytest

from dotenv import load_dotenv

from src.services.config_service import ConfigService
from src.util.cite_parser import CiteParser

# pytest -v tests/test_cite_parser.py


def test_parsing_reasonable_values():
    parser = CiteParser()

    url = parser.parse("99 Wash. App. 575", "0575")
    assert parser.scrubbed_cite == "99 wash app 575"
    assert url == "https://static.case.law/wash-app/99/cases/0575-01.json"

    url = parser.parse("99 Wash. App. 575", "0575-01")
    assert parser.scrubbed_cite == "99 wash app 575"
    assert url == "https://static.case.law/wash-app/99/cases/0575-01.json"

    parser = CiteParser()
    url = parser.parse("99 Wash. App. 575", "0575-05")
    assert parser.scrubbed_cite == "99 wash app 575"
    assert url == "https://static.case.law/wash-app/99/cases/0575-05.json"

    url = parser.parse("95 Wash. 2d 394", "0394-01")
    assert parser.scrubbed_cite == "95 wash 2d 394"
    assert url == "https://static.case.law/wash-2d/95/cases/0394-01.json"

    url = parser.parse("1 Wash. 110", None)
    assert parser.scrubbed_cite == "1 wash 110"
    assert url == "https://static.case.law/wash/1/cases/0110-01.json"

    url = parser.parse("41 Wn. (2d) 224", None)
    assert parser.scrubbed_cite == "41 wn 2d 224"
    assert url == "https://static.case.law/wash-2d/41/cases/0224-01.json"

    url = parser.parse("41 Wn. (2d) 224", "0224")
    assert parser.scrubbed_cite == "41 wn 2d 224"
    assert url == "https://static.case.law/wash-2d/41/cases/0224-01.json"

    url = parser.parse("45 Wn. (2d) 71", None)
    assert parser.scrubbed_cite == "45 wn 2d 71"
    assert url == "https://static.case.law/wash-2d/45/cases/0071-01.json"

    url = parser.parse("45 Wn. (2d) 71", "0071")
    assert parser.scrubbed_cite == "45 wn 2d 71"
    assert url == "https://static.case.law/wash-2d/45/cases/0071-01.json"

    data = CiteParser.values_counter.get_data()
    expected_key = "parsed | 45 Wn. (2d) 71^0071 | https://static.case.law/wash-2d/45/cases/0071-01.json"
    assert expected_key in data.keys()


def test_parsing_unexpected_and_odd_values():
    parser = CiteParser()

    url = parser.parse(None, None)
    assert parser.scrubbed_cite == "none"
    assert url == None

    url = parser.parse("             ", None)
    assert parser.scrubbed_cite == ""
    assert url == None

    url = parser.parse(
        "this value(...) is UNexpected AND really() makes no sensE", None
    )
    assert parser.scrubbed_cite == "this value is unexpected and really makes no sense"
    assert url == None
