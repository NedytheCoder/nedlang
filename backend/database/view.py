import os
import sqlite3
import sys
from pathlib import Path
from typing import Any

import streamlit as st

ROOT_DIR = Path(__file__).resolve().parent
BACKEND_ROOT = ROOT_DIR.parent
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from database.script import DB_PATH, get_connection


def get_table_names(conn: sqlite3.Connection) -> list[str]:
    rows = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
    ).fetchall()
    return [row[0] for row in rows]


def get_table_schema(conn: sqlite3.Connection, table_name: str) -> list[dict[str, Any]]:
    rows = conn.execute(f"PRAGMA table_info({table_name})").fetchall()
    return [dict(zip(["cid", "name", "type", "notnull", "dflt_value", "pk"], row)) for row in rows]


def get_table_rows(conn: sqlite3.Connection, table_name: str, limit: int = 100) -> list[dict[str, Any]]:
    rows = conn.execute(f"SELECT * FROM {table_name} LIMIT ?", (limit,)).fetchall()
    return [dict(row) for row in rows]


def execute_sql(conn: sqlite3.Connection, sql: str) -> list[dict[str, Any]]:
    rows = conn.execute(sql).fetchall()
    return [dict(row) for row in rows]


def main() -> None:
    st.set_page_config(page_title="Lingua AI DB Viewer", layout="wide")
    st.title("Lingua AI Database Viewer")
    st.markdown("Inspect the `lingua_ai.db` SQLite database used by the backend.")

    st.sidebar.header("Connection")
    st.sidebar.write(DB_PATH)

    with get_connection() as conn:
        table_names = get_table_names(conn)

        if not table_names:
            st.warning("No tables were found in the database.")
            return

        selected_table = st.sidebar.selectbox("Choose table", table_names)
        row_limit = st.sidebar.number_input("Rows to preview", min_value=10, max_value=1000, value=100, step=10)
        show_sql = st.sidebar.checkbox("Show SQL query editor", value=False)

        st.subheader(f"Table: `{selected_table}`")

        schema = get_table_schema(conn, selected_table)
        with st.expander("Table schema", expanded=True):
            st.table(schema)

        rows = get_table_rows(conn, selected_table, limit=row_limit)
        st.write(f"Showing up to {row_limit} rows from `{selected_table}`.")
        st.dataframe(rows)

        if show_sql:
            st.markdown("---")
            st.subheader("Run a custom SQL query")
            sql_query = st.text_area("SQL", value=f"SELECT * FROM {selected_table} LIMIT {row_limit}")
            if st.button("Execute SQL"):
                try:
                    query_rows = execute_sql(conn, sql_query)
                    st.write(f"Query returned {len(query_rows)} rows.")
                    st.dataframe(query_rows)
                except Exception as exc:
                    st.error(f"SQL execution failed: {exc}")

        st.sidebar.markdown("---")
        st.sidebar.write("Powered by Streamlit")


if __name__ == "__main__":
    main()
