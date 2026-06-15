"""Load suites, tasks, and fixtures, and validate them against schemas.

Status: WIRED (WB1). Validates against JSON Schema and resolves suite YAML
(with include composition) to ordered task paths.
"""
from __future__ import annotations
import json
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


SUITES_DIR = ROOT / "suites"


def parse_simple_yaml(text: str) -> dict[str, Any]:
    """Parse the tiny YAML subset the suite files use — scalars, block lists
    (``key:`` then indented ``- item``), and inline flow lists (``[a, b]``).
    Dependency-free by design (plan KTD3); not a general YAML parser."""
    doc: dict[str, Any] = {}
    current_key: str | None = None
    for raw in text.splitlines():
        line = "" if raw.lstrip().startswith("#") else raw.split("#", 1)[0].rstrip()
        if not line.strip():
            continue
        if line.lstrip().startswith("- ") and current_key is not None:
            doc.setdefault(current_key, [])
            doc[current_key].append(line.strip()[2:].strip())
            continue
        if ":" in line:
            key, _, rest = line.partition(":")
            key = key.strip()
            rest = rest.strip()
            if rest == "":
                doc[key] = []
                current_key = key
            elif rest.startswith("[") and rest.endswith("]"):
                doc[key] = [x.strip() for x in rest[1:-1].split(",") if x.strip()]
                current_key = None
            else:
                doc[key] = rest.strip("'\"")
                current_key = None
    return doc


def _suite_doc(name: str) -> dict[str, Any]:
    path = SUITES_DIR / f"{name}.yaml"
    if not path.exists():
        raise SystemExit(f"unknown suite '{name}' (no {path.name} in suites/)")
    return parse_simple_yaml(path.read_text(encoding="utf-8"))


def _suite_task_ids(name: str, _seen: set[str] | None = None) -> list[str]:
    """Ordered, de-duplicated task ids for a suite, resolving `include:`
    composition recursively while preserving first-seen order."""
    _seen = _seen if _seen is not None else set()
    if name in _seen:
        return []  # guard against an include cycle
    _seen.add(name)
    doc = _suite_doc(name)
    ids: list[str] = []
    if doc.get("include"):
        for sub in doc["include"]:
            ids.extend(_suite_task_ids(sub, _seen))
    ids.extend(doc.get("tasks", []))
    out: list[str] = []
    seen_ids: set[str] = set()
    for i in ids:
        if i not in seen_ids:
            seen_ids.add(i)
            out.append(i)
    return out


def _task_id_index() -> dict[str, Path]:
    index: dict[str, Path] = {}
    for t in sorted((ROOT / "fixtures").rglob("*.task.json")):
        index[_load_json(t).get("id", "")] = t
    return index


def load_suite(name: str) -> list[Path]:
    """Resolve a suite name to the ordered list of task file paths it declares,
    by parsing ``suites/<name>.yaml`` (with ``include:`` composition)."""
    ids = _suite_task_ids(name)
    index = _task_id_index()
    out: list[Path] = []
    for tid in ids:
        if tid not in index:
            raise SystemExit(f"suite '{name}' references unknown task id '{tid}'")
        out.append(index[tid])
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
