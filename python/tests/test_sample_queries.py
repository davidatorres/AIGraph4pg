import logging

from src.util.sample_queries import SampleQueries

# pytest -v tests/test_sample_queries.py


def test_read_queries():
    queries = SampleQueries.read_queries()
    found_pg_extensions_query = False
    assert len(queries) > 3
    for q in queries:
        assert "name" in q
        assert "text" in q
        assert len(q["name"]) > 3
        assert len(q["text"]) > 10
        logging.info(q)

        if q["name"] == "PG: PostgreSQL Extensions":
            found_pg_extensions_query = True
            assert q["text"] == "SELECT oid, extname, extversion FROM pg_extension;"

    assert found_pg_extensions_query == True
