# Blog Delivery Contract: 5 gates

The v1.9.0 quality contract that every draft passes through before reaching
the user. Gate 4 (Content Review) is BLOCKING: the `blog-reviewer` agent must
return `BLOCKING: false` with score >= 90 and zero P0 issues, or the draft
returns to the writer.

```mermaid
flowchart LR
    classDef terminal fill:#1A1612,stroke:#5A5750,stroke-width:1px,color:#9075BD
    classDef gate fill:#3F2C5C,stroke:#7B5EA7,stroke-width:2px,color:#F5F4ED
    classDef blocking fill:#7B5EA7,stroke:#C9B3E6,stroke-width:4px,color:#FFFFFF,font-weight:bold
    classDef deliver fill:#7B5EA7,stroke:#3F2C5C,stroke-width:3px,color:#F5F4ED,font-weight:bold

    DRAFT["Draft<br/>ready"]:::terminal --> G1
    G1["Gate 1<br/>Capability<br/>Discovery"]:::gate --> G2
    G2["Gate 2<br/>Format<br/>Completeness"]:::gate --> G3
    G3["Gate 3<br/>Visual<br/>Verification"]:::gate --> G4
    G4["Gate 4<br/>Content Review<br/>BLOCKING"]:::blocking --> G5
    G5["Gate 5<br/>Asset + Link<br/>Integrity"]:::gate --> DELIVER["Deliver<br/>to user"]:::deliver

    G4 -.->|score below 90<br/>or P0 issues| RETURN["Return to<br/>writer with<br/>fix list"]:::terminal
```

## Gate-by-gate

| Gate | What it checks | Runner |
|---|---|---|
| 1. Capability Discovery | All sub-skills referenced in the draft are installed and callable | `scripts/blog_preflight.py --gate 1` |
| 2. Format Completeness | Markdown structure, frontmatter, required sections, word count | `scripts/blog_preflight.py --gate 2` |
| 3. Visual Verification | Hero image present, dimensions valid, alt text non-empty | `scripts/blog_preflight.py --gate 3` |
| 4. Content Review (BLOCKING) | E-E-A-T, AI-detection signals, citation depth, score >= 90 | `agents/blog-reviewer.md` (Task tool) |
| 5. Asset + Link Integrity | All internal links resolve, no broken images, JSON-LD valid | `scripts/blog_preflight.py --gate 5` |

A draft passing all 5 gates is delivered. A draft failing Gate 4 returns to
the writer with an explicit fix list (no auto-publish through that gate).
Gates 1, 2, 3, 5 run via `blog_preflight.py --strict`. Gate 4 is a separate
agent invocation, run BEFORE delivery, BLOCKING by design.

Full contract spec: `skills/blog/references/blog-delivery-contract.md`.
