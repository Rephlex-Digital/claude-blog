# Agent Prompt: reusable native-SVG terminal banner

Use this prompt to give another AI agent everything it needs to produce a
matching banner for a sibling repo (claude-seo, claude-blog, claude-ads, or
a new one).

The deliverable is a single `branding/banner.svg` file (around 7KB,
1680x720 viewBox, 3 SMIL animations) that can be embedded directly in any
README.

This is the SVG variant of the brand system. For the PNG-from-HTML variant
(full CRT phosphor look with noise grain and drifting scanline), see
`claude-ads/branding/banner-template.html` and the PNG-render path in
`claude-ads/branding/AGENT-PROMPT.md`.

---

## Copy-paste prompt

````
You are creating a terminal-style banner SVG for a GitHub repo. The
banner must visually match the established cross-product brand
(retro CRT terminal, bold wordmark, HUD bars top + bottom, accent
divider, 7-command palette right-aligned, deep espresso background).

Template to copy: `branding/banner.svg` from claude-blog (purple palette)
or claude-ads (orange palette). Either is a valid starting point.
Pick the one whose layout already matches your target.

INPUTS to provide for the target repo:

  PRODUCT_NAME_LINE_1:   e.g. "CLAUDE"             (4 to 7 chars)
  PRODUCT_NAME_LINE_2:   e.g. "SEO"                (3 to 5 chars)
  PRODUCT_SLUG:          e.g. "CLAUDE-SEO"         (used in top HUD)
  TAGLINE:               e.g. "AI-Powered SEO Analysis"
  SYSTEM_LINE:           e.g. "RUNTIME READY . 18 SUB-SKILLS . 4 AGENTS . 312 CHECKS"
  COMMANDS (exactly 7):  e.g.
    /seo audit
    /seo schema
    /seo geo                  (this one will be highlighted in white)
    /seo sitemap
    /seo plan <type>
    /seo hreflang
    /seo competitor-pages
  STATUS_TOKENS (3):     e.g. "LINK . STABLE", "BUF 1024K", "V1.4.2"
  IDENTIFIER:            e.g. "208.140.MAINFRAME.AGRICIDANIEL"
  ACCENT_PALETTE:        one of:
                           orange      (Claude Ads, default)
                           teal-green  (Claude SEO)
                           purple      (Claude Blog)
                           cobalt-blue (Claude API)
                           crimson     (high-attention launches)

PROCESS (exactly 5 steps):

STEP 1: Pick the source banner.svg

  cp claude-blog/branding/banner.svg target-repo/branding/banner.svg

  (Or claude-ads/branding/banner.svg if you want orange default.)

STEP 2: Swap the accent palette

  In the <defs> block, edit `wordGrad` and `dividerGrad` stop colors to
  match the 5-step accent ramp for your product. Use the presets below
  ("Pre-built palette presets" section) and copy the colors verbatim.

  Then find/replace the bare `#7B5EA7` (purple) or `#D97757` (orange)
  references throughout the rest of the SVG: top HUD dot, bottom HUD
  dot, divider fill, the "/" prefix of the highlighted command, and the
  ">" prefix of the system-line. There are 5 to 6 spots total.

STEP 3: Edit the wordmark

  Find the two <text> elements with content "CLAUDE" and "BLOG"
  (or whatever the source used). Replace with PRODUCT_NAME_LINE_1 and
  PRODUCT_NAME_LINE_2.

  The wordmark uses Inter at font-size 148, weight 900, letter-spacing -4.
  If your product name is longer than 6 chars, you may need to reduce
  font-size to 132 or 120 and adjust the `<rect>` scanline overlay
  widths to match.

STEP 4: Fill the six EDIT THIS slots

  - Top HUD: replace "SYS . CLAUDE-BLOG" with "SYS . <PRODUCT_SLUG>"
  - Tagline: replace text content of the tagline <text> element
  - System line: replace the dotted-token list after the "> " prefix
  - Command palette: 7 <text> elements; replace each. Keep the
    highlighted-white command at position 4 (the middle one). That is
    the one with fill="#F5F4ED" and the accent-color "/" prefix.
  - Bottom HUD: replace the 3 status tokens and the identifier text

STEP 5: Validate and commit

  - Verify XML well-formedness:
      python3 -c "import xml.etree.ElementTree as ET; ET.parse('branding/banner.svg'); print('OK')"
  - Render to PNG for visual eyeball:
      python3 -c "from playwright.sync_api import sync_playwright; ..."
      (see render_banner.py in claude-blog/branding/)
  - File size should be under 10KB. If much larger, something went wrong
    (likely a stray embedded image).
  - Commit and push.

QA CHECKLIST before committing:

  [ ] File is branding/banner.svg, single self-contained file
  [ ] XML well-formed (parses without error)
  [ ] File size 5KB to 15KB
  [ ] viewBox is "0 0 1680 720" (21:9)
  [ ] Wordmark renders the right product name
  [ ] Top HUD shows "SYS . <YOUR_PRODUCT_SLUG>"
  [ ] All 7 commands appear; the 4th is highlighted in white
  [ ] Accent color appears in: dots, divider, "/" of highlighted command,
      "> " of system line. All 5+ references use the same hex value
  [ ] Tagline and system-line are visible below the divider
  [ ] No console errors when opening the SVG in a browser
  [ ] No external font fetches (no Google Fonts <link>, no @import)
  [ ] 3 SMIL <animate> elements: 2 dots + 1 divider. No more, no less
  [ ] README references branding/banner.svg with width="100%"
````

---

## Pre-built palette presets

These are tested 5-step ramps. Copy the block matching your product into the
`<defs>` block of your banner.svg, replacing the existing gradient stops.

### Orange (Claude Ads, default, "warm CRT phosphor")

```
wordGrad stops:    #F7C9A8 -> #E89270 -> #D97757 -> #7A3A1F
dividerGrad stops: #D97757 -> #F5B095 -> #D97757
accent (HUD dots, /, >): #D97757
deep accent (HUD text):  #7A3A1F
```

### Teal / sea-green (Claude SEO, "ops console")

```
wordGrad stops:    #B6DECE -> #8BC0A8 -> #4F7B6E -> #2B4A41
dividerGrad stops: #4F7B6E -> #8BC0A8 -> #4F7B6E
accent (HUD dots, /, >): #4F7B6E
deep accent (HUD text):  #2B4A41
```

### Purple (Claude Blog, "publishing terminal")

```
wordGrad stops:    #C9B3E6 -> #9075BD -> #7B5EA7 -> #3F2C5C
dividerGrad stops: #7B5EA7 -> #B49DD6 -> #7B5EA7
accent (HUD dots, /, >): #7B5EA7
deep accent (HUD text):  #3F2C5C
```

### Cobalt blue (Claude API style)

```
wordGrad stops:    #AFC9EE -> #6790CD -> #4A77C7 -> #234176
dividerGrad stops: #4A77C7 -> #8DAEDD -> #4A77C7
accent (HUD dots, /, >): #4A77C7
deep accent (HUD text):  #234176
```

### Crimson (high-attention launches)

```
wordGrad stops:    #F4B7A5 -> #DC6E50 -> #C94A2C -> #6E2415
dividerGrad stops: #C94A2C -> #F09078 -> #C94A2C
accent (HUD dots, /, >): #C94A2C
deep accent (HUD text):  #6E2415
```

---

## What stays constant across all variants

These elements form the cross-repo brand identity. Do not change:

- Background gradient: `#1A1612 -> #110E0B -> #060504` (radial, top to bottom)
- Top + bottom HUD bar background: `#0A0807` solid
- Aspect ratio: 21:9 (viewBox 0 0 1680 720)
- Typography: Inter for tagline, `ui-monospace` for HUD + commands
- HUD layout pattern: top-left = SYS slug + node, top-right = uptime.
  Bottom-left = live dot + 3 status tokens, bottom-right = identifier + UTC clock
- Animation: exactly 3 SMIL anims (top dot 1.6s, bottom dot 1.6s, divider 6s)
- Vignette: radial gradient transparent center to 35 percent black corners
- Scanline overlay: horizontal lines every 5px on the wordmark rect, 55 percent opacity

The only things that change per product are: wordmark text, slug, tagline,
system-line stats, command list (7 verbs), status tokens, identifier, and
the 5-step accent palette.

---

## Why this works as a brand system

- Constant chrome plus variable accent equals product family. Every banner
  feels like the same OS booted with a different module. The viewer reads
  "another tool in the same family" before they parse the product name.
- One palette swap plus one wordmark edit equals full re-skin. No other
  edits needed. An agent can produce a new repo banner end-to-end in under
  60 seconds given the inputs above.
- SVG-native plus SMIL animations means the banner renders identically on
  GitHub, RSS, AI crawlers, docs sites, and any environment that supports
  inline SVG. No render step, no build pipeline, no font dependencies.

---

## File checklist for the target repo

After running through the process, the target repo should have:

```
target-repo/
├── branding/
│   ├── banner.svg                  (NEW, around 7KB)
│   ├── AGENT-PROMPT.md             (this file)
│   ├── README.md                   (system index, adapt from claude-blog)
│   └── diagrams/                   (optional, for architecture visuals)
│       ├── *.md                    (mermaid sources)
│       └── *.svg                   (pre-rendered via mmdc)
└── README.md                       (references branding/banner.svg at top)
```

If you want only the banner (no diagrams, no system docs), drop just
`branding/banner.svg` in the target repo and you are done.
