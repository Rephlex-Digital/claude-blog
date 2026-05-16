"""Smoke tests for scripts/cognitive_load.py.

Covers:
1. Happy path: a markdown post with H2 sections produces a valid JSON report
   with per-section load scores and a healthy overall verdict.
2. Empty input: a file with no H2 sections still produces parseable JSON
   without crashing.
3. Overloaded path: a synthetically dense section is flagged as overloaded.

Stdlib only. No network. Subprocess invocation matches the documented CLI.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "cognitive_load.py"


def _run(post_path: Path) -> dict:
    """Invoke the CLI with --format json and return the parsed payload."""
    result = subprocess.run(
        [sys.executable, str(SCRIPT), str(post_path), "--format", "json"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, f"non-zero exit: stderr={result.stderr!r}"
    return json.loads(result.stdout)


def test_happy_path_low_load(tmp_path: Path) -> None:
    """A plain post with simple sections should be classified Healthy."""
    post = tmp_path / "happy.md"
    post.write_text(
        "---\ntitle: Test\n---\n\n"
        "## Why This Matters\n\n"
        "Most readers want simple explanations. We keep things short. "
        "We use plain words and one idea per paragraph.\n\n"
        "## What To Do\n\n"
        "Start with the obvious step. Watch what happens. Adjust if needed.\n",
        encoding="utf-8",
    )
    report = _run(post)
    assert report["verdict"] in {"Healthy", "Moderate"}
    assert report["section_count"] >= 2
    assert report["overall_load"] >= 0


def test_empty_post_no_crash(tmp_path: Path) -> None:
    """A post with no H2 sections must not crash and must return JSON."""
    post = tmp_path / "empty.md"
    post.write_text("Just one paragraph with no headings.\n", encoding="utf-8")
    report = _run(post)
    assert "verdict" in report
    assert "sections" in report
    assert isinstance(report["sections"], list)


def test_overloaded_section_flagged(tmp_path: Path) -> None:
    """A dense section with many entities, numerics, and jargon should be flagged."""
    post = tmp_path / "dense.md"
    body = (
        "## Methodology\n\n"
        "We tested Acme Corp, Globex Inc, Initech Systems, Umbrella Labs, "
        "Hooli Networks, Pied Piper Tech, Stark Industries, Wayne Enterprises, "
        "and 7 other firms in 2024. Adoption hit 87.3%, retention reached "
        "92.1%, churn dropped to 3.5%, NPS reached 67. Schema markup, "
        "structured data, e-e-a-t, geo, aeo, burstiness, ttr, hreflang, "
        "canonical, robots.txt, indexability all moved together, which is "
        "what we will see later when we discuss the second-order analysis, "
        "though as we will see in the next section the results vary, since "
        "while X happened also Y emerged because the underlying patterns shifted.\n"
    )
    post.write_text(body, encoding="utf-8")
    report = _run(post)
    methodology = next(
        s for s in report["sections"] if "Methodology" in s["heading"]
    )
    assert methodology["load_score"] > 0
    assert methodology["new_entities"] >= 5
    assert methodology["numeric_claims"] >= 4


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
