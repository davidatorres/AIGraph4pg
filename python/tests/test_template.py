import os
import pytest

from src.util.template import Template
from src.services.config_service import ConfigService

# pytest -v tests/test_template.py


# @pytest.mark.skip(reason="bypassed for now")
# def test_get_template_and_render():
#     ConfigService.set_standard_unit_test_env_vars()

#     TODO - revist this test for vertex/edge generation

#     t = Template.get_template(os.getcwd(), "test_owl.txt")
#     assert t != None

#     values = dict()
#     values["ns"] = "http://cosmosdb.com/caigtest#"
#     values["comment"] = "This is a test comment"
#     values["label"] = "This is a test label"

#     text = Template.render(t, values)
#     assert text.strip() == expected_content()


def expected_content():
    return """

""".strip()
