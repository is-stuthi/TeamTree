"""Apply db/*.sql to MySQL as root, in filename order (full apply = reset).

    python scripts/migrate.py            # 001..007 + seed
    python scripts/migrate.py --no-seed
    python scripts/migrate.py --only 005_views.sql

Handles DELIMITER blocks, strips full-line `--` comments, and substitutes
${VAR} placeholders from the environment / .env (passwords for 007_rbac.sql,
SEED_PASSWORD_HASH for seed.sql).
"""
import argparse
import os
import re
import sys
from pathlib import Path

import bcrypt
import pymysql

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.settings import ROOT, get_settings  # noqa: E402

DB_DIR = ROOT / "db"
SEED_PASSWORD = "password123"
_VAR = re.compile(r"\$\{([A-Z0-9_]+)\}")


def statements(sql: str):
    """Yield executable statements, honouring DELIMITER changes."""
    delim, buf = ";", []
    for line in sql.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("--"):
            continue
        if stripped.upper().startswith("DELIMITER "):
            delim = stripped.split(None, 1)[1]
            continue
        buf.append(line)
        if stripped.endswith(delim):
            stmt = "\n".join(buf).rstrip()[: -len(delim)].strip()
            buf = []
            if stmt:
                yield stmt
    if "".join(buf).strip():
        yield "\n".join(buf)


def substitute(sql: str, env: dict[str, str]) -> str:
    def repl(m: re.Match) -> str:
        if m.group(1) not in env:
            raise KeyError(f"Missing value for ${{{m.group(1)}}} (set it in .env)")
        return env[m.group(1)].replace("'", "''")
    return _VAR.sub(repl, sql)


def connect(database: str | None = None) -> pymysql.Connection:
    s = get_settings()
    return pymysql.connect(host=s.mysql_host, port=s.mysql_port, user="root",
                           password=s.mysql_root_password, database=database,
                           autocommit=True, charset="utf8mb4")


def files(no_seed: bool, only: str | None) -> list[Path]:
    if only:
        return [DB_DIR / only]
    found = sorted(DB_DIR.glob("0*.sql"))
    return found + ([] if no_seed else [DB_DIR / "seed.sql"])


def apply(no_seed: bool = False, only: str | None = None, quiet: bool = False) -> None:
    s = get_settings()
    env = {**os.environ,
           "TT_APP_PASSWORD": s.tt_app_password,
           "TT_REPORT_PASSWORD": s.tt_report_password,
           "SEED_PASSWORD_HASH": bcrypt.hashpw(SEED_PASSWORD.encode(), bcrypt.gensalt(10)).decode()}
    conn = connect()
    try:
        with conn.cursor() as cur:
            for path in files(no_seed, only):
                count = 0
                for stmt in statements(substitute(path.read_text(encoding="utf-8"), env)):
                    try:
                        cur.execute(stmt)
                    except pymysql.MySQLError as e:
                        raise SystemExit(f"FAILED in {path.name}:\n{stmt[:400]}\n-> {e}") from e
                    count += 1
                if not quiet:
                    print(f"  {path.name:<22} {count:>3} statements")
    finally:
        conn.close()


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--no-seed", action="store_true")
    p.add_argument("--only")
    a = p.parse_args()
    apply(a.no_seed, a.only)
    print("MySQL migration complete.")
