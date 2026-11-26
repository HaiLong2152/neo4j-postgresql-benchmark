"""Check the PostgreSQL benchmark connection with read-only queries."""

import os
import sys
from pathlib import Path


EXPECTED_SERVER_VERSION = 170012


def main() -> int:
    print(f"Python {sys.version.split()[0]}")
    try:
        import psycopg
        from dotenv import load_dotenv
    except ImportError:
        print("Connection check: FAILED. Install requirements.txt in .venv.", file=sys.stderr)
        return 1

    print(f"Psycopg {psycopg.__version__}")
    load_dotenv(Path(__file__).resolve().parents[1] / ".env", interpolate=False, encoding="utf-8-sig")
    password = os.environ.get("BENCHMARK_POSTGRES_PASSWORD")
    if not password:
        print("Connection check: FAILED. Set BENCHMARK_POSTGRES_PASSWORD in benchmark/.env.", file=sys.stderr)
        return 1

    try:
        with psycopg.connect(
            host="127.0.0.1",
            port=os.environ.get("BENCHMARK_POSTGRES_PORT") or "5433",
            user=os.environ.get("BENCHMARK_POSTGRES_USER") or "postgres",
            dbname=os.environ.get("BENCHMARK_POSTGRES_DB") or "fraud_benchmark",
            password=password,
            connect_timeout=5,
            autocommit=True,
        ) as connection:
            version_number = connection.info.server_version
            with connection.cursor() as cursor:
                probe = cursor.execute("SELECT 1").fetchone()
                server = cursor.execute("SHOW server_version").fetchone()
    except (ValueError, psycopg.Error) as error:
        print(f"Connection check: FAILED ({type(error).__name__}). Check credentials, port and server state.", file=sys.stderr)
        return 1

    if server:
        print(f"Server: PostgreSQL {server[0]}")
    if probe:
        print(f"SELECT 1 = {probe[0]}")
    if probe != (1,) or not server or version_number != EXPECTED_SERVER_VERSION:
        print("Connection check: FAILED. Expected SELECT 1 and PostgreSQL 17.12.", file=sys.stderr)
        return 1
    print("Connection check: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
