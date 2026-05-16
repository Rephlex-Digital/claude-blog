# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.8.0] - 2026-05-16

### Methodology ports from impeccable (Paul Bakaus, Apache 2.0)

Four editorial methodologies adapted from the impeccable frontend-design plugin
(`github.com/pbakaus/impeccable` v3.1.1). Impeccable polishes UIs; this release
applies the same mental models to prose. No code is copied verbatim; only the
mental models. See `CONTRIBUTORS.md` for the full attribution.

#### Added

- **`skills/blog/references/ai-slop-detection.md`**: two-tier reflex
  methodology for catching AI-generated structural tics that survive the
  vocabulary blocklist. First-order = phrase + lexical (existing). Second-order
  = structural and rhythmic (new): question-cadence H2s, three-clause sentence
  rhythm, hedge stacking, symmetric list bloat, wrap-up rhetorical questions,
  capsule H2 transitions, "key insight" sentence openers, listicle intro bloat,
  paragraph-shape flatness. A draft is "AI-detection clean" only when both
  tiers pass.
- **`skills/blog/references/editorial-heuristics.md`**: ordinal 0-4 rubric
  with P0-P3 severity tags. Parallel to (not replacing) the 100-point score.
  Translates Nielsen's 10 Usability Heuristics into editorial heuristics
  (e.g. "Error prevention" -> "Fabricated-stat prevention"; "Recognition
  rather than recall" -> "Reader does not memorize"). Exposed via
  `/blog analyze --rubric`.
- **`skills/blog/references/cognitive-load.md`** + **`scripts/cognitive_load.py`**
 : per-section concept-density analyzer. Measures new-entity density, numeric
  claim density, jargon introductions, forward references, and average clause
  depth. Identifies overloaded H2 sections (composite load score >= 50).
  Exposed via `/blog analyze --cognitive-load`.
- **`skills/blog-brand/` (new sub-skill)**: generates `BRAND.md` and
  `VOICE.md` at the project root. When present, all blog sub-skills auto-load
  these files at the start of any drafting / reviewing / scoring command.
  Commands: `/blog brand init|show|update`. Editorial analog of impeccable's
  PRODUCT.md / DESIGN.md context-loading pattern. Backward-compatible: absent
  files = unchanged v1.7.1 behavior.
- **`tests/test_cognitive_load.py`**: happy path + empty input regression
  test for the new analyzer.

#### Changed

- `skills/blog-rewrite/SKILL.md`: anti-AI scrub now invokes the two-tier
  check. Tier 2 runs after Tier 1 in Phase 1, step 3.
- `agents/blog-reviewer.md`: AI Content Detection section gains a
  Second-Order Structural Reflex subsection with 13 specific patterns to flag.
- `skills/blog-analyze/SKILL.md`: adds `--rubric` and `--cognitive-load`
  flags. Default behavior unchanged. JSON output schema preserved; new
  fields are additive (`rubric`, `cognitive_load`).
- `skills/blog/SKILL.md`: orchestrator now auto-loads `BRAND.md` and
  `VOICE.md` when present at the project root, injecting contents into
  downstream agent prompts. Adds `blog-brand` to routing table, sub-skills
  table, and quick reference. Adds three new reference files to the
  on-demand load list. Version bumped to 1.8.0.
- `.claude-plugin/plugin.json`: version 1.8.0; sub-skill count 28 -> 30;
  description extended with v1.8.0 features.

### Methodology adaptation from last30days-skill (Matt Van Horn, MIT)

Three research-discipline methodologies adapted from `last30days-skill` v3.2.1
(`github.com/mvanhorn/last30days-skill`). The upstream is a multi-platform
discourse engine (Reddit / X / YouTube / TikTok / Hacker News / Polymarket /
GitHub / Bluesky / etc.) that depends on platform APIs. This release ports the
RESEARCH METHODOLOGY only; no API plumbing is copied. Everything runs API-free
via WebSearch with platform-targeted site operators.

#### Added

- `skills/blog-discourse/SKILL.md`: new user-invokable sub-skill. Researches
  "what are people actually saying about <topic> in the last 30 days" across
  Reddit / Hacker News / X / YouTube / dev.to / Medium / GitHub / Stack
  Overflow / Substack / Bluesky via WebSearch + site operators. Produces
  `DISCOURSE.md` at project root with NEW themes, cross-platform consensus,
  contrarian takes, practitioner specifics, and source breakdown. Composes
  with `/blog brief | write | strategy` via `--feed-into <command>`.
- `scripts/discourse_research.py`: CLI helper that consumes a JSON array of
  pre-gathered SERP results and emits the structured brief. Applies LAW 2
  (no invented titles), LAW 3 (strips em-dashes / en-dashes), LAW 5 (inline
  `[name](url)` citations), and cross-source clustering. Stdlib only.
- `skills/blog/references/research-quality.md`: 5-dimension research-output
  rubric (groundedness 30, specificity 25, coverage 20, actionability 15,
  format 10), four pre-flight keyword-trap classes (demographic shopping,
  numeric trap, overly-literal phrase, generic single-noun), named-entity
  decomposition pattern (Step 0.55), cross-source clustering procedure, and
  freshness floor table (30-day for time-sensitive, 90-day for evergreen).
- `skills/blog/references/synthesis-contract.md`: 6 LAWs governing research-
  synthesis output. LAW 1: no trailing Sources block when inline-cited.
  LAW 2: no invented titles. LAW 3: no em-dashes or en-dashes. LAW 4: no
  raw cluster dumps with score tuples in body. LAW 5: every citation as
  inline `[name](url)`. LAW 6: discrete claims, not topic surveys.
- `tests/test_discourse_research.py`: 3 smoke tests (happy path multi-platform,
  empty input, LAW hygiene).

#### Changed

- `agents/blog-researcher.md`: gains Step 0.45 (keyword-trap pre-flight),
  Step 0.55 (named-entity decomposition), freshness floor (30-day / 90-day
  classification with explicit source-count gates), 5-dimension quality
  rubric scoring before handoff to `blog-writer`, and cross-source clustering
  to prevent echo. Each addition references `research-quality.md`.
- `skills/blog/SKILL.md`: orchestrator now auto-loads `DISCOURSE.md` (when
  present at project root) at the start of drafting / brief / strategy
  commands, alongside the existing BRAND.md / VOICE.md auto-load. Adds
  `blog-discourse` to routing table, sub-skills table, and quick reference.
  Adds `research-quality.md` and `synthesis-contract.md` to the reference
  files list. Sub-skill count 29 -> 30.
- `skills/blog-brief/SKILL.md`, `skills/blog-strategy/SKILL.md`,
  `skills/blog-write/SKILL.md`, `skills/blog-rewrite/SKILL.md`: each
  references `research-quality.md` and `synthesis-contract.md` for input
  research-quality scoring and synthesis-output LAW enforcement.

### Audit-driven hardening (cybersecurity 8-agent + github 6-agent + competitive analysis, 2026-05-17)

A comprehensive three-track audit ran against v1.8.0 before commit:
cybersecurity (8 parallel specialist agents, OWASP + MITRE ATT&CK +
threat-intel + AI-code review), github (6 scoring agents across README /
metadata / legal / community / release / SEO), and a shallow competitive-gap
analysis (rankenstein-blog, last30days, marketing-skills, Frase, SurferSEO).
Composite scores before fixes: cybersec ~75 (capped at C by auto-CRITICAL
gate), github ~85, competitive positioning strong. The following fixes
landed before this release.

#### Security (CRITICAL)
- **Indirect prompt-injection guard for project-root file auto-load
  (`skills/blog/SKILL.md`)**: the v1.8.0 BRAND.md / VOICE.md / DISCOURSE.md
  auto-load was flagged CRITICAL by 3 of 8 cybersecurity agents
  independently. A poisoned project-root file could instruct downstream
  agents (including blog-researcher with WebFetch authority) to exfiltrate
  data. Closed by an "Untrusted-Data Contract" section that mandates
  explicit fencing (`=== BEGIN UNTRUSTED PROJECT-ROOT CONTEXT ===`),
  pre-injection sanitization scan for instruction-shaped patterns
  ("ignore previous", "from now on", "exfiltrate", "system:",
  `<|im_start|>`, "act as", etc.), tool-boundary preservation (project-root
  files cannot unlock tools the agent does not already have), and
  provenance recording (file mtime in the injection).
- **`SECURITY.md` adds T12 trust boundary** documenting the project-root
  auto-load surface in line with T9 (WebFetch indirect injection).

#### Security (HIGH)
- **Path-traversal / symlink / DoS hardening for new v1.8.0 scripts**:
  `scripts/cognitive_load.py` and `scripts/discourse_research.py` previously
  accepted unrestricted Path() arguments. Now use `_validate_input_path` and
  `_validate_output_path` helpers that:
  - Refuse symlinks (CWE-59) so a hostile link to `/etc/passwd` or
    `~/.ssh/id_rsa` is rejected
  - Refuse non-regular files (no FIFOs, devices, sockets)
  - Enforce size caps (`MAX_INPUT_BYTES = 10 MB` for cognitive_load file,
    `1 MB` for jargon; `25 MB` for discourse results, `256 KB` for
    decomposition file; `25 MB` for stdin)
  - Refuse overwriting existing symlinks via `--output`
  - Refuse output paths whose parent directory does not exist
- **JSON schema validation in `scripts/discourse_research.py`**: input items
  must be objects with required fields (`platform`, `url`, `title`,
  `snippet`); arrays capped at `MAX_ITEMS = 10_000` to prevent
  clustering-complexity DoS.
- **`google-genai` upper-bound pinned** in
  `skills/blog-audio/scripts/requirements.txt` (`>=1.0.0,<2.0.0`) to
  prevent silent v2.x breaking-change adoption.

#### Legal compliance
- **`NOTICE` file added at repo root** to satisfy Apache 2.0 § 4(d)
  attribution for the impeccable methodology adaptations. Lists all four
  impeccable-sourced methodologies, all five last30days-sourced
  methodologies, and the FLOW CC BY 4.0 sync arrangement, with explicit
  source-to-target mapping.
- **`LICENSE` copyright year extended** from `2025` to `2025-2026` to
  reflect the substantial 2026 development arc (v1.6.5 through v1.8.0).
- **`CITATION.cff` updated**: version `1.5.0 -> 1.8.0`, date released
  `2026-03-18 -> 2026-05-16`, given-names / family-names added,
  keywords expanded (added geo, aeo, plugin, mdx, wordpress, multilingual,
  hreflang, flow-framework, discourse-research), homepage URL switched
  from `rankenstein.pro` to `claude-blog.md`.
- **`pyproject.toml` version bumped** from `1.7.1 -> 1.8.0`.

#### Community
- **`.github/ISSUE_TEMPLATE/config.yml`** added: disables blank issues and
  routes general questions to Discussions, security disclosures to the
  Security Advisories page, and documentation to docs/.
- **`.github/FUNDING.yml`** added with GitHub Sponsors link.
- **`.github/pull_request_template.md`** expanded from a 5-line stub to
  include Type of Change, Linked issue, comprehensive test plan (pytest +
  plugin validate + em-dash hygiene), documentation checklist, security
  checklist, and link to CONTRIBUTING.md.
- **`CONTRIBUTING.md`** expanded with explicit Code Style section
  (Python conventions, prose conventions, conventional commits) and
  Security expectations section.

#### Documentation
- **`README.md`** count and content fixes: added 9 missing user-facing
  commands to the Commands table (blog-cluster, blog-multilingual,
  blog-translate, blog-localize, blog-locale-audit, blog-flow, blog-brand,
  blog-discourse); Architecture section sub-skill count corrected
  (`21 user-facing + 1 internal` -> `28 user-facing + 2 internal-only`);
  agents list corrected (4 -> 5, added blog-translator); scripts list
  expanded to include cognitive_load.py, discourse_research.py, sync_flow.py.
- **`docs/COMMANDS.md`** routing table extended to include all 30
  sub-skills (previously listed only the v1.6.x set).
- **`PRIVACY.md`** date bumped to `2026-05-17`.

#### Tests
- **`tests/test_security_v1_8_0.py`** (12 tests, 11 pass + 1 graceful skip):
  symlink refusal on input and output paths for both new scripts; size-cap
  enforcement; JSON schema validation (non-array, missing fields,
  too-many-items); orchestrator Untrusted-Data Contract presence; T12
  documentation in SECURITY.md; NOTICE file existence and Apache 2.0
  attribution. Total test count: 60 -> 71.

## [1.7.1] - 2026-04-27

### Security audit + remediation arc (12 commits, all CRITICAL + HIGH closed)

The 2026-04-27 cybersecurity audit (via `/cybersecurity` skill) identified
1 CRITICAL + 5 HIGH + 14 MEDIUM + 11 LOW + 8 INFO findings (39 total).
This release closes all of them across 10 focused commits.

#### Security (Critical / High)
- **CRITICAL VULN-001**: `setup_image_mcp.py` defaulted to project-local
  `.mcp.json` (which was tracked) and wrote literal `GOOGLE_AI_API_KEY`.
  Default flipped to `--global` (writes user-private `~/.claude/settings.json`,
  mode 0600); `--project` opts in to env-expansion-only mode and refuses to
  write into a tracked file.
- **HIGH**: `.mcp.json` removed from git tracking, added to `.gitignore`;
  new tracked `.mcp.example.json` template with env-expansion + pinned
  `@ycse/nanobanana-mcp@1.1.1`.
- **HIGH**: `_save_oauth_token` and NotebookLM `_save_browser_state` now
  use atomic write + `chmod 0o600`. `_harden_perms` helper applied to
  every credential-write site.
- **HIGH**: OAuth flow gains CSRF state token via `secrets.token_urlsafe`,
  validated in handler with 403 on mismatch. Listener bound to 127.0.0.1.
- **HIGH**: 4 hash-pinned lock files (1915 LoC) for all pip manifests via
  `pip-compile --generate-hashes --strip-extras --allow-unsafe`.
- **HIGH**: README install ordering reframed (clone+checkout-tag now
  recommended; curl-pipe-bash documented as convenience with trust caveat).

#### Security (Medium)
- OAuth scopes downgraded to per-command least-privilege (`gsc_readonly +
  ga4` default; `--scopes` flag for explicit elevation).
- `--no-sandbox` removed from NotebookLM Chromium launch (env opt-in only).
- `sync_flow.py` lockfile drift now BLOCKS via `sys.exit(2)` unless
  `--allow-drift` explicitly passed; drift fires before filesystem mutation.
- `google_report.py` `--domain` whitelist regex + path containment check.
- CI workflow gains top-level `permissions: contents: read`, concurrency
  cancel-in-progress, and `pip install -e ".[dev]"` (was unpinned).
- Dependabot adds 3 nested-manifest entries (was missing 80% of dep surface).
- `pyproject.toml` advanced extras now bounded; new `[ads]` group declares
  previously-phantom `google-ads` dep.
- GitHub Actions SHA-pinned (`actions/checkout` + `actions/setup-python`).

#### Security (Low / INFO)
- `traceback.print_exc()` in NotebookLM error path replaced with clean
  error; verbose trace gated behind `BLOG_DEBUG` env.
- 6 bare `except:` blocks changed to `except Exception:` so signals
  propagate.
- `__init__.py` import-time side effects removed (no more silent
  venv.create + Chrome download on test discovery).
- API key masking changed from `key[:8]+...+key[-4:]` to length-only.
- Unexecutable Bash instruction removed from `blog-writer` agent prompt.
- `uninstall.sh` and `uninstall.ps1` now glob `blog-*` (was static list
  missing v1.7.0 sub-skills) and purge `~/.config/claude-seo/` credentials.
- CLI input length caps on `ask_question.py` and `notebook_manager.py`.

#### PowerShell 5.1 compatibility (post-audit pushback)
- `install.ps1` + `uninstall.ps1` 3-arg `Join-Path` calls (PS 6.0+ only)
  rewritten as nested 2-arg form. Default Windows 10/11 ships PS 5.1; the
  prior code would fail with "A positional parameter cannot be found"
  on every install attempt.
- The `??` null-coalescing operator (also PS 6.0+) was already removed
  in an earlier hotfix commit (96ef396).

#### Tests
- `test_google_auth_write_secret_atomic_sets_mode_0600`: behavioral test
  loading the helper via `importlib.spec_from_file_location` + `tmp_path`.
- `test_notebooklm_credential_files_contain_chmod_hardening`: static test
  requiring `_harden_perms(` count >= 2 (def + at least 1 call).
- `test_mcp_json_is_gitignored`: regression gate for `.gitignore` entry.
- `test_user_invokable_skills_have_complete_frontmatter` (NEW): asserts
  every user-invokable SKILL.md has `description`, `argument-hint`, and
  `license` fields. Closes the verifier blind spot that allowed
  blog-rewrite (and 14 other skills) to ship without these fields.

#### Docs
- New comprehensive `SECURITY.md`: vulnerability disclosure flow, in/out
  of scope, T1-T11 trust boundaries with STRIDE, dual-use technology notes
  (patchright stealth-fork rationale, WebFetch indirect prompt injection
  risk model, sync_flow defenses), audit history, hardening checklist.
- `docs/MCP-INTEGRATION.md` updated with new `--global` default flow.
- `skills/blog-image/SKILL.md` setup section reflects new defaults +
  pinning convention.
- `docs/COMMANDS.md` updated to cover all 27 user commands (was 17).
- `agents/blog-researcher.md` adds explicit prompt-injection framing for
  WebFetch / WebSearch content (T9 boundary defense).
- `agents/blog-writer.md` clarifies dual install path for analyze script.

#### Dependencies
- Generated 4 hash-pinned lock files (`requirements.lock` at root +
  3 nested `skills/*/scripts/requirements.lock`). All install paths
  via `setup_environment.py` now prefer `--require-hashes -r .lock`
  when present.
- pyproject.toml: bound previously-unbounded `advanced` extras (`lxml`,
  `jsonschema`, `spacy`, `sentence-transformers`, `scikit-learn`,
  `language-tool-python`); synced `core` upper bounds with
  `requirements.txt`; added `[ads]` optional group with `google-ads`.

#### Skills (frontmatter completeness)
- All 27 user-invokable SKILL.md files now declare `argument-hint` and
  `license: MIT` consistently. Caught by full-skill test pass + 9-agent
  meta-audit; previously 15 skills were missing one or both fields.

### Audit + meta-audit dispatch summary
- 7-agent cybersecurity audit dispatch (parallel, single message)
- 28-agent full-skill test dispatch (one per sub-skill, parallel)
- 9-agent meta-audit (re-audit the audit + fix arc)
- Independent code-reviewer agent caught 5 issues post-commit (build-system
  missing, bare-filename crash, PS 5.1 incompatibility, weak test, missing
  ValueError handler) -> hotfix commit applied.
- Codex GPT-5.5 high-reasoning council used 4 times for plan validation;
  each returned APPROVE-WITH-CHANGES with substantive corrections that
  materially improved the plan.

### Open follow-ups (not release-blocking)
- `blog-write/SKILL.md` Phase 5 extraction: currently 535 lines, ideal
  is < 500. Extract Phase 5 to a reference file in next iteration.
- `sentence-transformers` upper bound `<5.0.0` is one major behind current
  5.4.1; re-evaluate when next minor lands.
- E-E-A-T overlap consolidation across `eeat-signals.md`, `geo-optimization.md`,
  `quality-scoring.md` (architectural).

## [1.7.0] - 2026-04-27

### Pro Hub Challenge community release + FLOW framework integration

#### Added
- **`blog-cluster`** sub-skill (winner of the AI Marketing Hub Pro Hub Challenge, March 2026, by Lutfiya Miller). Semantic topic-cluster planning + execution engine. SERP-based keyword grouping, hub-and-spoke architecture, sequential `blog-write` orchestration with shared cluster context and automatic internal-link injection. XSS-hardened cluster-map.html (no inline JavaScript). Adapted from [semantic-cluster-engine](https://github.com/Drfiya/semantic-cluster-engine).
- **`blog-multilingual`** sub-skill (by Chris Mueller, AI Marketing Hub Pro). One-command international publishing. Orchestrates `blog-write`, `blog-translate`, `blog-localize`, plus optional `seo-hreflang` integration. Adapted from [claude-blog-multilingual](https://github.com/Chriss54/multilingual-int).
- **`blog-translate`** sub-skill (by Chris Mueller). SEO-optimized translation with format preservation, machine-translation artifact detection, and locale-correct number/date/currency formatting.
- **`blog-localize`** sub-skill (by Chris Mueller). Cultural deep-adaptation with built-in profiles for DACH, Francophone, Hispanic, and Japanese markets, plus a custom-locale template.
- **`blog-locale-audit`** sub-skill (by Chris Mueller). Multilingual quality control: completeness matrix, hreflang correctness, meta-tag parity, freshness checks.
- **`blog-translator`** specialized agent (no `Bash` tool, per the v1.9.6 lesson from claude-seo).
- **`blog-flow`** sub-skill. FLOW framework integration ([github.com/AgriciDaniel/flow](https://github.com/AgriciDaniel/flow), CC BY 4.0 prompt content + MIT code). Commands: `/blog flow [find|optimize|win|prompts|sync]`. Surfaces 30 blog-applicable evidence-led prompts; the local-SEO stage is intentionally excluded (use claude-seo for those).
- **`scripts/sync_flow.py`**. Pulls FLOW references from GitHub. Stdlib only. HTTPS-only host allowlist (`api.github.com`). 5 MB cap. Atomic writes. Path-traversal guard. Anonymous-first GitHub API. Supports `--dry-run` and `--ref <sha>` pinning. SHA-256 lockfile drift detection. Injects CC BY 4.0 license header on every synced markdown file plus the auto-generated index README.
- **`tests/test_security_guardrails.py`**. Four mechanical pytest gates that fail CI if (1) any agent grants `Bash`, (2) any SKILL.md uses the invalid `allowed-tools` field, (3) skill names collide, or (4) the FLOW sync script loses a security invariant.
- **`CONTRIBUTORS.md`** crediting Pro Hub Challenge contributors and recording the integration decisions.

#### Changed
- Plugin description bumped to mention 27 commands, 5 agents, FLOW + cluster + multilingual capabilities.
- Marketplace description updated to "28 skills, 5 agents, FLOW framework integration, semantic topic-cluster execution, multilingual publishing".
- `skills/blog/SKILL.md` orchestrator: routing entries added for `cluster`, `multilingual`, `translate`, `localize`, `locale-audit`, and `flow`. Quick Reference table updated. Version bumped to 1.7.0.
- `CLAUDE.md` file counts updated (28 sub-skills, 5 agents).
- Plugin keywords expanded to include `flow-framework`, `topic-clusters`, `hub-and-spoke`, `multilingual`, `translation`, `localization`, `hreflang`, `i18n`.

#### Fixed
- **Pre-existing security debt**: removed `Bash` from `agents/blog-reviewer.md` tools list. The agent scores text and only needs `Read`, `Grep`, `Glob`. Aligns with the v1.9.6 lesson from claude-seo (prompt-injection blast radius on agents with shell access). Now enforced mechanically by `test_no_bash_tool_in_any_agent_frontmatter`.

## [1.6.8] - 2026-04-08

### Fixed
- install.ps1: Fixed Windows PowerShell 5.1 ParameterBindingException (`irm|iex` to `iex (irm)`)
- install.ps1: Corrected Python version warning from 3.12+ to 3.11+
- ci.yml: Bumped actions/checkout and actions/setup-python from v4/v5 to v6
- docs/INSTALLATION.md: Updated Windows one-liner to match install.ps1 fix

## [1.6.7] - 2026-04-08

### Fixed
- 29 corrections across API endpoints, crawler specs, schema markup, and distribution playbook
- GA4 quota corrected from 25K to 200K Core Tokens/day
- Removed misquoted "46% reading mode" stat; replaced with actual Kevin Indig finding
- Added 8 new AI crawlers to ai-crawler-guide.md
- BlogPosting schema properties corrected from "Required" to "Recommended" per Google docs
- Sweep-up: 5 residual attribution fixes from Areas 3-7 audit

## [1.6.6] - 2026-04-08

### Fixed
- Corrected 20 misattributed or unverifiable statistics in google-landscape-2026.md and geo-optimization.md
- Removed fabricated Mueller quote; replaced with paraphrase of documented position
- Removed unverifiable +340% Seenos citation claim from SKILL.md, content-rules.md, schema-stack.md, distribution-playbook.md
- Added caveats to FAQPage (+28%, sponsored SEL article), G2 stats (self-reported), B2B SaaS decline (single case study)
- Updated ChatGPT users 800M to 900M, AI Mode countries 120 to 200+, Hidden Gems 77% to 70.85%

## [1.6.5] - 2026-03-28

### Added
- **blog-google sub-skill**: Google API integration with 13 commands across 4 credential tiers. Includes PageSpeed Insights, CrUX Core Web Vitals (25-week history), Search Console performance, URL Inspection, Indexing API, GA4 organic traffic, NLP entity analysis, YouTube video search, Google Ads Keyword Planner, and PDF/HTML report generation. Contains 11 Python scripts in isolated venv. Shares config with claude-seo at `~/.config/claude-seo/google-api.json`.
- **YouTube video embedding**: Blog posts now discover and embed 2-3 relevant YouTube videos using srcdoc lazy-loading pattern (~5KB vs ~500KB per embed). Integrated into blog-write (Phase 2 research + Phase 5 embedding), blog-rewrite (audit + inject), and blog-schema (VideoObject generation). Supports MDX, HTML, Markdown, and Hugo embed formats with noscript fallback for AI crawlers.
- **VideoObject JSON-LD schema**: blog-schema now generates VideoObject for embedded videos (up to 7 schema types per page, from 6). Added to schema-stack.md reference with @id pattern `#video-{N}`.
- **video-embeds.md reference**: New reference file with quality criteria (0-100 scoring), embed placement strategy, platform-specific code patterns, and graceful degradation.
- **Google API integrations in existing workflows**: blog-seo-check (optional PSI/CrUX), blog-rewrite (NLP entity analysis), blog-geo (GSC performance), blog-researcher (YouTube video discovery).

### Fixed
- **Plugin compliance**: Removed non-standard `allowed-tools` frontmatter field from all 22 SKILL.md files per Claude Code plugin specification. Only valid fields remain: name, description, user-invokable, argument-hint, compatibility, license, metadata.
- **CLAUDE.md development rules**: Clarified SKILL.md frontmatter field requirements and reference file size guidelines.

## [1.6.2] - 2026-03-27

### Fixed
- **plugin.json**: Removed invalid `skills` array of objects that failed `claude plugin validate` (skills auto-discovered from `skills/` directory)
- **Agent frontmatter**: Removed unsupported `context: fork` field from all 4 agents (blog-researcher, blog-writer, blog-seo, blog-reviewer) per plugin agent spec
- **Version alignment**: Synced pyproject.toml version with plugin.json (was 1.5.0, now 1.6.2)

### Added
- **Marketplace support**: Created `.claude-plugin/marketplace.json` for self-hosted marketplace distribution (`/plugin marketplace add AgriciDaniel/claude-blog`)
- **plugin.json `repository` field**: Source code URL for marketplace discoverability
- **plugin.json `keywords` field**: 14 tags for marketplace search (blog, seo, content, writing, ai-citations, geo, aeo, eeat, etc.)

## [1.6.0] - 2026-03-25

### Added
- **blog-notebooklm sub-skill**: Query NotebookLM for source-grounded research with 10 Python scripts and 2 reference docs
- **blog-audio sub-skill**: Generate audio narration via Gemini TTS with 30 voice options, summary/full/dialogue modes, and 5 Python scripts

### Fixed
- Dynamic skill discovery in installers (fixes #8, fixes missing blog-notebooklm/blog-audio)
- Replaced remaining em dashes in .gitattributes and requirements.txt
- Updated "Claude Banana" reference to "Banana Claude" after upstream repo rename

## [1.5.0] - 2026-03-18

### Added
- **blog-persona sub-skill**: Writing persona management with NNGroup 4-dimension tone framework, configurable readability bands (Consumer/Professional/Technical), and style enforcement
- **blog-cannibalization sub-skill**: Keyword overlap detection across blog posts with local-only (grep) and DataForSEO API modes, severity scoring, and merge/differentiate recommendations
- **blog-factcheck sub-skill**: Statistics verification pipeline that fetches cited source URLs and scores claim confidence (exact match, paraphrase, not found)
- **blog-taxonomy sub-skill**: CMS taxonomy management supporting WordPress REST, Shopify GraphQL, Ghost, Strapi, and Sanity. Tag suggestion, sync, and audit workflows
- **CTA placement reference**: Content-type-specific CTA positioning rules with HubSpot statistics (202% better contextual CTAs, 266% more conversions with single CTA)
- **Visual rhythm enforcement**: Mandatory visual element (image/chart/callout) every 300-500 words in blog-write and blog-writer agent
- **Link deduplication check**: Step 5.5 in blog-seo-check flags duplicate URLs in body content
- **Creative Director prompting**: 4-dimension professional image prompting (Lighting, Camera, Film Stock, Material) in blog-image prompt engineering reference

### Changed
- **TL;DR replaced with Key Takeaways**: Default summary box label changed to "Key Takeaways" with 3-5 bullet format. Configurable per persona. Backward compatible (accepts TL;DR, Key Takeaways, The Bottom Line, What You'll Learn, At a Glance, In Brief)
- **Readability bands by audience**: Consumer (Grade 6-8), Professional (Grade 8-10), Technical (Grade 10-12) with default at Grade 7-8
- **analyze_blog.py**: Updated summary box detection to recognize all 6 label variants
- **blog-image models**: Added Imagen 4 pricing, legacy model deprecation note (June 1, 2026), blog image post-processing pipeline spec
- Updated install scripts to handle 4 new sub-skills and personas directory
- Updated orchestrator routing table, Quick Reference, and Sub-Skills table (19 sub-skills, 17 commands)

## [1.4.0] - 2026-03-14

### Added
- **blog-image sub-skill**: AI image generation and editing for blog content via Gemini MCP (`@ycse/nanobanana-mcp`)
  - 6-component Reasoning Brief system (Subject, Action, Context, Composition, Lighting, Style)
  - 6 blog-optimized domain modes (Editorial, Product, Landscape, UI/Web, Infographic, Abstract)
  - Commands: `/blog image generate`, `/blog image edit`, `/blog image setup`
  - 3 reference files: gemini-models.md, mcp-tools.md, prompt-engineering-blog.md
  - 2 setup scripts: setup_image_mcp.py, validate_image_setup.py
- **MCP integration**: nanobanana-mcp server config in `.mcp.json` for Gemini image generation
- **blog-write**: AI image generation as alternative/supplement to stock photos in Phase 2 Research
- **blog-rewrite**: AI image generation for missing/insufficient images in Phase 2 and Phase 4g
- **blog-researcher**: AI image recommendation output when stock photos are insufficient
- **visual-media.md**: Option 3 - AI-Generated Cover documentation with domain mode guidance

### Changed
- Updated install scripts (install.sh, install.ps1) to handle blog-image references and scripts
- Updated orchestrator routing table, Quick Reference, and Sub-Skills table for blog-image
- Updated docs: COMMANDS.md, MCP-INTEGRATION.md, INSTALLATION.md with image generation docs
- Updated README.md: commands table, architecture diagram, feature descriptions, badge count (13→15)
- Sub-skill count: 14 → 15 (13 user-facing + 1 internal chart + 1 image generation)

---

## [1.3.1] - 2026-03-06

### Added
- **SKILL.md**: `license`, `compatibility`, and `metadata` fields per Agent Skills spec (agentskills.io)
- **plugin.json**: `version`, `homepage`, `license` fields; `skills` array declaring all 14 skills (marketplace readiness); `blog-chart` marked `user-invocable: false`
- GitHub issue template and PR template (community health files)

### Changed
- **README.md**: Removed broken `/plugin install claude-blog@AgriciDaniel` (not yet registered in marketplace); corrected Python badge `3.12+` → `3.11+`; added inline note clarifying `blog-chart` is internal
- **docs/INSTALLATION.md**: Removed "Plugin Install (Recommended)" section with broken command; corrected Python `3.12+` → `3.11+` (aligns with `pyproject.toml >=3.11` and CI matrix)
- **docs/INSTALLATION.md**: Added `blog-chart` to manual `mkdir` brace expansion (was missing from 13-skill list)
- **CLAUDE.md**: Corrected Python version reference `3.12+` → `3.11+`

### Fixed
- **install.ps1**: Removed dead `$dirs` variable block (declared but never used); updated paths for `skills/blog/` restructure; added `blog` skip in sub-skill loop to prevent double-copy
- **skills/blog/SKILL.md**: Corrected `compatibility` field Python version `3.12+` → `3.11+`; corrected `user-invocable` → `user-invokable` (correct Agent Skills spec spelling)
- **skills/blog-chart/SKILL.md**: Added `user-invokable: false` to match plugin.json declaration; corrected attribute spelling

### Security
- Deleted `firebase-debug.log` (gitignored debug artifact); deleted stale remote branch `claude/review-plugin-testing-practices-eVVOU`

---

## [1.3.0] - 2026-03-06

### Added
- **Plugin ecosystem support**: `.claude-plugin/plugin.json` for `/plugin install` compatibility
- **44 pytest unit tests** for `analyze_blog.py`, covers frontmatter, headings, paragraphs, images, AI detection, citations, FAQ, freshness, readability, links, schema, and integration tests
- **GitHub Actions CI**: 3 jobs - Python tests (3.11 + 3.12), SKILL.md frontmatter validation, plugin.json validation
- **DataForSEO MCP integration** documentation, recommended primary MCP server for live SEO data (SERP, keywords, backlinks, on-page, domain analytics, content analysis, AI optimization)
- `pyproject.toml` with dependency groups (core, advanced, dev)
- `CONTRIBUTING.md` with development guidelines
- `.mcp.json` for optional MCP server configuration
- Skill evaluation scenarios (7 trigger test cases)

### Changed
- **Directory restructure**: `blog/` → `skills/blog/` (official Anthropic plugin layout)
- Updated all internal path references across skills, docs, and install scripts
- README updated with plugin install as primary method
- MCP-INTEGRATION.md updated with DataForSEO as recommended integration

### Fixed
- **install.sh**: Restored `TEMP_DIR` global scope fix (lost during restructure)
- **install.sh**: Removed `--break-system-packages` pip flag (security concern)
- **install.sh**: Removed redundant `mkdir` and double-copy of `skills/blog/`
- **CI**: Fixed lint-markdown grep matching legitimate `skills/blog/references/` paths
- **Docs**: Fixed 11 instances of double `skills/skills/` paths in INSTALLATION.md and TROUBLESHOOTING.md

### Removed
- `--break-system-packages` pip install flag

## [1.2.1] - 2026-03-06

### Fixed
- **install.sh**: Move `TEMP_DIR` declaration to global scope so the `EXIT` trap can access it after `main()` returns (fixes "unbound variable" error with `set -u` when installing via `curl | bash`)

## [1.2.0] - 2026-02-18

### Changed
- **Readability layer upgrade** with research-backed thresholds (120+ sources):
  - Flesch target: 45-60 → 60-70 (aligns with Yoast, GEO, WCAG, Raptive data)
  - Paragraph hard limit: 100 → 150 words (200 = Yoast red)
  - Ideal paragraph range: 40-55 → 40-80 words
  - H2 heading frequency: 150-200 → 200-300 words
  - Content Quality redistribution: Depth 8→7, Readability 6→7
- New automated checks in `analyze_blog.py`: passive voice estimation, transition word percentage, AI trigger word detection (26 words), sentence length distribution
- New reference sections in `google-landscape-2026.md` and `geo-optimization.md` for readability signals
- 16 files updated across references, script, skills, agents, and docs

### Added
- YouTube demo video link in README
- Header image and demo GIFs (`assets/`)

### Removed
- Placeholder `screenshots/` directory

## [1.1.0] - 2026-02-18

### Added
- **Built-in SVG chart generation** (`blog-chart` sub-skill), eliminates external `/svg` dependency
  - Supports 7 chart types: horizontal bar, grouped bar, donut, line, lollipop, area, radar
  - Dark-mode compatible, accessible (WCAG), platform-aware (HTML/JSX auto-detection)
- **Image URL verification** in researcher agent, validates HTTP 200 before embedding
- **Mid-writing readability check** in writer agent, self-checks Flesch targets before returning
- **Image density guidelines** by content type in visual-media.md

### Changed
- claude-blog is now fully self-contained, no external skill dependencies required
- Integration section updated to list companion skills as optional
- Installer scripts updated for 13 sub-skills

### Removed
- External `/svg` / `/svg-chart` skill dependency

## [1.0.0] - 2026-02-18

### Added
- **12 slash commands**: write, rewrite, analyze, brief, calendar, strategy, outline, seo-check, schema, repurpose, geo, audit
- **12 reference documents** loaded on-demand (RAG pattern):
  - google-landscape-2026, geo-optimization, content-rules, visual-media, quality-scoring
  - eeat-signals, content-templates, ai-crawler-guide, schema-stack, platform-guides, distribution-playbook, internal-linking
- **12 content type templates**: how-to, listicle, case study, comparison, pillar page, product review, thought leadership, roundup, tutorial, news analysis, data research, FAQ/knowledge base
- **4 specialized subagents**: blog-researcher, blog-writer, blog-seo, blog-reviewer
- **Python quality analysis script** (`analyze_blog.py`):
  - 5-category, 100-point scoring system (Content 30, SEO 25, E-E-A-T 15, Technical 15, AI Citation 15)
  - Readability analysis via textstat (Flesch, Gunning Fog, SMOG, Coleman-Liau)
  - AI content detection signals (burstiness, known AI phrases, vocabulary diversity)
  - Schema detection via BeautifulSoup
  - Batch mode with directory scanning
  - Multiple output formats (JSON, markdown, table)
  - Graceful degradation without optional dependencies
- **Unix + Windows installers** (install.sh, install.ps1) with one-command curl install
- **Uninstaller** (uninstall.sh) for clean removal
- **Full documentation suite** (docs/): Installation, Commands, Architecture, Templates, Troubleshooting, MCP Integration

### Architecture
- Main orchestrator: `skills/blog/SKILL.md` (routes all 12 commands)
- 12 sub-skills in `skills/blog-*/SKILL.md`
- 4 subagents in `agents/blog-*.md`
- 12 reference docs in `skills/blog/references/` (loaded on-demand)
- 12 content templates in `skills/blog/templates/`

### Fixed
- Corrected phantom "January 2026 Authenticity Update" references to verified **December 2025 Core Update** (Dec 11-29, 2025)
