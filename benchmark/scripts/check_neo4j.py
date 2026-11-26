"""Check the Neo4j benchmark connection with two read-only queries."""

import os
import sys
from pathlib import Path


EXPECTED_VERSION = "5.26.34"
EXPECTED_EDITION = "community"


def main() -> int:
    print(f"Python {sys.version.split()[0]}")
    try:
        from dotenv import load_dotenv
        from neo4j import GraphDatabase, READ_ACCESS, __version__
        from neo4j.exceptions import AuthError, DriverError, Neo4jError
    except ImportError:
        print("Connection check: FAILED. Install requirements.txt in .venv.", file=sys.stderr)
        return 1

    print(f"Neo4j Python Driver {__version__}")
    load_dotenv(Path(__file__).resolve().parents[1] / ".env", interpolate=False, encoding="utf-8-sig")
    password = os.environ.get("BENCHMARK_NEO4J_PASSWORD")
    if not password:
        print("Connection check: FAILED. Set BENCHMARK_NEO4J_PASSWORD in benchmark/.env.", file=sys.stderr)
        return 1

    port = os.environ.get("BENCHMARK_NEO4J_BOLT_PORT") or "7688"
    uri = os.environ.get("BENCHMARK_NEO4J_URI") or f"bolt://127.0.0.1:{port}"
    username = os.environ.get("BENCHMARK_NEO4J_USER") or "neo4j"
    database = os.environ.get("BENCHMARK_NEO4J_DATABASE") or "neo4j"
    try:
        with GraphDatabase.driver(uri, auth=(username, password), connection_timeout=5) as driver:
            with driver.session(database=database, default_access_mode=READ_ACCESS) as session:
                probe = session.run("RETURN 1 AS ok").single(strict=True)
                server = session.run(
                    "CALL dbms.components() YIELD name, versions, edition "
                    "WHERE name = 'Neo4j Kernel' "
                    "RETURN versions[0] AS version, edition"
                ).single(strict=True)
    except AuthError:
        print("Connection check: FAILED. Neo4j rejected authentication.", file=sys.stderr)
        return 1
    except (ValueError, DriverError, Neo4jError) as error:
        print(f"Connection check: FAILED ({type(error).__name__}). Check the URI and server state.", file=sys.stderr)
        return 1

    version, edition = server["version"], server["edition"]
    print(f"Server: Neo4j {version} {edition}")
    print(f"RETURN 1 = {probe['ok']}")
    if probe["ok"] != 1 or version != EXPECTED_VERSION or edition != EXPECTED_EDITION:
        print(f"Connection check: FAILED. Expected RETURN 1 and Neo4j {EXPECTED_VERSION} {EXPECTED_EDITION}.", file=sys.stderr)
        return 1
    print("Connection check: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
