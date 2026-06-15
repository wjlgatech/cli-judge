"""Load suites, tasks, and fixtures, and validate them against schemas.

Status: PARTIALLY WIRED. TODOs marked for WB1/WB8.
"""
from __future__ import annotations
import json
import os
from pathlib import Path
from typing import Any

import jsonschema

ROOT = Path(__file__).resolve().parents[2]  # repo root
SCHEMA_DIR = ROOT / "schemas"


def _load_json(path: Path) -> dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _schema(name: str) -> dict[str, Any]:
    return _load_json(SCHEMA_DIR / name)


def validate_dir(target: str) -> list[str]:
    """Validate every *.task.json and *.fixture.json under target.
    Returns a list of human-readable error strings (empty = all valid)."""
    task_schema = _schema("task.schema.json")
    fixture_schema = _schema("fixture.schema.json")
    errors: list[str] = []
    base = Path(target)
    for p in base.rglob("*.json"):
        if p.name.endswith(".task.json"):
            schema = task_schema
        elif p.name.endswith(".fixture.json"):
            schema = fixture_schema
        else:
            continue
        try:
            doc = _load_json(p)
            # Drop $schema ref before validating (it's a pointer, not data).
            doc.pop("$schema", None)
            jsonschema.validate(doc, schema)
        except Exception as e:  # noqa: BLE001
            errors.append(f"{p}: {e.__class__.__name__}: {e}")
    return errors


def load_suite(name: str) -> list[Path]:
    """Resolve a suite name to an ordered list of task file paths.

    TODO (WB1): parse suites/<name>.yaml (or .json). For now, a suite maps to
    a dimension-prefix filter so the harness is runnable without a YAML dep:
      core -> d1.* and d2.* ; safety -> d4.* ; portability -> d3.* ;
      efficiency -> d5.* ; full -> all.
    """
    prefix_map = {
        "core": ("d1.", "d2."),
        "safety": ("d4.",),
        "portability": ("d3.",),
        "efficiency": ("d5.",),
        "full": ("d1.", "d2.", "d3.", "d4.", "d5."),
    }
    prefixes = prefix_map.get(name, ("d1.", "d2.", "d3.", "d4.", "d5."))
    fixtures_root = ROOT / "fixtures"
    tasks = sorted(fixtures_root.rglob("*.task.json"))
    out = []
    for t in tasks:
        doc = _load_json(t)
        if str(doc.get("id", "")).startswith(prefixes):
            out.append(t)
    return out


def load_task(path: Path) -> dict[str, Any]:
    doc = _load_json(path)
    doc.pop("$schema", None)
    doc["_path"] = str(path)
    return doc


def load_fixture_for(task: dict[str, Any]) -> dict[str, Any]:
    fx = ROOT / task["fixture"]
    doc = _load_json(fx)
    doc.pop("$schema", None)
    return doc
