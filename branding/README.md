# claude-blog branding system

Source-of-truth visual assets for the `claude-blog` skill suite. Mirrors the
cross-product brand system established in `claude-ads/branding/`: same chrome
(typography, HUD bars, dotted separators, accent-driven divider), product
specific accent palette (purple `#7B5EA7` family, the "publishing terminal"
preset from the system).

## What ships here

| File | Purpose | Format |
|---|---|---|
| `banner.svg` | Hero banner for README, social cards, talks | Native SVG, ~7KB, 3 SMIL animations |
| `AGENT-PROMPT.md` | Reusable prompt for generating matching banners in sibling repos | Markdown |
| `diagrams/*.md` | Mermaid source for architecture diagrams | Markdown with mermaid blocks |
| `diagrams/*.svg` | Pre-rendered SVG of each diagram | Native SVG via `mmdc` |

## How to use `banner.svg`

Embed in any markdown surface:

```html
<img src="branding/banner.svg"
     alt="claude-blog: AI-Powered Blog Authority"
     width="100%">
```

The SVG is self contained. No external font fetches. Uses the system font
stack with Inter fallback for the wordmark and `ui-monospace` for HUD text.
Renders identically on GitHub, RSS readers, AI crawlers, and any docs site
that supports inline SVG.

## How to edit `banner.svg`

The SVG is plain text. Open in any editor. The key sections:

| Section (approx lines) | What lives there |
|---|---|
| `<defs>` (12 to 60) | Gradients (`bgGrad`, `wordGrad`, `dividerGrad`), `scanlines` pattern, glow filters |
| Top HUD (62 to 78) | Top status bar: SYS slug, node, uptime, breathing dot |
| Wordmark (80 to 95) | "CLAUDE BLOG" two-line wordmark + scanline overlay |
| Divider + tagline (97 to 111) | Horizontal accent bar + tagline + system-line |
| Command palette (113 to 132) | The 7 right-aligned commands |
| Bottom status bar (134 to 152) | Live dot, 3 status tokens, identifier, UTC clock |

To swap the accent color: edit the stop colors in `wordGrad` and `dividerGrad`,
plus the five `#7B5EA7` references in HUD chrome, divider, dots, and the
highlighted command. Replace all six spots and the banner re-skins.

## How to render the Mermaid diagrams

```bash
# One time
npm install --no-save @mermaid-js/mermaid-cli

# Per diagram (already committed; re-run only after editing the .md source)
npx mmdc \
  -i branding/diagrams/orchestrator-routing.md \
  -o branding/diagrams/orchestrator-routing.svg \
  -t dark \
  -b transparent
```

The repo commits both the source `.md` and the rendered `.svg`. Embedding the
`.svg` in READMEs makes the diagrams render in environments that do not
support mermaid (RSS, AI crawlers, email previews) while keeping the source
editable.

## Cross-product brand consistency

`claude-blog`, `claude-ads`, and any sibling repos share these constants:

- Background: deep espresso radial gradient `#1A1612 -> #110E0B -> #060504`
- Typography: Inter for tagline, `ui-monospace` for HUD and commands
- HUD layout: top-left SYS slug + node, top-right uptime. Bottom-left live
  dot + 3 status tokens, bottom-right identifier + UTC clock
- Aspect ratio: 21:9 (1680x720 viewBox)
- Animation budget: 3 elements per banner, banner-only motion across the system

What varies per product:

- The 5-step accent palette (orange = ads, purple = blog, teal = seo)
- The wordmark text and tagline
- The 7-command palette
- The system-line stats (sub-skill count, contract version)

See `AGENT-PROMPT.md` for the full reusable prompt.

## Animation budget

Three SMIL animations, all subtle, all loop forever:

| Element | Animation | Loop | Purpose |
|---|---|---|---|
| Top HUD dot | Opacity 0.45 -> 1.0 -> 0.45 | 1.6s | "Live system" signal |
| Bottom HUD dot | Opacity 0.45 -> 1.0 -> 0.45 | 1.6s | Mirrors top dot |
| Divider bar | Opacity 0.72 -> 1.0 -> 0.72 | 6s | Slow breath beneath wordmark |

Everything else on the banner is static. Everything else in the branding
system (diagrams, charts, future visuals) is static. Total moving things on
any rendered page: 3.

## Accessibility notes

- The SVG includes `<title>` and `<desc>` for screen readers
- `role="img"` and `aria-labelledby` are set
- Vignette is decorative only; `pointer-events="none"` prevents interaction interference
- GitHub strips inline `<style>` blocks from SVG, so `prefers-reduced-motion`
  CSS media queries inside the SVG do not take effect on GitHub's rendered
  view. For accessibility-critical contexts, render `banner.svg` to a static
  PNG once and embed the PNG instead

## Provenance

This system was first established in [AgriciDaniel/claude-ads](https://github.com/AgriciDaniel/claude-ads)
`branding/`. The `claude-blog` adaptation uses the purple "publishing
terminal" palette preset documented in claude-ads `AGENT-PROMPT.md` and the
native-SVG wordmark approach (cleaner alternative to the original
`figlet` ANSI Shadow rendering that depended on font-specific monospace
width).
