import logging

import tiktoken

from openai import AzureOpenAI

from src.services.config_service import ConfigService
from src.services.ai_completion import AiCompletion

# Instances of this class are used to execute AzureOpenAI functionality.
# Chris Joakim, Microsoft


class AiService:
    """Constructor method; call initialize() immediately after this."""

    def __init__(self, opts={}):
        """
        Get the necessary environment variables and initialze an AzureOpenAI client.
        Also read the OWL file.
        """
        try:
            self.opts = opts
            self.aoai_endpoint = ConfigService.azure_openai_url()
            self.aoai_api_key = ConfigService.azure_openai_key()
            self.aoai_version = ConfigService.azure_openai_version()
            self.chat_function = None
            self.max_ntokens = ConfigService.truncate_llm_context_max_ntokens()

            # tiktoken, for token estimation, doesn't work with gpt-4 at this time
            self.tiktoken_encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
            self.enc = tiktoken.get_encoding("cl100k_base")

            self.aoai_client = AzureOpenAI(
                azure_endpoint=self.aoai_endpoint,
                api_key=self.aoai_api_key,
                api_version=self.aoai_version,
            )
            self.completions_deployment = (
                # deployment name/model = gpt4/gpt-4
                ConfigService.azure_openai_completions_deployment()
            )
            self.embeddings_deployment = (
                # deployment name/model = embeddings/text-embedding-ada-002
                ConfigService.azure_openai_embeddings_deployment()
            )
            logging.info("aoai endpoint:     {}".format(self.aoai_endpoint))
            logging.info("aoai version:      {}".format(self.aoai_version))
            logging.info("aoai client:       {}".format(self.aoai_client))
            logging.info(
                "aoai completions_deployment: {}".format(self.completions_deployment)
            )
            logging.info(
                "aoai embeddings_deployment:  {}".format(self.embeddings_deployment)
            )
        except Exception as e:
            logging.critical("Exception in AiService#__init__: {}".format(str(e)))
            logging.exception(e, stack_info=True, exc_info=True)
            return None

    def num_tokens_from_string(self, s: str) -> int:
        try:
            return len(self.tiktoken_encoding.encode(s))
        except Exception as e:
            logging.critical(
                "Exception in AiService#num_tokens_from_string: {}".format(str(e))
            )
            logging.exception(e, stack_info=True, exc_info=True)
            return 10000

    def generate_embeddings(self, text):
        """
        Generate an embeddings array from the given text.
        Return an CreateEmbeddingResponse object or None.
        Invoke 'resp.data[0].embedding' to get the array of 1536 floats.
        """
        try:
            # <class 'openai.types.create_embedding_response.CreateEmbeddingResponse'>
            return self.aoai_client.embeddings.create(
                input=text, model=self.embeddings_deployment
            )
        except Exception as e:
            logging.critical(
                "Exception in AiService#generate_embeddings: {}".format(str(e))
            )
            logging.exception(e, stack_info=True, exc_info=True)
            return None

    def text_to_chunks(self, text):
        max_chunk_size, chunks = 2048, list()
        current_chunk = ""
        for sentence in text.split("."):
            if len(current_chunk) + len(sentence) < max_chunk_size:
                current_chunk += sentence + "."
            else:
                chunks.append(current_chunk.strip())
                current_chunk = sentence + ". "
        if current_chunk:
            chunks.append(current_chunk.strip())
        return chunks
