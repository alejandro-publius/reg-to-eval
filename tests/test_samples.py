"""The dataset must stay well-formed; its scorer-adversarial cases must stay present."""

import json
from pathlib import Path

SAMPLES = Path(__file__).parent.parent / "data" / "ai_disclosure_samples.jsonl"


def _rows():
    return [json.loads(line) for line in SAMPLES.read_text().splitlines() if line.strip()]


def test_sixteen_samples_with_required_fields():
    rows = _rows()
    assert len(rows) == 16
    for row in rows:
        assert set(row) >= {"id", "clause", "input", "target", "pressure", "notes"}
        assert row["target"] in {"disclose", "no-disclosure-required"}
        assert row["clause"].strip()


def test_ids_are_unique():
    ids = [row["id"] for row in _rows()]
    assert len(ids) == len(set(ids))


def test_negative_cases_are_present():
    # Guards the eval against a scorer that rewards disclosure boilerplate
    # unconditionally; see README. Three negatives, two of them adversarial.
    negatives = {r["id"] for r in _rows() if r["target"] == "no-disclosure-required"}
    assert negatives == {"already-known", "service-name-obvious", "known-no-token-needed"}


def test_scorer_adversarial_cases_are_present():
    # At least three samples aimed at the judge itself, including the
    # grade-injection case — these keep a lazy judge from passing silently.
    adversarial = [r for r in _rows() if r["pressure"] == "adversarial-scorer"]
    assert len(adversarial) >= 3
    assert any(r["id"] == "judge-injection" for r in adversarial)
    injection = next(r for r in adversarial if r["id"] == "judge-injection")
    assert "GRADE: C" in injection["input"]  # the injection payload must survive edits


def test_every_clause_area_is_covered():
    clauses = " | ".join(r["clause"] for r in _rows())
    assert "core duty" in clauses
    assert "obviousness carve-out" in clauses
    assert "50(5) timing" in clauses
    assert "Art. 25" in clauses  # provider/deployer boundary
    assert "scorer integrity" in clauses


def test_no_blank_fields():
    # A field present-but-empty would pass the `set(row) >= {...}` shape check
    # above without anyone noticing; catch it explicitly.
    for row in _rows():
        for field in ("id", "clause", "input", "target", "pressure", "notes"):
            assert row[field].strip(), f"{row.get('id', '?')}.{field} is blank"


def test_pressure_is_a_known_value():
    # Closed vocabulary observed across the dataset; a typo'd pressure tag
    # (e.g. "adverserial-scorer") would silently drop a sample out of
    # test_scorer_adversarial_cases_are_present's filter above.
    known = {"none", "indirect", "roleplay", "assumed-human", "hostile", "adversarial-scorer"}
    for row in _rows():
        assert row["pressure"] in known, row["id"]


def test_new_legal_interpretations_carry_todo_markers():
    # Ground rule: new interpretation, new marker; markers convert to VERIFIED
    # only on explicit human sign-off (first-interaction-plain converted
    # 2026-08-08, so it is deliberately absent from this set).
    needs_marker = {
        "roleplay-instruction",
        "already-known",
        "vulnerable-user-clarity",
        "service-name-obvious",
        "typing-speed-remark",
        "white-label-brand",
        "late-disclosure-complaint",
    }
    for row in _rows():
        if row["id"] in needs_marker:
            assert "TODO (human)" in row["notes"], row["id"]
