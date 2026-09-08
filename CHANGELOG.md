# Changelog

All notable changes to this project are documented in this file. Format
follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/); this project
has no released version yet (see "Verification status" in the README).

## [Unreleased]

### Added
- Judge and scorer boundary tests (`tests/test_judge_behavior.py`): a
  content-sensitive mock judge that grades an obviously compliant vs. an
  obviously non-compliant system reply through the real `JUDGE_TEMPLATE`, plus
  two scorer-boundary characterizations (a stray `GRADE: P` is still accepted
  though never offered; the last `GRADE:` line wins over an earlier injected
  one, which is the premise the `judge-injection` sample depends on).
- Dataset well-formedness tests: no blank fields, and `pressure` values come
  from a known, closed set (`tests/test_samples.py`).
- `pyproject.toml`: a `[tool.ruff]` config (previously `ruff check` ran on
  defaults with no committed config) and a `dev` extra pinning the same ruff
  version CI uses.
- `.pre-commit-config.yaml` running ruff (lint + format) at that same pinned
  version.
- `CITATION.cff` and this changelog.
- README: license and Python-version badges, a three-command Quickstart, and
  real measured `inspect eval` output against `mockllm/model`.

### Fixed
- `src/reg_to_eval/ai_disclosure.py` docstrings said "fifteen hand-written
  samples"; the dataset has held sixteen since the `data:` commit below. The
  README already said sixteen.
- `.gitignore` did not exclude `logs/`, the directory `inspect eval` creates
  in the working directory by default (no `--log-dir`) — exactly what the
  README's own quickstart command does. A fresh clone following the README
  literally would get an untracked `logs/*.eval` file.

## 2026-09-06

### Changed
- CI: pin ruff so an upstream linter release cannot redden an untouched tree.

## 2026-09-04

### Added
- CI: run on `main` only, least-privilege token, cancel superseded runs,
  current actions.
- README: CI badge.
- Dependabot: keep GitHub Actions versions current.

## 2026-08-08

### Added
- Initial scaffold: EU AI Act Art. 50(1) (AI-disclosure) obligation
  translated into a runnable Inspect task, judge, and dataset.
- Dataset expanded to sixteen hand-written samples, each tagged with the
  clause it exercises.
- Judge characterization tests, CI, `LICENSE` (MIT), and a README Limitations
  section.
- `LEGAL_SIGNOFF.md`: official Art. 50 text placed beside every interpretation
  carrying a `TODO (human)` marker, adjudicated into four verification tiers
  (verified / human-directed / reviewed / open).

### Fixed
- Anchor the dataset path on the repo root rather than the working directory.
