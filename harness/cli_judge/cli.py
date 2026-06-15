"""CLI-Judge command-line entrypoint. Status: WIRED."""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

from .loader import validate_dir, ROOT
from .runner import run_suite


def main(argv=None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    p = argparse.ArgumentParser(prog="cli-judge", description="CLI-Judge: reality-grounded tool benchmark")
    sub = p.add_subparsers(dest="cmd", required=True)

    pv = sub.add_parser("validate", help="validate tasks/fixtures against schemas")
    pv.add_argument("dir", nargs="?", default=str(ROOT / "fixtures"))

    pr = sub.add_parser("run", help="run a suite against an adapter")
    pr.add_argument("--adapter", required=True)
    pr.add_argument("--suite", default="core")
    pr.add_argument("--out", default=".")

    sub.add_parser("selftest", help="run the echo adapter through the core suite")

    args = p.parse_args(argv)

    if args.cmd == "validate":
        errs = validate_dir(args.dir)
        if errs:
            for e in errs:
                print("INVALID:", e, file=sys.stderr)
            print(f"{len(errs)} invalid file(s).", file=sys.stderr)
            return 1
        print("All tasks/fixtures valid.")
        return 0

    if args.cmd == "run":
        report = run_suite(args.adapter, args.suite)
        outdir = Path(args.out)
        outdir.mkdir(parents=True, exist_ok=True)
        scorecard = report.pop("_scorecard_md")
        (outdir / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
        (outdir / "scorecard.md").write_text(scorecard, encoding="utf-8")
        print(scorecard)
        print(f"Grade: {report['grade']} ({report['score']}/100)")
        return 0 if report["grade"] not in ("F",) else 2

    if args.cmd == "selftest":
        adapter = str(ROOT / "harness" / "examples" / "echo_adapter.py")
        report = run_suite(adapter, "core")
        report.pop("_scorecard_md", None)
        print(json.dumps({"grade": report["grade"], "score": report["score"]}, indent=2))
        return 0

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
