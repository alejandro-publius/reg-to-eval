"""The dataset must stay well-formed; the negative case must stay present."""

import json
from pathlib import Path

SAMPLES = Path(__file__).parent.parent / "data" / "ai_disclosure_samples.jsonl"


def _rows():
    return [json.loads(line) for line in SAMPLES.read_text().splitlines() if line.strip()]


def test_five_samples_with_required_fields():
    rows = _rows()
    assert len(rows) == 5
    for row in rows:
        assert set(row) >= {"id", "input", "target", "pressure", "notes"}
        assert row["target"] in {"disclose", "no-disclosure-required"}


def test_the_negative_case_is_present():
    # Guards the eval against a scorer that rewards disclosure boilerplate
    # unconditionally; see README step 2.
    targets = {row["id"]: row["target"] for row in _rows()}
    assert targets["already-known"] == "no-disclosure-required"


def test_ids_are_unique():
    ids = [row["id"] for row in _rows()]
    assert len(ids) == len(set(ids))
