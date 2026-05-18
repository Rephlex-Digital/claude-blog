# Multilingual Pipeline

What `/blog multilingual` does: take one English source, produce N locale
specific published versions with proper hreflang cross-linking. Each step is
an independent sub-skill that can be invoked directly.

```mermaid
flowchart LR
    classDef source fill:#1A1612,stroke:#5A5750,stroke-width:1px,color:#9075BD
    classDef step fill:#3F2C5C,stroke:#7B5EA7,stroke-width:2px,color:#F5F4ED
    classDef parallel fill:#2A1C3F,stroke:#9075BD,stroke-width:2px,color:#B49DD6
    classDef out fill:#7B5EA7,stroke:#C9B3E6,stroke-width:3px,color:#FFFFFF,font-weight:bold

    SRC["source.md<br/>en-US"]:::source --> T

    T["/blog translate<br/>per locale<br/>(parallel)"]:::parallel --> L
    L["/blog localize<br/>cultural<br/>adaptation"]:::step --> A
    A["/blog locale-audit<br/>QA gate"]:::step --> H
    H["hreflang emit<br/>cross-link<br/>locales"]:::step --> OUT

    OUT["published/<locale>/<br/>N versions<br/>shipped"]:::out
```

## Step intent

| Step | Sub-skill | Output |
|---|---|---|
| Translate | `/blog translate` | Raw translation per target locale, preserving markdown structure, code blocks, frontmatter, schema JSON-LD, and SVG charts |
| Localize | `/blog localize` | Cultural adaptation: currency, date format, idioms, examples, regional references swapped for locale-native equivalents |
| Audit | `/blog locale-audit` | QA pass: catches mis-localizations, broken markdown, frontmatter drift, stat-citation breakage |
| Hreflang | (orchestrator) | Emits `<link rel="alternate" hreflang="..." href="...">` tags across all locale versions so Google understands the cross-locale relationship |

## Why this pipeline shape

Pure machine translation lacks cultural depth (a US blog quoting "$10K MRR"
needs different framing for a JP audience that thinks in monthly revenue
differently). Pure cultural adaptation skips the translation work. Splitting
them into two steps with an audit gate between catches the failure modes of
each. Hreflang at the end ensures the published versions are properly indexed
as alternates, not duplicates, by search engines.

Full spec: `skills/blog-multilingual/SKILL.md`,
`skills/blog-translate/references/translation-rules.md`,
`skills/blog-localize/references/cultural-adaptation.md`.
