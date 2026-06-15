import json
from pathlib import Path
from cli_judge.loader import validate_dir, load_suite, ROOT


def test_all_fixtures_valid():
    errs = validate_dir(str(ROOT / "fixtures"))
    assert errs == [], "\n".join(errs)


def test_core_suite_nonempty():
    tasks = load_suite("core")
    assert len(tasks) >= 1
    ids = [Path(t).name for t in tasks]
    assert any("pagination" in i for i in ids)


def test_every_fixture_has_real_provenance_or_is_synthetic():
    """Anti-gaming invariant: a fixture is only admitted with real provenance,
    otherwise it must be flagged synthetic (SPEC §9 governance)."""
    bad = []
    for p in (ROOT / "fixtures").rglob("*.fixture.json"):
        doc = json.loads(p.read_text(encoding="utf-8"))
        if not doc.get("provenance") and not doc.get("synthetic"):
            bad.append(p.name)
    assert bad == [], f"fixtures missing provenance and not marked synthetic: {bad}"


def test_full_suite_includes_every_committed_task():
    """The full suite must enumerate every committed task so none is orphaned."""
    on_disk = {json.loads(p.read_text())["id"] for p in (ROOT / "fixtures").rglob("*.task.json")}
    in_full = {json.loads(t.read_text())["id"] for t in load_suite("full")}
    assert on_disk == in_full, f"tasks not in any suite: {on_disk - in_full}"
