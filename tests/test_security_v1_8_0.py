"""Security regression tests for v1.8.0 defenses.

Covers:
1. Path traversal: scripts must refuse to read symlinks.
2. DoS: scripts must enforce MAX_*_BYTES size caps.
3. JSON schema: discourse_research.py must reject malformed input items.
4. Output path: discourse_research.py must refuse overwriting symlinks.
5. Prompt-injection guard: skills/blog/SKILL.md must instruct the orchestrator
   to fence project-root files (BRAND.md / VOICE.md / DISCOURSE.md).

Stdlib + pytest only. No network. All file ops use tmp_path.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
COGNITIVE = ROOT / "scripts" / "cognitive_load.py"
DISCOURSE = ROOT / "scripts" / "discourse_research.py"


def _run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, capture_output=True, text=True, check=False)


# ---------------------------------------------------------------------------
# Path traversal / symlink refusal
# ---------------------------------------------------------------------------


def test_cognitive_load_refuses_symlink_input(tmp_path: Path) -> None:
    """A symlink as input must be refused (CWE-59 defense)."""
    real_target = tmp_path / "real.md"
    real_target.write_text("## section\nbody\n", encoding="utf-8")
    symlink = tmp_path / "link.md"
    os.symlink(real_target, symlink)
    result = _run([sys.executable, str(COGNITIVE), str(symlink)])
    assert result.returncode != 0
    assert "symlink" in result.stderr.lower()


def test_discourse_research_refuses_symlink_input(tmp_path: Path) -> None:
    real_target = tmp_path / "real.json"
    real_target.write_text("[]", encoding="utf-8")
    symlink = tmp_path / "link.json"
    os.symlink(real_target, symlink)
    result = _run([
        sys.executable, str(DISCOURSE),
        "--input", str(symlink),
        "--topic", "test",
        "--format", "json",
    ])
    assert result.returncode != 0
    assert "symlink" in result.stderr.lower()


def test_discourse_research_refuses_symlink_output(tmp_path: Path) -> None:
    """An existing-symlink as --output must be refused so attacker symlinks
    cannot redirect writes to /etc/cron.d or similar."""
    real_target = tmp_path / "real_target.md"
    real_target.write_text("placeholder\n", encoding="utf-8")
    symlink_output = tmp_path / "DISCOURSE.md"
    os.symlink(real_target, symlink_output)
    inp = tmp_path / "results.json"
    inp.write_text("[]", encoding="utf-8")
    result = _run([
        sys.executable, str(DISCOURSE),
        "--input", str(inp),
        "--topic", "test",
        "--output", str(symlink_output),
    ])
    assert result.returncode != 0
    assert "symlink" in result.stderr.lower()


def test_discourse_research_refuses_nonexistent_output_dir(tmp_path: Path) -> None:
    inp = tmp_path / "results.json"
    inp.write_text("[]", encoding="utf-8")
    bogus_dir = tmp_path / "does" / "not" / "exist"
    result = _run([
        sys.executable, str(DISCOURSE),
        "--input", str(inp),
        "--topic", "test",
        "--output", str(bogus_dir / "DISCOURSE.md"),
    ])
    assert result.returncode != 0
    assert "directory does not exist" in result.stderr.lower()


# ---------------------------------------------------------------------------
# DoS: size caps
# ---------------------------------------------------------------------------


def test_cognitive_load_refuses_oversize_input(tmp_path: Path) -> None:
    """An input file over MAX_INPUT_BYTES (10MB) must be refused."""
    big = tmp_path / "huge.md"
    # 11 MB of zeros
    big.write_bytes(b"# title\n" + b"x" * (11 * 1024 * 1024))
    result = _run([sys.executable, str(COGNITIVE), str(big)])
    assert result.returncode != 0
    assert "size cap" in result.stderr.lower()


def test_discourse_research_refuses_oversize_input(tmp_path: Path) -> None:
    big = tmp_path / "huge.json"
    # 26 MB JSON array of empty objects
    big.write_text("[" + "{}," * (1_000_000) + "{}]", encoding="utf-8")
    if big.stat().st_size < 25 * 1024 * 1024:
        pytest.skip("test fixture too small; OS limit unexpected")
    result = _run([
        sys.executable, str(DISCOURSE),
        "--input", str(big),
        "--topic", "test",
        "--format", "json",
    ])
    assert result.returncode != 0
    assert "size cap" in result.stderr.lower()


# ---------------------------------------------------------------------------
# JSON schema validation
# ---------------------------------------------------------------------------


def test_discourse_research_rejects_non_array_input(tmp_path: Path) -> None:
    inp = tmp_path / "not_array.json"
    inp.write_text('{"not": "an array"}', encoding="utf-8")
    result = _run([
        sys.executable, str(DISCOURSE),
        "--input", str(inp),
        "--topic", "test",
    ])
    assert result.returncode != 0
    assert "must be a json array" in result.stderr.lower()


def test_discourse_research_rejects_item_missing_required_fields(tmp_path: Path) -> None:
    inp = tmp_path / "malformed.json"
    inp.write_text(json.dumps([{"platform": "reddit"}]), encoding="utf-8")  # missing url/title/snippet
    result = _run([
        sys.executable, str(DISCOURSE),
        "--input", str(inp),
        "--topic", "test",
    ])
    assert result.returncode != 0
    assert "missing required fields" in result.stderr.lower()


def test_discourse_research_rejects_too_many_items(tmp_path: Path) -> None:
    """MAX_ITEMS cap prevents pathological clustering complexity."""
    items = [
        {"platform": "web", "url": f"https://x.com/{i}", "title": f"t{i}", "snippet": "s"}
        for i in range(10_001)
    ]
    inp = tmp_path / "too_many.json"
    inp.write_text(json.dumps(items), encoding="utf-8")
    result = _run([
        sys.executable, str(DISCOURSE),
        "--input", str(inp),
        "--topic", "test",
    ])
    assert result.returncode != 0
    assert "exceeds cap" in result.stderr.lower()


# ---------------------------------------------------------------------------
# Prompt-injection guard documentation (orchestrator contract)
# ---------------------------------------------------------------------------


def test_orchestrator_has_untrusted_data_contract() -> None:
    """skills/blog/SKILL.md must document the project-root file fencing contract.

    Regression guard: if this section is ever removed or weakened, the
    indirect prompt-injection defense for BRAND.md / VOICE.md / DISCOURSE.md
    auto-load is gone. The section must mention all three files and the
    'untrusted-data' / 'fence' concepts.
    """
    orchestrator = (ROOT / "skills" / "blog" / "SKILL.md").read_text(encoding="utf-8")
    assert "Untrusted-Data Contract" in orchestrator, (
        "skills/blog/SKILL.md is missing the 'Untrusted-Data Contract' section "
        "that fences project-root files against prompt injection."
    )
    for f in ("BRAND.md", "VOICE.md", "DISCOURSE.md"):
        assert f in orchestrator, f"orchestrator does not mention {f}"
    # Must instruct fencing
    assert "BEGIN UNTRUSTED PROJECT-ROOT CONTEXT" in orchestrator, (
        "orchestrator does not specify the fence-block format for untrusted "
        "project-root content."
    )
    # Must instruct sanitization
    assert "ignore previous" in orchestrator.lower(), (
        "orchestrator does not list the 'ignore previous' injection pattern "
        "in its sanitization scan."
    )


def test_security_md_documents_t12() -> None:
    """SECURITY.md must include the T12 trust boundary (project-root auto-load)."""
    sec = (ROOT / "SECURITY.md").read_text(encoding="utf-8")
    assert "T12" in sec, "SECURITY.md missing T12 trust boundary"
    assert "BRAND.md" in sec and "DISCOURSE.md" in sec, (
        "SECURITY.md T12 section missing references to BRAND.md / DISCOURSE.md"
    )


# ---------------------------------------------------------------------------
# License compliance (regression guard)
# ---------------------------------------------------------------------------


def test_notice_file_exists_and_credits_apache_sources() -> None:
    """NOTICE file must exist and credit impeccable (Apache 2.0)."""
    notice = ROOT / "NOTICE"
    assert notice.exists(), "NOTICE file is missing (required for Apache 2.0 attribution)"
    text = notice.read_text(encoding="utf-8")
    assert "impeccable" in text, "NOTICE does not credit impeccable"
    assert "Paul Bakaus" in text, "NOTICE does not credit Paul Bakaus"
    assert "Apache License" in text or "Apache 2.0" in text, (
        "NOTICE does not reference the Apache License"
    )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
