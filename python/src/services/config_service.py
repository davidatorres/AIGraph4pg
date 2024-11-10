import base64
import json
import logging
import os
import sys
import time
import traceback

from cryptography.fernet import Fernet

# This class is used to define and obtain all configuration values
# in this solution.  These are typically obtained at runtime via
# environment variables.
#
# This class also implements encryption and decryption using a symmetric-key
# configured with environment variable AIG4PG_ENCRYPTION_SYMMETRIC_KEY.
#
# Chris Joakim, Microsoft


class ConfigService:

    @classmethod
    def envvar(cls, name: str, default: str = "") -> str:
        """
        Return the value of the given environment variable name,
        or the given default value."""
        if name in os.environ:
            return os.environ[name].strip()
        return default

    @classmethod
    def int_envvar(cls, name: str, default: int = -1) -> int:
        """
        Return the int value of the given environment variable name,
        or the given default value.
        """
        if name in os.environ:
            value = os.environ[name].strip()
            try:
                return int(value)
            except Exception as e:
                logging.error(
                    "int_envvar error for name: {} -> {}; returning default.".format(
                        name, value
                    )
                )
                return default
        return default

    @classmethod
    def float_envvar(cls, name: str, default: float = -1.0) -> float:
        """
        Return the float value of the given environment variable name,
        or the given default value.
        """
        if name in os.environ:
            value = os.environ[name].strip()
            try:
                return float(value)
            except Exception as e:
                logging.error(
                    "float_envvar error for name: {} -> {}; returning default.".format(
                        name, value
                    )
                )
                return default
        return default

    @classmethod
    def boolean_envvar(cls, name: str, default: bool) -> bool:
        """
        Return the boolean value of the given environment variable name,
        or the given default value.
        """
        if name in os.environ:
            value = str(os.environ[name]).strip().lower()
            if value == "true":
                return True
            elif value == "t":
                return True
            elif value == "yes":
                return True
            elif value == "y":
                return True
            else:
                return False
        return default

    @classmethod
    def boolean_arg(cls, flag: str) -> bool:
        """Return a boolean indicating if the given arg is in the command-line."""
        for arg in sys.argv:
            if arg == flag:
                return True
        return False

    @classmethod
    def project_version(cls) -> str:
        return "0.9.0, 2024/11/10"

    @classmethod
    def defined_environment_variables(cls) -> dict:
        """
        Return a dict with the defined environment variable names and descriptions
        """
        d = dict()
        d["AIG4PG_ENCRYPTION_SYMMETRIC_KEY"] = (
            "optional symmetric key for encryption/decryption"
        )
        d["AIG4PG_LOG_LEVEL"] = (
            "See values in class LoggingLevelService - notset, debug, info, warning, error, or critical"
        )
        d["AIG4PG_OPENAI_URL"] = "The URL of your Azure OpenAI account"
        d["AIG4PG_OPENAI_KEY"] = "The Key of your Azure OpenAI account"
        d["AIG4PG_OPENAI_COMPLETIONS_DEP"] = (
            "The name of your Azure OpenAI completions deployment"
        )
        d["AIG4PG_OPENAI_EMBEDDINGS_DEP"] = (
            "The name of your Azure OpenAI embeddings deployment"
        )
        d["AIG4PG_TRUNCATE_LLM_CONTEXT_MAX_NTOKENS"] = ""
        d["AIG4PG_PG_FLEX_SERVER"] = "Azure PostgreSQL Flex Server hostname"
        d["AIG4PG_PG_FLEX_PORT"] = "Azure PostgreSQL Flex Server port"
        d["AIG4PG_PG_FLEX_DB"] = "Azure PostgreSQL Flex Server database"
        d["AIG4PG_PG_FLEX_USER"] = "Azure PostgreSQL Flex Server user"
        d["AIG4PG_PG_FLEX_PASS"] = "Azure PostgreSQL Flex Server user password"

        # Optional environment variables.  Cosmos DB PostgreSQL is not used in this project.
        d["LOCAL_PG_PASS"] = (
            "Optional.  Used by the psql.ps1/psql.sh scripts for local PostgreSQL access"
        )
        d["AZURE_COSMOSDB_PG_SERVER"] = (
            "Optional.  Used by the psql.ps1/psql.sh scripts for Cosmos DB PostgreSQL"
        )
        d["AZURE_COSMOSDB_PG_USER"] = (
            "Optional.  Used by the psql.ps1/psql.sh scripts for Cosmos DB PostgreSQL"
        )
        d["AZURE_COSMOSDB_PG_PASS"] = (
            "Optional.  Used by the psql.ps1/psql.sh scripts for Cosmos DB PostgreSQL"
        )
        return d

    @classmethod
    def sample_environment_variable_values(cls) -> dict:
        d = dict()
        d["AIG4PG_ENCRYPTION_SYMMETRIC_KEY"] = ""
        d["AIG4PG_LOG_LEVEL"] = "info"
        d["AIG4PG_OPENAI_URL"] = ""
        d["AIG4PG_OPENAI_KEY"] = ""
        d["AIG4PG_OPENAI_COMPLETIONS_DEP"] = "gpt4"
        d["AIG4PG_OPENAI_EMBEDDINGS_DEP"] = "embeddings"
        d["AIG4PG_TRUNCATE_LLM_CONTEXT_MAX_NTOKENS"] = "0"
        d["AIG4PG_PG_FLEX_SERVER"] = ""
        d["AIG4PG_PG_FLEX_PORT"] = "5432"
        d["AIG4PG_PG_FLEX_DB"] = ""
        d["AIG4PG_PG_FLEX_USER"] = ""
        d["AIG4PG_PG_FLEX_PASS"] = ""
        d["LOCAL_PG_PASS"] = ""
        return d

    @classmethod
    def log_defined_env_vars(cls):
        """Log the defined AIG4PG_ environment variables as JSON"""
        keys = sorted(cls.defined_environment_variables().keys())
        selected = dict()
        for key in keys:
            value = cls.envvar(key)
            selected[key] = value
        logging.info(
            "log_defined_env_vars: {}".format(
                json.dumps(selected, sort_keys=True, indent=2)
            )
        )

    @classmethod
    def print_defined_env_vars(cls):
        """print() the defined AIG4PG_ environment variables as JSON"""
        keys = sorted(cls.defined_environment_variables().keys())
        selected = dict()
        for key in keys:
            value = cls.envvar(key)
            selected[key] = value
        print(
            "print_defined_env_vars: {}".format(
                json.dumps(selected, sort_keys=True, indent=2)
            )
        )

    @classmethod
    def symmetric_encryption_key(cls) -> str:
        return cls.envvar("AIG4PG_ENCRYPTION_SYMMETRIC_KEY", "")

    @classmethod
    def using_symmetric_encryption_key(cls) -> bool:
        key = cls.symmetric_encryption_key()
        if (key == None) or (len(key) == 0):
            return False
        else:
            return True

    @classmethod
    def postgresql_server(cls) -> str:
        value = cls.envvar("AIG4PG_PG_FLEX_SERVER", None)
        if cls.using_symmetric_encryption_key():
            return cls.sym_decrypt(value)
        else:
            return value

    @classmethod
    def postgresql_port(cls) -> str:
        return cls.envvar("AIG4PG_PG_FLEX_PORT", "5432")

    @classmethod
    def postgresql_database(cls) -> str:
        return cls.envvar("AIG4PG_PG_FLEX_DB", None)

    @classmethod
    def postgresql_user(cls) -> str:
        value = cls.envvar("AIG4PG_PG_FLEX_USER", None)
        if cls.using_symmetric_encryption_key():
            return cls.sym_decrypt(value)
        else:
            return value

    @classmethod
    def postgresql_password(cls) -> str:
        value = cls.envvar("AIG4PG_PG_FLEX_PASS", None)
        if cls.using_symmetric_encryption_key():
            return cls.sym_decrypt(value)
        else:
            return value

    @classmethod
    def azure_openai_url(cls) -> str:
        value = cls.envvar("AIG4PG_OPENAI_URL", None)
        if cls.using_symmetric_encryption_key():
            return cls.sym_decrypt(value)
        else:
            return value

    @classmethod
    def azure_openai_key(cls) -> str:
        value = cls.envvar("AIG4PG_OPENAI_KEY", None)
        if cls.using_symmetric_encryption_key():
            return cls.sym_decrypt(value)
        else:
            return value

    @classmethod
    def azure_openai_version(cls) -> str:
        return cls.envvar("AIG4PG_OPENAI_VERSION", "2023-12-01-preview")

    @classmethod
    def azure_openai_completions_deployment(cls) -> str:
        return cls.envvar("AIG4PG_OPENAI_COMPLETIONS_DEP", None)

    @classmethod
    def azure_openai_embeddings_deployment(cls) -> str:
        return cls.envvar("AIG4PG_OPENAI_EMBEDDINGS_DEP", None)

    @classmethod
    def truncate_llm_context_max_ntokens(cls) -> int:
        """
        Zero indicates no truncation.
        A positive integer is the max number of tokens.
        """
        return cls.int_envvar("AIG4PG_TRUNCATE_LLM_CONTEXT_MAX_NTOKENS", 0)

    @classmethod
    def epoch(cls) -> float:
        """Return the current epoch time, as time.time()"""
        return time.time()

    @classmethod
    def verbose(cls, override_flags: list = None) -> bool:
        """Return a boolean indicating if --verbose or -v is in the command-line."""
        flags = ["--verbose", "-v"] if override_flags is None else override_flags
        # true_value if condition else false_value
        for arg in sys.argv:
            for flag in flags:
                if arg == flag:
                    return True
        return False

    @classmethod
    def sym_encrypt(cls, value: str) -> str | None:
        if value is not None:
            key = ConfigService.symmetric_encryption_key()
            if len(key) > 0:
                fernet = Fernet(key)
                b64_bytes = base64.b64encode(value.encode("utf-8"))
                return fernet.encrypt(b64_bytes).decode("utf-8")
            else:
                return value
        else:
            return value

    @classmethod
    def sym_decrypt(cls, value: str) -> str | None:
        if value is not None:
            key = ConfigService.symmetric_encryption_key()
            if len(key) > 0:
                fernet = Fernet(key)
                bytes = fernet.decrypt(value)
                return base64.b64decode(bytes).decode("utf-8")
            else:
                return value
        else:
            return value

    @classmethod
    def generate_fernet_key(cls) -> str:
        return str(Fernet.generate_key().decode("utf-8"))

    @classmethod
    def set_standard_unit_test_env_vars(cls):
        """Set environment variables for use in unit tests"""
        os.environ["AIG4PG_ENCRYTION_SYMMETRIC_KEY"] = ""
        os.environ["AIG4PG_LOG_LEVEL"] = "debug"

        os.environ["AIG4PG_OPENAI_URL"] = "https://gbbcjcaigopenai3.openai.azure.com/"
        os.environ["AIG4PG_OPENAI_KEY"] = "xj48"
        os.environ["AIG4PG_OPENAI_COMPLETIONS_DEP"] = "gpt4"
        os.environ["AIG4PG_OPENAI_EMBEDDINGS_DEP"] = "embeddings"

        os.environ["AIG4PG_PG_FLEX_SERVER"] = "gbbcj.postgres.database.azure.com"
        os.environ["AIG4PG_PG_FLEX_DB"] = "aig"
        os.environ["AIG4PG_PG_FLEX_PORT"] = "5432"
        os.environ["AIG4PG_PG_FLEX_USER"] = "cj"
        os.environ["AIG4PG_PG_FLEX_PASS"] = "topSECRET!"

        os.environ["SAMPLE_INT_VAR"] = "98"
        os.environ["SAMPLE_FLOAT_VAR"] = "98.6"
        os.environ["SAMPLE_BOOLEAN_TRUE_VAR"] = "TRue"
        os.environ["SAMPLE_BOOLEAN_FALSE_VAR"] = "F"
        os.environ["SAMPLE_IATA_CODE"] = "CLT"
