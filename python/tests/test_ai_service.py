import json
import os
import time
import pytest
import faker

from src.services.ai_completion import AiCompletion
from src.services.ai_conversation import AiConversation
from src.services.ai_service import AiService
from src.util.fs import FS

# pytest -v tests/test_ai_service.py


@pytest.mark.skip(reason="bypassed for now")
def test_constructor():
    ai_svc = AiService()
    assert ai_svc.aoai_endpoint.startswith("https://")
    assert ai_svc.aoai_endpoint.endswith(".openai.azure.com/")
    assert ai_svc.aoai_version.startswith("202")
    assert ai_svc.aoai_client is not None


@pytest.mark.skip(reason="bypassed for now")
def test_generate_embeddings():
    ai_svc = AiService()
    resp = ai_svc.generate_embeddings("python fastapi pydantic microservices")
    print(resp)
    assert resp is not None
    assert "CreateEmbeddingResponse" in str(type(resp))
    assert len(resp.data[0].embedding) == 1536
