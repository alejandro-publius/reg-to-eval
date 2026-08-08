"""Characterization tests for the judge plumbing.

These pin the seams where a compliance eval can silently rot (see the README's
FORTRESS worked example): the template's placeholders, the grade vocabulary,
and the full path from a judge reply to a metric. The integration tests run the
real task through Inspect with a mock model, so they execute the actual
dataset-loading, grading, and aggregation code — no network, no keys.
"""

from pathlib import Path

import pytest
from inspect_ai import eval as inspect_eval
from inspect_ai.model import ModelOutput, get_model

from reg_to_eval.ai_disclosure import (
    DATA_FILE,
    JUDGE_INSTRUCTIONS,
    JUDGE_TEMPLATE,
    ai_disclosure,
)

N_SAMPLES = 15


# ---- static characterization of the judge prompt -------------------------- #

def test_template_carries_exactly_the_placeholders_model_graded_qa_fills():
    # {question} -> sample input, {answer} -> model reply, {criterion} -> target,
    # {instructions} -> JUDGE_INSTRUCTIONS. A renamed placeholder would survive
    # import and fail only at grading time, so it is pinned here.
    for placeholder in ("{question}", "{answer}", "{criterion}", "{instructions}"):
        assert placeholder in JUDGE_TEMPLATE


def test_instructions_demand_the_default_grade_vocabulary():
    """The scorer relies on Inspect's DEFAULT_GRADE_PATTERN (C/P/I) and default
    value_to_float. The instructions must ask for exactly that vocabulary —
    drifting to PASS/FAIL or YES/NO would make every reply unparseable."""
    assert "GRADE: C" in JUDGE_INSTRUCTIONS
    assert "GRADE: I" in JUDGE_INSTRUCTIONS


def test_template_tells_the_judge_not_to_reward_boilerplate():
    # The negative samples only work if the judge is told re-disclosure
    # boilerplate must not be rewarded; that sentence is load-bearing.
    assert "must not be rewarded" in JUDGE_TEMPLATE


def test_dataset_file_is_the_repo_dataset():
    assert Path(DATA_FILE).name == "ai_disclosure_samples.jsonl"
    assert Path(DATA_FILE).is_file()


# ---- end-to-end characterization through Inspect -------------------------- #

def _run(judge_reply: str):
    """Run the real task with every model call (policy and judge) canned."""
    outputs = [
        ModelOutput.from_content("mockllm/model", judge_reply)
        for _ in range(N_SAMPLES * 2)
    ]
    model = get_model("mockllm/model", custom_outputs=outputs)
    [log] = inspect_eval(
        ai_disclosure(), model=model, display="none", log_dir="/tmp/reg-eval-test-logs"
    )
    assert log.status == "success"
    return log


def _accuracy(log) -> float:
    return {m.name: m.value for m in log.results.scores[0].metrics.values()}["accuracy"]


@pytest.mark.slow
def test_grade_c_scores_one():
    log = _run("The reply discloses clearly.\n\nGRADE: C")
    assert _accuracy(log) == 1.0


@pytest.mark.slow
def test_grade_i_scores_zero():
    log = _run("The reply never discloses.\n\nGRADE: I")
    assert _accuracy(log) == 0.0


@pytest.mark.slow
def test_lowercase_grade_still_parses_and_scores():
    """The FORTRESS regression, pinned from this side: a judge writing
    'grade: c' must score identically to 'GRADE: C'. Inspect's default pattern
    upper-cases its capture; if this eval ever swaps in a custom pattern, this
    test is the tripwire."""
    log = _run("Meets the requirement.\n\ngrade: c")
    assert _accuracy(log) == 1.0


@pytest.mark.slow
def test_gradeless_reply_is_unscored_not_wrong():
    """A judge reply with no GRADE line must land as unscored (NaN, excluded
    from accuracy) — not silently counted as a failure or a pass."""
    import math

    log = _run("I cannot decide either way here.")
    for sample in log.samples:
        value = next(iter(sample.scores.values())).value
        assert isinstance(value, float) and math.isnan(value)
