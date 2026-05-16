#!/usr/bin/env python3
"""
Discourse Research: Synthesis Helper for /blog discourse

Consumes a JSON file of pre-gathered SERP / WebSearch results and produces:
1. A DISCOURSE.md brief at the requested output path
2. Structured JSON on stdout (when --format json)

This script does NOT call any external APIs or perform searches. It expects the
search to have been performed upstream (by Claude via WebSearch, or by another
process) and the results to be passed in as JSON.

Adapted from the methodology of last30days-skill v3.2.1 (Matt Van Horn, MIT,
github.com/mvanhorn/last30days-skill). The upstream uses platform APIs; this
script uses pre-gathered WebSearch results.

Input JSON schema:
    [
      {
        "platform": "reddit" | "hackernews" | "x" | "youtube" | "devto" | "medium"
                  | "github" | "stackoverflow" | "substack" | "web",
        "url": "https://...",
        "title": "Title as visible in SERP / source",
        "snippet": "Snippet text",
        "date": "YYYY-MM-DD" | null,
        "engagement_proxy": "upvotes / likes / views as visible" | null
      },
      ...
    ]

Usage:
    python discourse_research.py --input results.json --topic "topic" \\
        --days 30 --output DISCOURSE.md
    python discourse_research.py --input results.json --topic "topic" \\
        --format json     # prints JSON brief to stdout, no file output
    python discourse_research.py --input - --topic "topic" --days 90   # stdin

Output JSON schema:
    {
      "topic": "...",
      "window_days": 30,
      "generated": "YYYY-MM-DD",
      "platform_breakdown": { "reddit": N, "x": M, ... },
      "themes_new": [ { "theme": "...", "claim": "...", "sources": [...] } ],
      "themes_consensus": [ { "theme": "...", "claim": "...", "sources": [...] } ],
      "themes_contrarian": [ ... ],
      "specifics": [ ... ],
      "source_count": N,
      "useful_count": M
    }

The script enforces LAW 2 (no invented titles -- titles come verbatim from
input data; never paraphrased), LAW 3 (no em-dashes in output), and LAW 5
(every source is rendered as inline markdown link [name](url)).
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

PLATFORM_LABELS = {
    "reddit": "Reddit",
    "hackernews": "Hacker News",
    "hn": "Hacker News",
    "x": "X / Twitter",
    "twitter": "X / Twitter",
    "youtube": "YouTube",
    "devto": "dev.to",
    "dev.to": "dev.to",
    "medium": "Medium",
    "github": "GitHub",
    "stackoverflow": "Stack Overflow",
    "substack": "Substack",
    "bluesky": "Bluesky",
    "web": "Web",
}

# Stopwords for theme keyword extraction
STOPWORDS = {
    "the", "a", "an", "and", "or", "but", "if", "in", "on", "at", "of", "for",
    "to", "with", "by", "as", "is", "are", "was", "were", "be", "been", "being",
    "this", "that", "these", "those", "it", "its", "they", "them", "their",
    "i", "you", "he", "she", "we", "us", "our", "my", "your", "his", "her",
    "from", "into", "out", "up", "down", "all", "any", "each", "more", "most",
    "some", "such", "no", "not", "only", "own", "same", "so", "than", "too",
    "very", "can", "will", "just", "don", "should", "now", "about",
}

EM_DASH_REPLACEMENTS = {
    "—": " - ",  # em-dash
    "–": " - ",  # en-dash
    " -- ": " - ",
}


def strip_em_dashes(text: str) -> str:
    """Apply LAW 3: no em-dashes or en-dashes in output."""
    for old, new in EM_DASH_REPLACEMENTS.items():
        text = text.replace(old, new)
    return text


# ---------------------------------------------------------------------------
# Parsing input
# ---------------------------------------------------------------------------

MAX_INPUT_BYTES = 25 * 1024 * 1024   # 25 MB cap on results JSON (DoS guard)
MAX_DECOMP_BYTES = 256 * 1024        # 256 KB cap on decomposition file
MAX_ITEMS = 10_000                   # cap on items in results array
MAX_STDIN_BYTES = 25 * 1024 * 1024   # cap on stdin reads

REQUIRED_FIELDS = {"platform", "url", "title", "snippet"}
OPTIONAL_FIELDS = {"date", "engagement_proxy"}


def _validate_input_path(path: Path, max_bytes: int, label: str) -> Path:
    """Validate a CLI file path. Closes path-traversal, symlink, and DoS vectors."""
    if not path.exists():
        raise FileNotFoundError(f"{label} not found: {path}")
    if path.is_symlink():
        raise ValueError(
            f"{label} is a symlink; refusing to follow for safety: {path}"
        )
    if not path.is_file():
        raise ValueError(f"{label} is not a regular file: {path}")
    size = path.stat().st_size
    if size > max_bytes:
        raise ValueError(
            f"{label} exceeds size cap ({size} bytes > {max_bytes}): {path}"
        )
    return path


def _validate_output_path(path_str: str) -> Path:
    """Validate an output path. Refuses overwriting symlinks; ensures parent dir exists."""
    out = Path(path_str)
    if out.exists() and out.is_symlink():
        raise ValueError(
            f"Output path is a symlink; refusing to overwrite for safety: {out}"
        )
    if out.exists() and not out.is_file():
        raise ValueError(f"Output path exists but is not a regular file: {out}")
    if not out.parent.exists():
        raise ValueError(f"Output directory does not exist: {out.parent}")
    return out


def _validate_item(item: Any, index: int) -> dict[str, Any]:
    """Validate one result item against the JSON schema. Returns the item if valid."""
    if not isinstance(item, dict):
        raise ValueError(f"Result item {index} is not an object: got {type(item).__name__}")
    missing = REQUIRED_FIELDS - set(item.keys())
    if missing:
        raise ValueError(
            f"Result item {index} missing required fields: {sorted(missing)}"
        )
    return item


def load_results(input_path: str) -> list[dict[str, Any]]:
    """Load and validate a JSON array of result objects.

    Source: file path or stdin ('-'). Enforces size cap, schema, and item count
    to defend against DoS and malformed-input crashes.
    """
    if input_path == "-":
        raw = sys.stdin.read(MAX_STDIN_BYTES + 1)
        if len(raw) > MAX_STDIN_BYTES:
            raise ValueError(f"stdin input exceeds size cap ({MAX_STDIN_BYTES} bytes)")
    else:
        validated = _validate_input_path(Path(input_path), MAX_INPUT_BYTES, "Input file")
        raw = validated.read_text(encoding="utf-8")
    if not raw.strip():
        return []
    data = json.loads(raw)
    if not isinstance(data, list):
        raise ValueError("Input must be a JSON array of result objects.")
    if len(data) > MAX_ITEMS:
        raise ValueError(
            f"Result array length {len(data)} exceeds cap ({MAX_ITEMS})"
        )
    return [_validate_item(item, i) for i, item in enumerate(data)]
    return data


def parse_date(value: Any) -> dt.date | None:
    if not value:
        return None
    if isinstance(value, dt.date):
        return value
    if isinstance(value, str):
        for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%m/%d/%Y", "%b %d, %Y"):
            try:
                return dt.datetime.strptime(value.strip(), fmt).date()
            except ValueError:
                continue
    return None


def parse_engagement(value: Any) -> int:
    """Best-effort numeric parse of engagement strings like '1.2k', '450 upvotes'."""
    if value is None:
        return 0
    if isinstance(value, (int, float)):
        return int(value)
    s = str(value).lower().replace(",", "")
    m = re.search(r"(\d+(?:\.\d+)?)\s*([kmb]?)", s)
    if not m:
        return 0
    n = float(m.group(1))
    suffix = m.group(2)
    multiplier = {"k": 1_000, "m": 1_000_000, "b": 1_000_000_000}.get(suffix, 1)
    return int(n * multiplier)


# ---------------------------------------------------------------------------
# Scoring and theming
# ---------------------------------------------------------------------------


def score_item(item: dict[str, Any], today: dt.date, window_days: int) -> float:
    """Combined recency (60%) + engagement (40%) score in [0, 100]."""
    date = parse_date(item.get("date"))
    if date is None:
        recency_score = 30.0  # unknown date - middling
    else:
        age_days = max(0, (today - date).days)
        if age_days > window_days * 3:
            recency_score = 0.0
        else:
            recency_score = max(0.0, 60.0 * (1 - age_days / (window_days * 3)))

    engagement = parse_engagement(item.get("engagement_proxy"))
    if engagement == 0:
        engagement_score = 5.0  # unknown - middling-low
    else:
        # log-scale; 10 = 8 pts, 100 = 16, 1000 = 24, 10000 = 32, 100000 = 40
        import math
        engagement_score = min(40.0, 8.0 * math.log10(max(10, engagement)))
    return round(recency_score + engagement_score, 1)


def extract_theme_keywords(text: str, topic_tokens: set[str], top_n: int = 5) -> list[str]:
    """Extract candidate theme keywords from a title or snippet."""
    words = re.findall(r"\b[A-Za-z][A-Za-z0-9\-]{2,}\b", text.lower())
    candidates = [
        w for w in words
        if w not in STOPWORDS and w not in topic_tokens and len(w) >= 4
    ]
    seen = set()
    out = []
    for w in candidates:
        if w not in seen:
            seen.add(w)
            out.append(w)
        if len(out) >= top_n:
            break
    return out


def cluster_by_theme(
    items: list[dict[str, Any]],
    topic: str,
) -> list[dict[str, Any]]:
    """Bucket items by shared keyword themes."""
    topic_tokens = set(topic.lower().split())
    keyword_to_items: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in items:
        text = f"{item.get('title', '')} {item.get('snippet', '')}"
        for kw in extract_theme_keywords(text, topic_tokens):
            keyword_to_items[kw].append(item)

    clusters = []
    used_urls: set[str] = set()
    for kw, group in sorted(
        keyword_to_items.items(),
        key=lambda kv: (-len(kv[1]), kv[0]),
    ):
        unique_group = [g for g in group if g.get("url") not in used_urls]
        if len(unique_group) < 1:
            continue
        for g in unique_group:
            used_urls.add(g.get("url", ""))
        clusters.append({"theme": kw, "items": unique_group})
    return clusters


def classify_clusters(
    clusters: list[dict[str, Any]],
    today: dt.date,
    window_days: int,
) -> dict[str, list[dict[str, Any]]]:
    """Sort clusters into NEW / CONSENSUS / CONTRARIAN / SPECIFICS buckets."""
    new_themes = []
    consensus_themes = []
    contrarian_themes = []
    specifics = []

    for cluster in clusters:
        platforms = {i.get("platform") for i in cluster["items"]}
        item_count = len(cluster["items"])
        recent_count = sum(
            1
            for i in cluster["items"]
            if (d := parse_date(i.get("date"))) and (today - d).days <= window_days
        )
        if recent_count >= 2 and len(platforms) >= 2:
            consensus_themes.append(cluster)
        elif recent_count >= 1 and item_count == 1:
            contrarian_themes.append(cluster)
        elif recent_count >= 1:
            new_themes.append(cluster)
        if any(
            re.search(r"(command|config|setup|fix|workaround|how to|step|version|`)", i.get("snippet", "").lower())
            for i in cluster["items"]
        ):
            specifics.extend(cluster["items"])

    # Dedup specifics by URL, cap at 5
    seen = set()
    specifics_unique = []
    for s in specifics:
        u = s.get("url")
        if u and u not in seen:
            seen.add(u)
            specifics_unique.append(s)
        if len(specifics_unique) >= 5:
            break

    return {
        "new": new_themes[:5],
        "consensus": consensus_themes[:4],
        "contrarian": contrarian_themes[:3],
        "specifics": specifics_unique,
    }


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------


def render_inline_link(item: dict[str, Any]) -> str:
    """LAW 5: every citation as [name](url). LAW 2: never invent titles."""
    url = item.get("url", "")
    title = item.get("title") or item.get("platform", "source")
    platform = item.get("platform", "")
    label = PLATFORM_LABELS.get(platform, platform.capitalize()) if platform else ""
    name = title[:80]
    if label and label.lower() not in name.lower():
        name = f"{name} ({label})"
    if not url:
        return name
    return f"[{name}]({url})"


def render_cluster_paragraph(cluster: dict[str, Any]) -> str:
    items = cluster["items"]
    theme = cluster["theme"].replace("-", " ").title()
    sources = ", ".join(render_inline_link(i) for i in items[:3])
    sample_snippet = (items[0].get("snippet") or "")[:200].strip()
    sample_snippet = strip_em_dashes(sample_snippet)
    if sample_snippet:
        body = f"{sample_snippet} Cited in {sources}."
    else:
        body = f"Cited across {sources}."
    return f"- **{theme}.** {body}"


def render_markdown(
    topic: str,
    window_days: int,
    generated: dt.date,
    buckets: dict[str, list[dict[str, Any]]],
    items: list[dict[str, Any]],
    decomposition: list[str] | None,
) -> str:
    platform_counts: dict[str, int] = defaultdict(int)
    for item in items:
        platform_counts[item.get("platform") or "web"] += 1
    platforms_used = len([p for p, c in platform_counts.items() if c > 0])

    lines = [
        f"# Discourse Brief: {topic}",
        "",
        f"> Generated {generated.isoformat()} via /blog discourse. "
        f"Window: last {window_days} days. "
        f"Sources scanned: {len(items)} across {platforms_used} platforms.",
        "",
    ]
    if decomposition:
        lines.append("## Decomposition")
        lines.append("")
        for i, q in enumerate(decomposition, 1):
            lines.append(f"{i}. {q}")
        lines.append("")

    lines.append(f"## What's NEW in the last {window_days} days")
    lines.append("")
    if buckets["new"]:
        for cluster in buckets["new"]:
            lines.append(render_cluster_paragraph(cluster))
    else:
        lines.append("- No distinctly new themes detected in the window. Consider widening to --days 90.")
    lines.append("")

    lines.append("## Consensus across platforms")
    lines.append("")
    if buckets["consensus"]:
        for cluster in buckets["consensus"]:
            lines.append(render_cluster_paragraph(cluster))
    else:
        lines.append("- No cross-platform consensus themes detected.")
    lines.append("")

    lines.append("## Contrarian / minority takes")
    lines.append("")
    if buckets["contrarian"]:
        for cluster in buckets["contrarian"]:
            lines.append(render_cluster_paragraph(cluster))
    else:
        lines.append("- None surfaced. Absence is honest; do not invent contrarian takes.")
    lines.append("")

    lines.append("## Practitioner specifics (commands, configs, links)")
    lines.append("")
    if buckets["specifics"]:
        for item in buckets["specifics"]:
            snippet = strip_em_dashes((item.get("snippet") or "").strip())
            lines.append(f"- {render_inline_link(item)}: {snippet[:160]}")
    else:
        lines.append("- No concrete practitioner specifics surfaced in the window.")
    lines.append("")

    lines.append("## Source breakdown")
    lines.append("")
    lines.append("| Platform | Sources scanned |")
    lines.append("|---|---|")
    for platform, count in sorted(platform_counts.items(), key=lambda kv: -kv[1]):
        label = PLATFORM_LABELS.get(platform, platform.capitalize())
        lines.append(f"| {label} | {count} |")
    lines.append("")
    return strip_em_dashes("\n".join(lines))


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def build_brief(
    items: list[dict[str, Any]],
    topic: str,
    window_days: int,
    today: dt.date,
    decomposition: list[str] | None = None,
) -> dict[str, Any]:
    """Build the structured-JSON brief."""
    for item in items:
        item["_score"] = score_item(item, today, window_days)
    items_sorted = sorted(items, key=lambda i: -i.get("_score", 0))

    clusters = cluster_by_theme(items_sorted, topic)
    buckets = classify_clusters(clusters, today, window_days)
    markdown = render_markdown(topic, window_days, today, buckets, items_sorted, decomposition)

    def cluster_summary(c: dict[str, Any]) -> dict[str, Any]:
        return {
            "theme": c["theme"],
            "item_count": len(c["items"]),
            "sources": [
                {"platform": i.get("platform"), "url": i.get("url"), "title": i.get("title")}
                for i in c["items"][:3]
            ],
        }

    platform_breakdown: dict[str, int] = defaultdict(int)
    for item in items_sorted:
        platform_breakdown[item.get("platform") or "web"] += 1

    return {
        "topic": topic,
        "window_days": window_days,
        "generated": today.isoformat(),
        "source_count": len(items_sorted),
        "platform_breakdown": dict(platform_breakdown),
        "themes_new": [cluster_summary(c) for c in buckets["new"]],
        "themes_consensus": [cluster_summary(c) for c in buckets["consensus"]],
        "themes_contrarian": [cluster_summary(c) for c in buckets["contrarian"]],
        "specifics_count": len(buckets["specifics"]),
        "markdown": markdown,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--input", required=True, help="Path to results JSON, or '-' for stdin")
    parser.add_argument("--topic", required=True, help="Original topic string")
    parser.add_argument("--days", type=int, default=30, help="Freshness window in days (default 30)")
    parser.add_argument("--output", default=None, help="Path to write DISCOURSE.md (default: stdout markdown)")
    parser.add_argument(
        "--format", choices=["markdown", "json"], default="markdown",
        help="Output format when not writing to --output",
    )
    parser.add_argument(
        "--decomposition", default=None,
        help="Optional path to a newline-delimited file of decomposition questions",
    )
    args = parser.parse_args()

    try:
        items = load_results(args.input)
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2
    except json.JSONDecodeError as e:
        print(f"Error: input is not valid JSON: {e}", file=sys.stderr)
        return 2
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2

    decomposition: list[str] | None = None
    if args.decomposition:
        try:
            decomp_path = _validate_input_path(
                Path(args.decomposition), MAX_DECOMP_BYTES, "Decomposition file"
            )
            decomposition = [
                line.strip()
                for line in decomp_path.read_text(encoding="utf-8").splitlines()
                if line.strip()
            ]
        except (FileNotFoundError, ValueError) as e:
            print(f"Warning: {e}; proceeding without decomposition.", file=sys.stderr)

    brief = build_brief(items, args.topic, args.days, dt.date.today(), decomposition)

    if args.output:
        try:
            out_path = _validate_output_path(args.output)
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            return 2
        out_path.write_text(brief["markdown"], encoding="utf-8")
        print(json.dumps({k: v for k, v in brief.items() if k != "markdown"}, indent=2))
    elif args.format == "json":
        print(json.dumps(brief, indent=2))
    else:
        print(brief["markdown"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
