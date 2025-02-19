import os
import uuid

import duckdb
import pytest


@pytest.fixture(scope="session")
def db_connection():
    """Provides an in-memory DuckDB connection for tests."""
    con = duckdb.connect(database="test_db.duckdb")
    con.sql(
        "CREATE TABLE dwellings (uuid UUID PRIMARY KEY DEFAULT UUID(), status string)"
    )
    con.sql(
        """
        CREATE TABLE hubs (
        uuid UUID PRIMARY KEY DEFAULT UUID(),
        dwelling_uuid UUID REFERENCES dwellings(uuid))
        """
    )
    con.sql(
        """
        CREATE TABLE devices (
        uuid UUID PRIMARY KEY DEFAULT UUID(),
        type TEXT NOT NULL,
        state TEXT NOT NULL,
        hub_uuid UUID REFERENCES hubs(uuid))
        """
    )

    yield con

    if os.path.exists("test_db.duckdb"):
        os.remove("test_db.duckdb")

    con.close()  # Cleanup after tests


@pytest.fixture
def create_dwelling():
    con = duckdb.connect(database="test_db.duckdb")
    dwelling_uuid = str(uuid.uuid4())
    result = con.execute(
        "INSERT INTO dwellings (uuid) VALUES (?) RETURNING (uuid);",
        (dwelling_uuid,),
    ).fetchone()
    return str(result[0])
