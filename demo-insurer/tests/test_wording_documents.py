"""The wordings in ../insurance/policy-library are written from the insurer's data and must say the same thing."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

import make_wording_documents as docs  # noqa: E402
from insurer.seed_policy import WORDINGS  # noqa: E402

if not docs.OUT.is_dir():
    pytest.skip("the policy library is not next to this copy of the insurer", allow_module_level=True)


@pytest.mark.parametrize("wording_id", sorted(docs.FILES))
def test_the_markdown_file_is_what_the_data_gives(wording_id):
    path = docs.OUT / f"{docs.FILES[wording_id]}.md"
    assert path.read_text(encoding="utf-8") == docs.markdown(WORDINGS[wording_id]), "run tools/make_wording_documents.py again"


@pytest.mark.parametrize("wording_id", sorted(docs.FILES))
def test_every_clause_is_in_the_file_with_its_number(wording_id):
    text = (docs.OUT / f"{docs.FILES[wording_id]}.md").read_text(encoding="utf-8")
    for clause in WORDINGS[wording_id]["clauses"]:
        assert f"**{clause['clause']} {clause['heading']}.** {clause['text']}" in text


@pytest.mark.parametrize("wording_id", sorted(docs.FILES))
def test_a_pdf_stands_beside_each_markdown_file(wording_id):
    pdf = docs.OUT / f"{docs.FILES[wording_id]}.pdf"
    assert pdf.is_file() and pdf.read_bytes()[:5] == b"%PDF-"
