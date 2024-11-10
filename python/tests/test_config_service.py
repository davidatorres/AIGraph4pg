import os
import sys
import pytest

from dotenv import load_dotenv

from src.services.config_service import ConfigService

# pytest -v tests/test_config_service.py


def test_envvar():
    ConfigService.set_standard_unit_test_env_vars()
    assert ConfigService.envvar("SAMPLE_IATA_CODE") == "CLT"
    assert ConfigService.envvar("MISSING") == ""
    assert ConfigService.envvar("MISSING", None) == None
    assert ConfigService.envvar("UNIVERSAL_ANSWER", "42") == "42"


def test_int_envvar():
    ConfigService.set_standard_unit_test_env_vars()
    assert ConfigService.int_envvar("SAMPLE_INT_VAR") == 98
    assert ConfigService.int_envvar("MISSING") == -1
    assert ConfigService.int_envvar("AIG4PG_GRAPH_SOURCE_TYPE") == -1
    assert ConfigService.int_envvar("MISSING", 13) == 13
    assert ConfigService.int_envvar("SAMPLE_IATA_CODE", 13) == 13


def test_float_envvar():
    ConfigService.set_standard_unit_test_env_vars()
    assert ConfigService.float_envvar("SAMPLE_FLOAT_VAR") == 98.6
    assert ConfigService.float_envvar("MISSING") == -1.0
    assert ConfigService.float_envvar("AIG4PG_GRAPH_SOURCE_TYPE") == -1.0
    assert ConfigService.float_envvar("MISSING", 13.1) == 13.1
    assert ConfigService.float_envvar("SAMPLE_IATA_CODE", 13.1) == 13.1


def test_boolean_envvar():
    ConfigService.set_standard_unit_test_env_vars()
    os.environ["TRUE_ARG"] = "TRuE"
    os.environ["FALSE_ARG"] = "FALse"
    os.environ["T_ARG"] = "t"
    os.environ["F_ARG"] = "F"
    os.environ["YES_ARG"] = "yeS"
    os.environ["Y_ARG"] = "Y"
    os.environ["N_ARG"] = "N"
    assert ConfigService.boolean_envvar("MISSING", True) == True
    assert ConfigService.boolean_envvar("MISSING", False) == False
    assert ConfigService.boolean_envvar("TRUE_ARG", False) == True
    assert ConfigService.boolean_envvar("FALSE_ARG", True) == False
    assert ConfigService.boolean_envvar("T_ARG", False) == True
    assert ConfigService.boolean_envvar("F_ARG", True) == False
    assert ConfigService.boolean_envvar("YES_ARG", False) == True
    assert ConfigService.boolean_envvar("Y_ARG", False) == True
    assert ConfigService.boolean_envvar("N_ARG", True) == False


def test_boolean_arg():
    ConfigService.set_standard_unit_test_env_vars()
    assert ConfigService.boolean_arg(sys.argv[0]) == True
    assert ConfigService.boolean_arg("MISSING") == False


def test_project_version():
    assert ConfigService.project_version() == "1.0.0, November 2024"


def test_defined_and_sample_environment_variables():
    ConfigService.print_defined_env_vars()
    defined = ConfigService.defined_environment_variables()
    samples = ConfigService.sample_environment_variable_values()
    assert "AIG4PG_LOG_LEVEL" in defined.keys()
    assert "AIG4PG_LOG_LEVEL" in samples.keys()
    assert len(defined.keys()) == 16
    assert len(samples.keys()) == 13


def test_log_defined_env_vars():
    try:
        ConfigService.log_defined_env_vars()
        assert True
    except Exception as e:
        assert False


def test_azure_postgresql_variables():
    ConfigService.set_standard_unit_test_env_vars()
    assert ConfigService.postgresql_server() == "gbbcj.postgres.database.azure.com"
    assert ConfigService.postgresql_port() == "5432"
    assert ConfigService.postgresql_database() == "aig"
    assert ConfigService.postgresql_user() == "cj"
    assert ConfigService.postgresql_password() == "topSECRET!"


def test_azure_openai_variables():
    ConfigService.set_standard_unit_test_env_vars()
    assert (
        ConfigService.azure_openai_url() == "https://gbbcjcaigopenai3.openai.azure.com/"
    )
    assert ConfigService.azure_openai_key() == "xj48"
    assert ConfigService.azure_openai_embeddings_deployment() == "embeddings"
    assert ConfigService.azure_openai_completions_deployment() == "gpt4"

    version = ConfigService.azure_openai_version()
    assert version.startswith("2023")


def test_verbose():
    # this is a challenge to test as tests.ps1 contains -v itself!
    # pytest -v --cov=pysrc/ --cov-report html tests/
    if "-v" in sys.argv:
        assert ConfigService.verbose() == True
    else:
        assert ConfigService.verbose() == False

    assert ConfigService.verbose(["-wordy"]) == False


def test_epoch():
    e = ConfigService.epoch()
    print(e)
    assert e > 1730061780  # 2024-10-27
    assert e < 1800000000


def test_key_generation():
    for n in range(10):
        key = ConfigService.generate_fernet_key()
        assert len(key) > 30
        assert len(key) < 50


def test_sym_encrypt_decrypt():
    test_cases = [
        "",
        "hello earth",
        "867-5309",
        "8888fbdbb32943ad9874ceXX729f53bh",
        "jwonQQTexjIQvYTfX4Rx6LoVT5mCf8yYDorkAz8LrK4FsGzOa8L9At33Kzflj26xCS4JCiYr9swgXYDbV8pnqQ==",
        "https://en.wikipedia.org/wiki/Easter_Island",
    ]
    test_cases.append(gettysburg_address())
    assert len(test_cases) == 7
    assert "our fathers brought forth" in test_cases[-1]

    # First test the use of no symmetric key
    os.environ["AIG4PG_ENCRYPTION_SYMMETRIC_KEY"] = ""
    assert ConfigService.symmetric_encryption_key() == ""
    assert ConfigService.using_symmetric_encryption_key() == False

    for test_case in test_cases:
        encrypted = ConfigService.sym_encrypt(test_case)
        decrypted = ConfigService.sym_decrypt(encrypted)
        assert test_case == decrypted

    assert ConfigService.sym_encrypt(None) == None
    assert ConfigService.sym_decrypt(None) == None

    # Next test the use of a symmetric key
    key = "VFu-rwVkaiZfAzkyqjyFzhdh25MKyZJqLTWbtGRCkUg="
    os.environ["AIG4PG_ENCRYPTION_SYMMETRIC_KEY"] = key
    assert ConfigService.symmetric_encryption_key() == key
    assert ConfigService.using_symmetric_encryption_key() == True

    for test_case in test_cases:
        encrypted = ConfigService.sym_encrypt(test_case)
        decrypted = ConfigService.sym_decrypt(encrypted)
        assert test_case == decrypted


def test_failing_decryption():
    ConfigService.set_standard_unit_test_env_vars()
    key = "VFu-rwVkaiZfAzkyqjyFzhdh25MKyZJqLTWbtGRCkUg="
    os.environ["AIG4PG_ENCRYPTION_SYMMETRIC_KEY"] = key

    with pytest.raises(Exception) as e_info:
        ConfigService.postgresql_server() == "gbbcj.postgres.database.azure.com"

    with pytest.raises(Exception) as e_info:
        ConfigService.postgresql_user() == "cj"

    with pytest.raises(Exception) as e_info:
        ConfigService.postgresql_password() == "topSECRET!"

    with pytest.raises(Exception) as e_info:
        ConfigService.azure_openai_url() == "https://gbbcjcaigopenai3.openai.azure.com/"

    with pytest.raises(Exception) as e_info:
        ConfigService.azure_openai_key() == "xj48"


def gettysburg_address():
    return """
Four score and seven years ago our fathers brought forth, on this continent, a new nation, conceived in Liberty, and dedicated to the proposition that all men are created equal.

Now we are engaged in a great civil war, testing whether that nation, or any nation so conceived and so dedicated, can long endure. We are met on a great battle-field of that war. We have come to dedicate a portion of that field, as a final resting place for those who here gave their lives that that nation might live. It is altogether fitting and proper that we should do this.

But, in a larger sense, we can not dedicate—we can not consecrate—we can not hallow—this ground. The brave men, living and dead, who struggled here, have consecrated it, far above our poor power to add or detract. The world will little note, nor long remember what we say here, but it can never forget what they did here. It is for us the living, rather, to be dedicated here to the unfinished work which they who fought here have thus far so nobly advanced. It is rather for us to be here dedicated to the great task remaining before us—that from these honored dead we take increased devotion to that cause for which they gave the last full measure of devotion—that we here highly resolve that these dead shall not have died in vain—that this nation, under God, shall have a new birth of freedom—and that government of the people, by the people, for the people, shall not perish from the earth.

Abraham Lincoln

November 19, 1863.
""".strip()
