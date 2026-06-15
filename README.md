<h1 align="center">⚖️ CLI-Judge</h1>

<p align="center">
  <strong>Everyone is shipping AI tools. Almost nobody checks if they actually work.<br>
  CLI-Judge is the independent referee that does.</strong>
</p>

<p align="center">
  A <strong>reality-grounded</strong> benchmark + verification harness for agent-native CLIs, MCP servers, and software harnesses.<br>
  It doesn't grade how a tool <em>looks</em>. It replays <strong>real recorded situations</strong> and grades what the tool <em>does</em>.
</p>

<p align="center">
  <a href="#-quick-start"><img src="https://img.shields.io/badge/Quick_Start-3_min-blue?style=for-the-badge" alt="Quick Start"></a>
  <a href="RUBRIC.md"><img src="https://img.shields.io/badge/Scored_on-5_Dimensions_/_100-blueviolet?style=for-the-badge" alt="Rubric"></a>
  <a href="#-what-it-catches-from-real-bug-reports"><img src="https://img.shields.io/badge/Fixtures-945%2B_real_issues-orange?style=for-the-badge" alt="Fixtures"></a>
  <a href="#-quick-start"><img src="https://img.shields.io/badge/Tests-44_passing-brightgreen?style=for-the-badge" alt="Tests"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-Apache_2.0-yellow?style=for-the-badge" alt="License"></a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-≥3.10-blue?logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/deps-jsonschema_only-green" alt="Deps">
  <img src="https://img.shields.io/badge/offline-deterministic-blueviolet" alt="Offline">
  <img src="https://img.shields.io/badge/safety-Ed25519_receipts-red" alt="Safety">
  <img src="https://img.shields.io/github/stars/wjlgatech/cli-judge?style=social" alt="Stars">
</p>

---

## 🤔 Why CLI-Judge exists (explain it to a 15-year-old)

AI agents are starting to **do real things** for us — book stuff, edit files, call services. They don't click buttons like we do; they run little command-line programs called **tools**.

Two popular "factories" mass-produce these tools for agents: [**CLI Printing Press**](https://github.com/mvanhorn/cli-printing-press) and [**CLI-Anything**](https://github.com/HKUDS/CLI-Anything). They're great at *making* tools fast.

But here's the catch: **each factory grades its own homework — and it grades the wrong thing.** It checks whether the tool *looks* right (does the code have the right shapes and patterns?) instead of whether the tool *actually works* (does it give the correct answer, safely, when it meets the real world?).

> It's like a driving school that hands you a license for **correctly naming the parts of a car** — without ever checking whether you can drive down a real road without crashing. 🚗💥

So the tools pass their own tests… then break in real life: you ask for **page 2** and get page 1, the tool mistakes a password for the wrong kind of key, it spits out raw gibberish instead of clean data, it crashes on Windows — or it quietly runs a **hidden delete command** hidden inside a filename.

**CLI-Judge is the independent road test.** It doesn't build tools, and it doesn't trust their looks. It replays *real recorded situations* at each tool and grades the **result**: Did you get the right answer? Did you stay safe? Were you fast and cheap? Every single point is backed by evidence from a real interaction — distilled from **945+ real bug reports** these factories' own users actually filed.

That's the whole pitch you can give a stranger in 20 seconds:
> *"AI agents run tools. The people who make those tools grade their own homework on how the code looks — not whether it works. CLI-Judge is the referee that replays real situations and grades the real result, especially safety."*

---

## 💡 The 5 reasons, in one breath

1. **An agent is only as smart as its tools.** A broken tool quietly hands back wrong answers — and you trust them.
2. **Today's report cards grade looks, not results.** A scorecard that checks "is the pattern in the source?" can't catch the bug a real user just hit.
3. **You can't be the player *and* the referee.** A tool's own factory will never fail it the way an independent judge will.
4. **Real situations, real outcomes.** Every score traces to a real recorded request or a real run — never a guess, never "the code looks fine."
5. **Safety is non-negotiable.** One hidden destructive command can wreck a system, so an unsafe tool can **never** score above a C — no matter how correct or pretty it is.

---

## 🖼️ The problem in one picture

|  | Structure scorecards (today) | **CLI-Judge** (outcomes) |
|---|---|---|
| **Question it asks** | "Does the code *look* right?" | "Does the tool *work* right?" |
| **Evidence for a point** | a pattern exists in the source | a real replayed request / real run |
| **Catches the bug a user actually hit?** | ❌ usually not | ✅ that's the entire point |
| **Who's grading?** | the tool's own factory | an independent judge |
| **Pass it by editing a comment?** | yes 😬 | never |

---

## 🎯 How it scores: 5 dimensions, 100 points

Every tool is replayed against real fixtures and scored on five dimensions (full point tables in [`RUBRIC.md`](RUBRIC.md)):

| Dimension | What it measures | Pts | A real failure it catches |
|---|---|----:|---|
| **D1 · Correctness** | right *typed* output against a real captured payload | 35 | you ask for page 2, the tool sends a cursor instead of `skip=50` |
| **D2 · Non-interactive** | works piped, `--json`, no prompts, typed exit codes | 20 | the tool blocks forever waiting on a human who isn't there |
| **D3 · Cross-platform** | paths / locale / encoding, and **loud** failure when a backend is missing | 15 | a Windows path breaks and it silently emits wrong output |
| **D4 · Safety** 🛡️ | declares blast radius, gates destructive ops, signs receipts, blocks injection | 20 | a malicious filename smuggles in a hidden `os.system('…')` |
| **D5 · Efficiency** | tokens-per-task and latency vs a budget | 10 | `--compact` claims 70% smaller… but isn't |

> 🛡️ **Hard safety gate:** any safety **blocker** caps the final grade at **C** — an unsafe tool is never shippable, no matter how correct it is everywhere else.

---

## 🚀 Quick Start

```bash
cd harness
python3 -m venv .venv && source .venv/bin/activate
pip install -e .                     # one hard dependency: jsonschema

cli-judge validate ../fixtures       # check every fixture against its schema
cli-judge run --adapter examples/echo_adapter.py --suite full   # score a tool → report.json + scorecard.md + a letter grade
```

You get a human `scorecard.md`, a machine `report.json`, and a one-line verdict like `Grade: B (78.0/100)` — **deterministic**, **offline**, and traceable to real evidence. Point CLI-Judge at a real tool by writing a tiny [adapter](templates/adapter.template.py) (one `invoke(call) -> Result` function); ready-made adapters for the two factories live in [`harness/adapters/`](harness/adapters/).

---

## 🧪 What it catches (from real bug reports)

Every fixture is distilled from a **real, observed failure** in one of the two factories' public issue trackers — so the benchmark is auditable, not invented:

| Failure | Dimension | From a real issue |
|---|---|---|
| Pagination param drift (cursor vs `skip`/`limit`) | D1 | [cli-printing-press#2961](https://github.com/mvanhorn/cli-printing-press/issues/2961) |
| Short token misclassified as a JWT | D1 | [pp#1598](https://github.com/mvanhorn/cli-printing-press/issues/1598) |
| `--compact` leaks raw `map[...]` strings | D1 | [pp#2950](https://github.com/mvanhorn/cli-printing-press/issues/2950) |
| Non-interactive mode broken (blocks on a prompt) | D2 | [CLI-Anything#214](https://github.com/HKUDS/CLI-Anything/issues/214) |
| Headless LibreOffice crashes on macOS | D3 | [ca#221](https://github.com/HKUDS/CLI-Anything/issues/221) |
| Code injection via an unsanitized macro path | D4 | [ca#282](https://github.com/HKUDS/CLI-Anything/issues/282) |
| Token-file path traversal / symlink escape | D4 | [ca#304](https://github.com/HKUDS/CLI-Anything/issues/304) |

See the full list in [`fixtures/CATALOG.md`](fixtures/CATALOG.md).

---

## 🧭 The Reality Principle (the one rule)

> Every point CLI-Judge awards must trace to **(a)** the tool's real stdout/stderr/exit-code from an actual run, **(b)** its behavior replayed against a **recorded real payload**, or **(c)** an independently verifiable property of its declared capability envelope.
>
> A point is **never** awarded because "a pattern exists in the source code." That is exactly the trap CLI-Judge exists to escape.

The core suite runs **fully offline** against recorded fixtures (no network). Destructive-action tests are **record/assert only** — CLI-Judge never executes a dangerous command against a live system. Safe by construction.

---

## 📦 What's in the box

| Path | Purpose |
|---|---|
| [`SPEC.md`](SPEC.md) | The benchmark spec — dimensions, task format, fixture format |
| [`RUBRIC.md`](RUBRIC.md) | The 100-point rubric with exact point allocations and pass gates |
| [`harness/`](harness/) | The runnable reference harness — replay engine, 5 scorers, signed receipts, runner, CLI |
| [`fixtures/`](fixtures/) | Real-world failure fixtures distilled from the two issue trackers |
| [`schemas/`](schemas/) | JSON Schemas for tasks, fixtures, capability envelope, signed receipts |
| [`AGENTS.md`](AGENTS.md) | Build brief for coding agents — architecture, work breakdown, definition of done |
| [`docs/`](docs/) | Strategy, threat model, methodology, roadmap, FAQ |

---

## 🚫 Scope discipline (read this)

**CLI-Judge measures tools. It is *not* another generator and must never become one.** If a contribution adds a code generator, it's out of scope. The defensible position — the whole reason this exists — is being the **referee**, not a third player on the field.

---

## 📜 License

[Apache-2.0](LICENSE). Built to be cited, forked, and run against anyone's tools — including ours.

<p align="center"><em>AI agents are only as trustworthy as the tools they run.<br>CLI-Judge is how you find out which ones to trust.</em></p>
