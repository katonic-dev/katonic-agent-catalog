"""Finance: a small finance warehouse to ask questions of with one read-only SQL statement."""

from __future__ import annotations

import re
import sqlite3
import threading

from fastapi import HTTPException, Path
from pydantic import BaseModel, Field

from ..common import Ctx, listing, make_subapp, not_found, reg

KEY = "finance"
TITLE = "Finance warehouse"
LINE = "A small general ledger and management accounts for 24 months, held in a database that answers one read-only SQL query at a time."

ROW_CAP = 200
FORBIDDEN = {"insert", "update", "delete", "drop", "attach", "detach", "pragma", "create", "alter", "vacuum", "reindex", "analyze",
             "begin", "commit", "rollback", "savepoint", "release", "truncate", "load_extension"}


class FinanceQuery(BaseModel):
    sql: str = Field(..., min_length=1, description="One SQL SELECT statement. SQLite dialect. Anything else is refused.")
    max_rows: int = Field(100, ge=1, le=ROW_CAP, description="The most rows to return. The service never returns more than 200.")


class Figure(BaseModel):
    label: str = Field(..., min_length=1, description="What the figure is, for example Operating cost, October.")
    value: float = Field(..., description="The figure as a number.")
    unit: str = Field("USD", description="The unit, for example USD or percent.")
    period: str = Field("", description="The period it covers, for example 2026-10.")


class Commentary(BaseModel):
    question: str = Field(..., min_length=1, description="The question that was asked, in the user's words.")
    query_run: str = Field(..., min_length=1, description="The SQL that was run to get the figures.")
    figures: list[Figure] = Field(default_factory=list, description="The figures that answer the question. Empty if the warehouse cannot answer it.")
    commentary: str = Field(..., min_length=1, description="The answer in plain sentences. If the warehouse cannot answer, say what is missing.")
    drafted_by: str = Field("agent", description="Who wrote the draft. Free text.")


def scan(sql: str) -> list[str]:
    """Words outside quotes. Raises a readable 400 for a comment or a second statement."""
    words, i, n, cur = [], 0, len(sql), ""
    quote = ""
    while i < n:
        ch = sql[i]
        if quote:
            if ch == quote:
                if i + 1 < n and sql[i + 1] == quote:
                    i += 1
                else:
                    quote = ""
        elif ch in "'\"`":
            quote = ch
            if cur:
                words.append(cur.lower())
                cur = ""
        elif sql.startswith("--", i) or sql.startswith("/*", i):
            raise HTTPException(400, "Comments are not allowed in a query. Remove them and send one SELECT statement.")
        elif ch == ";":
            if sql[i + 1:].strip():
                raise HTTPException(400, "Send one statement only. A second statement after a semicolon is refused.")
        elif ch.isalnum() or ch == "_":
            cur += ch
        else:
            if cur:
                words.append(cur.lower())
                cur = ""
        i += 1
    if quote:
        raise HTTPException(400, "A quote is not closed. Check the query.")
    if cur:
        words.append(cur.lower())
    return words


def check_query(sql: str) -> str:
    text = sql.strip()
    if not text:
        raise HTTPException(400, "The query is empty. Send one SELECT statement.")
    words = scan(text)
    if not words or words[0] not in ("select", "with"):
        raise HTTPException(400, "Only a single SELECT statement is allowed. This one does not start with SELECT.")
    bad = [w for w in words if w in FORBIDDEN]
    if bad:
        raise HTTPException(400, f"The word {bad[0].upper()} is not allowed. This service only runs one read-only SELECT statement.")
    return text.rstrip().rstrip(";")


def build_database(tables: dict) -> sqlite3.Connection:
    con = sqlite3.connect(":memory:", check_same_thread=False)
    for name, t in tables.items():
        cols = ", ".join(f'"{c[0]}" {c[1]}' for c in t["columns"])
        con.execute(f'CREATE TABLE "{name}" ({cols})')
        marks = ", ".join("?" for _ in t["columns"])
        con.executemany(f'INSERT INTO "{name}" VALUES ({marks})', t["rows"])
    con.commit()
    return con


def deny_writes(action, arg1, arg2, dbname, source):
    allowed = (sqlite3.SQLITE_SELECT, sqlite3.SQLITE_READ, sqlite3.SQLITE_FUNCTION, sqlite3.SQLITE_RECURSIVE)
    return sqlite3.SQLITE_OK if action in allowed else sqlite3.SQLITE_DENY


def build(ctx: Ctx):
    app = make_subapp(ctx, key=KEY, title=TITLE, summary_line=LINE,
                      description="This system is a finance warehouse: a general ledger and management accounts for 24 months. It answers one read-only SQL "
                                  "SELECT statement at a time and refuses anything else.")
    st = ctx.store
    tables = st.data["finance"]
    keeper = build_database(tables)
    app.state.finance_db = keeper
    db_lock = threading.Lock()

    def table_or_404(name):
        t = tables.get(name.lower())
        if not t:
            raise not_found("table", name, "Use list_finance_tables to find names.")
        return name.lower(), t

    @reg(app, "get", "/tables", "list_finance_tables", "List the finance tables",
         "List the tables of the finance warehouse: table_name, what it holds and the number of rows. Read the columns of one with describe_finance_table, "
         "then ask a question with run_finance_query.")
    def list_finance_tables():
        return listing([{"table_name": n, "description": t["description"], "row_count": len(t["rows"])} for n, t in tables.items()])

    @reg(app, "get", "/tables/{table_name}", "describe_finance_table", "Describe a finance table",
         "Describe one table: each column with its type and what it holds, the row count and the first five rows. For gl_monthly it also gives the first "
         "and last period. If a measure you need is not in any table, the warehouse cannot answer the question.")
    def describe_finance_table(table_name: str = Path(..., description="Table name, for example gl_monthly.")):
        name, t = table_or_404(table_name)
        out = {"table_name": name, "description": t["description"], "row_count": len(t["rows"]),
               "columns": [{"name": c[0], "type": c[1], "description": c[2]} for c in t["columns"]],
               "first_rows": [dict(zip([c[0] for c in t["columns"]], r)) for r in t["rows"][:5]]}
        if name == "gl_monthly":
            periods = sorted({r[0] for r in t["rows"]})
            out["first_period"], out["last_period"] = periods[0], periods[-1]
        return out

    @reg(app, "post", "/query", "run_finance_query", "Run one read-only SQL query",
         "Run ONE read-only SQL SELECT statement (SQLite) on the finance warehouse and get back the column names and the rows. At most 200 rows come back, "
         "and truncated says if there were more. Anything that is not a single SELECT is refused with 400: no insert, update, delete, drop, attach or "
         "pragma, no comments and no second statement. The database is also opened read-only. This is a read: nothing is stored.")
    def run_finance_query(body: FinanceQuery):
        sql = check_query(body.sql)
        con = sqlite3.connect(":memory:", check_same_thread=False)
        try:
            with db_lock:
                keeper.backup(con)
            con.execute("PRAGMA query_only = ON")
            con.set_authorizer(deny_writes)
            budget = {"n": 0}

            def stop():
                budget["n"] += 1
                return 1 if budget["n"] > 4000 else 0

            con.set_progress_handler(stop, 1000)
            cur = con.execute(sql)
            cols = [c[0] for c in cur.description] if cur.description else []
            rows = cur.fetchmany(body.max_rows + 1)
        except sqlite3.Error as exc:
            msg = str(exc)
            if "interrupted" in msg:
                msg = "The query took too long and was stopped. Use a filter or a smaller join."
            raise HTTPException(400, f"The query could not run: {msg}")
        finally:
            con.close()
        truncated = len(rows) > body.max_rows
        rows = [list(r) for r in rows[:body.max_rows]]
        return {"columns": cols, "rows": rows, "row_count": len(rows), "truncated": truncated, "row_cap": ROW_CAP}

    @reg(app, "post", "/commentary", "save_finance_commentary", "Save finance commentary (draft)",
         "Save your answer to a finance question: the question, the query that was run, the figures and the commentary. If the warehouse cannot answer "
         "the question, save it with no figures and say what is missing. This is a draft: stored with who wrote it, a timestamp and a version number, "
         "earlier versions kept (the same question gives a new version). The query must be one SELECT statement. Nothing is published.")
    def save_finance_commentary(body: Commentary):
        check_query(body.query_run)
        key = re.sub(r"\s+", " ", body.question.strip().lower())
        with st.lock:
            store_ = st.data["finance_commentaries"]
            item = next((x for x in store_.values() if x["key"] == key), None)
            if item is None:
                item = {"commentary_id": f"FCM-{st.next_number('commentary', 1001)}", "key": key, "question": body.question, "versions": []}
                store_[item["commentary_id"]] = item
        v = st.add_draft(item, "versions", {k: val for k, val in body.model_dump().items() if k != "drafted_by"}, body.drafted_by)
        return {"applied": True, "kind": "draft", "commentary_id": item["commentary_id"], "draft": v}

    return app
