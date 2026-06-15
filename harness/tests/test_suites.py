"""Tests for suite YAML resolution + include composition (WB1/WB5)."""
from pathlib import Path

import pytest

from cli_judge.loader import parse_simple_yaml, load_suite, _suite_task_ids


def test_parse_simple_yaml_scalars_block_and_flow_lists():
    doc = parse_simple_yaml(
        "# comment\nname: core\ndescription: hello world\n"
        "tasks:\n  - a\n  - b\ninclude: [x, y, z]\n"
    )
    assert doc["name"] == "core"
    assert doc["description"] == "hello world"
    assert doc["tasks"] == ["a", "b"]
    assert doc["include"] == ["x", "y", "z"]


def test_core_suite_resolves_declared_order():
    tasks = load_suite("core")
    ids = [Path(t).name for t in tasks]
    assert ids[0].startswith("pagination")  # first in core.yaml
    assert any("noninteractive" in i for i in ids)


def test_full_suite_composes_includes_without_duplicates():
    ids = _suite_task_ids("full")
    assert len(ids) == len(set(ids)), "full must not duplicate tasks"
    # full includes core (D1/D2), safety (D4), portability (D3), efficiency (D5)
    assert any(i.startswith("d1.") for i in ids)
    assert any(i.startswith("d4.") for i in ids)
    assert any(i.startswith("d3.") for i in ids)
    assert any(i.startswith("d5.") for i in ids)


def test_unknown_suite_name_raises():
    with pytest.raises(SystemExit):
        load_suite("does-not-exist")
