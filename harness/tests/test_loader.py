from pathlib import Path
from atb.loader import validate_dir, load_suite, ROOT


def test_all_fixtures_valid():
    errs = validate_dir(str(ROOT / "fixtures"))
    assert errs == [], "\n".join(errs)


def test_core_suite_nonempty():
    tasks = load_suite("core")
    assert len(tasks) >= 1
    ids = [Path(t).name for t in tasks]
    assert any("pagination" in i for i in ids)
