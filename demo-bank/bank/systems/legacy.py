"""Legacy: an old core banking system, read only. Tables, stored procedures and batch programs to explain and convert."""

from __future__ import annotations

from typing import Literal

from fastapi import HTTPException, Path
from pydantic import BaseModel, Field

from ..common import Ctx, listing, make_subapp, not_found, reg

KEY = "legacy"
TITLE = "Legacy core system"
LINE = "An old core banking system, read only: tables with cryptic names, stored procedures and batch programs, to explain and convert."


class ColumnMeaning(BaseModel):
    column: str = Field(..., min_length=1, description="The column name, for example AC_BAL.")
    meaning: str = Field("", description="What the column holds, in plain words. May be empty when the confidence is cannot_determine.")
    confidence: Literal["high", "medium", "low", "cannot_determine"] = Field(
        ..., description="How sure you are. Use cannot_determine when nothing in the tables, procedures and programs shows the meaning.")
    evidence: str = Field("", description="Where the meaning comes from: the procedure or program and line, or the sample rows.")


class Documentation(BaseModel):
    object_type: Literal["table", "procedure", "program"] = Field(..., description="What is being explained.")
    object_name: str = Field(..., min_length=1, description="The table, procedure or program name, for example ACMAST.")
    explanation: str = Field(..., min_length=1, description="What the object does or holds, in plain language that a new engineer can follow.")
    columns: list[ColumnMeaning] = Field(default_factory=list, description="For a table: what each column means, with confidence and evidence.")
    assumptions: list[str] = Field(default_factory=list, description="Every assumption made, each in one plain sentence.")
    drafted_by: str = Field("agent", description="Who wrote the draft. Free text.")


class Conversion(BaseModel):
    target_language: str = Field(..., min_length=1, description="The modern language of the conversion, for example Python or Java.")
    converted_source: str = Field(..., min_length=1, description="The converted program, as source text.")
    stage: Literal["draft_translation", "tests_written", "tests_passing", "ready_for_engineer_review"] = Field(
        ..., description="How far the conversion has got.")
    points_to_check: list[str] = Field(..., min_length=1, description="What an engineer must check before this is used, each in one plain sentence.")
    drafted_by: str = Field("agent", description="Who wrote the draft. Free text.")


def build(ctx: Ctx):
    app = make_subapp(ctx, key=KEY, title=TITLE, summary_line=LINE,
                      description="This system is an old core banking system that nobody can change. It is read only. Its tables, stored procedures and batch "
                                  "programs are here to be explained and converted. Its customers are its own and are not the records of the current core system.")
    st = ctx.store
    d = lambda: st.data

    @reg(app, "get", "/tables", "list_legacy_tables", "List the legacy tables",
         "List the tables of the old core system: table_name, row count and column count. The names are the old system's own and say little. "
         "Read one with get_legacy_table.")
    def list_legacy_tables():
        return listing([{"table_name": t["table_name"], "row_count": t["row_count"], "column_count": len(t["columns"])} for t in d()["legacy_tables"].values()])

    @reg(app, "get", "/tables/{table_name}", "get_legacy_table", "Get one legacy table",
         "Read one table: each column with its name, type, whether it may be empty and the catalogue comment (most are empty), the primary key, the "
         "foreign keys, the indexes, the row count and some sample rows. Amounts, dates and codes are stored in the old system's own forms. "
         "What a column means is not always written down: work it out from the stored procedures, the programs and the sample rows, and say so "
         "when it cannot be worked out. Also any saved documentation drafts.")
    def get_legacy_table(table_name: str = Path(..., description="Table name, for example ACMAST.")):
        t = d()["legacy_tables"].get(table_name.upper())
        if not t:
            raise not_found("table", table_name, "Use list_legacy_tables to find names.")
        return t

    @reg(app, "get", "/procedures", "list_stored_procedures", "List the stored procedures",
         "List the stored procedures of the old core system: procedure_name, the number of parameters, the number of source lines and the date last changed. "
         "Read the source of one with get_stored_procedure.")
    def list_stored_procedures():
        return listing([{"procedure_name": p["procedure_name"], "parameter_count": len(p["parameters"]), "line_count": p["line_count"],
                         "last_changed": p["last_changed"]} for p in d()["legacy_procedures"].values()])

    @reg(app, "get", "/procedures/{procedure_name}", "get_stored_procedure", "Get one stored procedure",
         "Read one stored procedure: its parameters and its source text, with the comments the authors left. The procedures show how the tables are "
         "used: which codes mean what and in which unit an amount is held.")
    def get_stored_procedure(procedure_name: str = Path(..., description="Procedure name, for example SP_POST_TXN.")):
        p = d()["legacy_procedures"].get(procedure_name.upper())
        if not p:
            raise not_found("procedure", procedure_name, "Use list_stored_procedures to find names.")
        return p

    @reg(app, "get", "/programs", "list_legacy_programs", "List the legacy batch programs",
         "List the batch programs of the old core system: program_name, language, when it runs, the number of source lines and the date last changed. "
         "Read the source of one with get_legacy_program.")
    def list_legacy_programs():
        return listing([{k: p[k] for k in ("program_name", "language", "schedule", "line_count", "last_changed")} for p in d()["legacy_programs"].values()])

    @reg(app, "get", "/programs/{program_name}", "get_legacy_program", "Get one legacy program",
         "Read one batch program as source text in an old business language, with its comments. Also any saved documentation drafts and conversions. "
         "Read the comments with care: a rule in a comment may be the reason for a line of code that looks wrong.")
    def get_legacy_program(program_name: str = Path(..., description="Program name, for example INTACCR.")):
        p = d()["legacy_programs"].get(program_name.upper())
        if not p:
            raise not_found("program", program_name, "Use list_legacy_programs to find names.")
        return p

    @reg(app, "post", "/documentation", "save_legacy_documentation", "Save legacy documentation (draft)",
         "Save your explanation of one table, procedure or program in plain language, with what each column means (for a table), your confidence in each "
         "and the evidence, and every assumption. This is a draft: stored with who wrote it, a timestamp and a version number, earlier versions kept. "
         "Use cannot_determine for a column whose meaning the system does not show. Refused with 404 if the object does not exist and 422 if a column "
         "is not in the table.")
    def save_legacy_documentation(body: Documentation):
        coll = {"table": "legacy_tables", "procedure": "legacy_procedures", "program": "legacy_programs"}[body.object_type]
        obj = d()[coll].get(body.object_name.upper())
        if not obj:
            raise not_found(body.object_type, body.object_name, "Use the list operations to find names.")
        if body.object_type == "table":
            known = {c["name"] for c in obj["columns"]}
            bad = [c.column for c in body.columns if c.column not in known]
            if bad:
                raise HTTPException(422, f"Column {bad[0]} is not in table {obj['table_name']}. Use get_legacy_table to read the columns.")
        elif body.columns:
            raise HTTPException(422, "Column meanings are only for a table. Leave columns empty for a procedure or a program.")
        v = st.add_draft(obj, "documentation_drafts", {k: val for k, val in body.model_dump().items() if k not in ("drafted_by",)}, body.drafted_by)
        return {"applied": True, "kind": "draft", "object": f"{body.object_type} {body.object_name.upper()}", "draft": v}

    @reg(app, "post", "/programs/{program_name}/conversion", "save_converted_program", "Save a converted program (draft)",
         "Save your conversion of a legacy batch program to a modern language: the converted source, the stage it has reached and the points an engineer "
         "must check before it is used. At least one point to check is required. This is a draft: stored with who wrote it, a timestamp and a version "
         "number, earlier versions kept. Nothing is run or installed.")
    def save_converted_program(body: Conversion, program_name: str = Path(..., description="Program name, for example INTACCR.")):
        p = d()["legacy_programs"].get(program_name.upper())
        if not p:
            raise not_found("program", program_name, "Use list_legacy_programs to find names.")
        v = st.add_draft(p, "conversions", {k: val for k, val in body.model_dump().items() if k != "drafted_by"}, body.drafted_by)
        return {"applied": True, "kind": "draft", "program": p["program_name"], "draft": v}

    return app
