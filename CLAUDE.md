# Poster Development Guide

## Overview

This is an HTML symposium poster (35" x 25", landscape) served locally with live-reload. The poster is developed
iteratively: Claude Code edits the HTML directly, the user edits text inline in the browser, and edits sync back
to the server via `edits.json`.

## Getting Started

1. Start the dev server: `uv run serve.py` (runs on port 8787)
2. Open `http://localhost:8787/poster.html` in a browser — **not** `file://`, or edits/reload won't work
3. The page auto-reloads every 500ms when the HTML file changes (polls `Last-Modified` header)
4. Text is editable inline: click any text, type, click away or press Escape. Edits are saved server-side.

## Architecture

### Files

- `poster.html` — the poster, self-contained HTML/CSS/JS
- `serve.py` — Python dev server with `Last-Modified` headers and `/edits` API
- `edits.json` — server-side store of user's inline text edits (JSON: `{key: innerHTML}`)
- `measure.html` — diagnostic page that measures column content heights via iframe
- `assets/mats-logo.svg` — MATS logo (downloaded from matsprogram.org)

### Dev Server (`serve.py`)

- `GET /poster.html` — serves the poster with `Last-Modified` + `Cache-Control: no-cache` headers
- `GET /edits` — returns current `edits.json` contents
- `POST /edits` — body `{"key": "...", "value": "..."}`, merges into `edits.json`
- `POST /edits/clear` — resets `edits.json` to `{}`
- HEAD request logging is suppressed to reduce noise

### Auto-Reload

The poster includes a polling script that sends `HEAD` requests every 500ms and compares `Last-Modified`. If the
file changed, it reloads — **unless** the user is currently editing text (`editingActive` flag), to avoid
clobbering in-progress edits.

### Troubleshooting

- **"CORS request not http" errors**: You're opening via `file://`. Use `http://localhost:8787/poster.html`.
- **Auto-reload not working**: Check `serve.py` is running (`lsof -ti:8787`). The old `python3 -m http.server`
doesn't send `Last-Modified` headers — must use `serve.py`.
- **Edits not persisting**: Verify `curl -s http://localhost:8787/edits` returns JSON. If empty after editing, the
    old server (without `/edits` routes) may still be holding the port — kill it and restart `serve.py`.
- **Server won't start**: Kill existing process on port 8787: `lsof -ti:8787 | xargs kill`, then restart.
- **Fonts not loading**: Fonts are loaded from Google Fonts CDN. Requires internet.

## Poster Layout

### Dimensions

- 3360px x 2400px (35" x 25" at 96dpi), landscape
- Scaled to fit viewport via CSS `transform: scale()` with JS computing the scale factor from `window.innerWidth`
and `window.innerHeight`
- `transform-origin: top left`

### Grid Structure

```
+---------------------------------------------------+
|                  HEADER BAR                        |
|  Title | Byline | Authors+Avatars | MATS Logo     |
+-----------------+-----------------+---------------+
|   Left Column   |  Middle Column  | Right Column  |
|                 |                 |               |
|  Hero Plot A    |  Results        | Conclusion    |
|  Caption        |  (4-plot grid)  | Plot+caption  |
|  Hero Plot B    |                 |               |
|  Caption        |  Methods        | Next Steps    |
|                 |                 |               |
|  Problem        |                 | Links & QR    |
|  (callout+text) |                 |               |
|                 |                 |               |
|  Solution       |                 |               |
|  (callout+text) |                 |               |
+-----------------+-----------------+---------------+
```

- Three equal-width columns (`grid-template-columns: 1fr 1fr 1fr`)
- Header spans full width (`grid-column: 1 / -1`)
- Columns separated by 2px border lines
- Sections within columns separated by 1px bottom borders
- Column padding: 36px 44px

### Reading Flow

Header -> Left column (top to bottom) -> Middle column -> Right column

## Typography (LessWrong-inspired)

### Fonts

- **Headings**: Libre Baskerville (serif) — 700 weight
- **Body**: Source Sans 3 (sans-serif) — 400 weight
- Both loaded from Google Fonts

### Sizes (poster-scale, not screen-scale)

- Title (h1): **88px**, weight 700, letter-spacing -1px
- Byline: **38px**, italic, serif
- Author names: **28px**, weight 600, sans
- Author affiliations: **22px**, sans
- Section headings (h2): **52px**, weight 700, serif
- Body text / list items: **32px**, line-height 1.55, sans
- Callout text: **32px**, italic, serif
- Takeaway captions: **34px**, italic, serif
- Plot placeholder labels: **24px**, weight 500, sans
- QR labels: **24px**, weight 500, sans
- Tooltips: **24px** (scaled with poster)
- References/small text: **16-18px**

## Colour Scheme

### CSS Custom Properties

```css
--text: #2c2c2c;           /* primary body text */
--text-secondary: #555;     /* byline, lighter text */
--text-muted: #888;         /* affiliations, labels */
--heading: #1a1a1a;         /* headings, strong text */
--bg: #fafaf7;              /* poster background (warm off-white) */
--card: #ffffff;            /* header background */
--border: #e0ddd5;          /* divider lines, avatar borders */
--accent: #801323;          /* MATS red — callout borders, tab highlights */
--accent-dark: #630c19;     /* MATS dark red — header bottom border, takeaway text */
--accent-light: #f5e8eb;    /* callout background tint */
```

### Plot Placeholder Colours (OKLAB)

Six distinct colours for placeholder rectangles, using oklch():
- plot-a: oklch(0.55 0.12 250) — blue
- plot-a2: oklch(0.55 0.12 280) — indigo
- plot-b: oklch(0.55 0.12 310) — purple
- plot-c: oklch(0.55 0.12 150) — teal
- plot-d: oklch(0.55 0.12 30) — coral
- plot-e: oklch(0.55 0.12 90) — olive
- plot-f: oklch(0.55 0.12 200) — cyan

### Browser Chrome

- Page background: #e8e8e4
- Tab bar: #f5f5f5 with #d0d0d0 bottom border

## Component Styles

### Header

- White background (--card) with 6px --accent bottom border
- Flexbox: text area (flex:1) + logo area
- Author avatars: 72px circles, #f0ede6 background, 3px border
- Authors separated from mentors by a | character (class author-sep)

### Callout Blocks

- 5px left border in --accent
- --accent-light background
- Italic serif text
- Rounded right corners (6px)

### Takeaway Captions

- Italic serif, --accent-dark colour
- Appear directly below plot placeholders

### QR Code Section

- Row of QR placeholder boxes (160x160px, white, 3px border)
- Editable labels beneath each

### Tab System

- Sticky tab bar at top of page (not part of poster)
- showTab(name) toggles .tab-content visibility
- Active tab persisted in sessionStorage
- Each tab contains a full .poster-wrap > .poster structure
- Currently: v1 (main) and v2 (alt layout placeholder)

## Inline Editing System

### How It Works

- Elements with `data-e="key"` attribute are editable
- On page load, `initEditing()` fetches `GET /edits` and applies saved values
- Click -> sets `contentEditable=true`, shows red outline
- Blur (or Escape) -> `contentEditable=false`, POSTs `{key, value}` to `/edits`
- Auto-reload pauses while `editingActive` is true
- "reset text edits" button in tab bar calls `POST /edits/clear` and reloads

### Key Naming Convention

- `title`, `byline` — header
- `l-*` — left column (e.g. l-h2, l-bg1, l-rq, l-m1)
- `m-*` — middle column (e.g. m-h1, m-desc, m-a1)
- `r-*` — right column (e.g. r-h1, r-d1, r-c1)
- `plot-a`, `plot-b`, etc. — plot placeholder labels
- `qr1-label`, `qr2-label`, `qr3-label` — QR code labels

### Integration Workflow

1. User edits text in browser -> saved to edits.json
2. Claude reads `cat edits.json` to see changes
3. Claude inlines edits into HTML (fixing typos, converting markdown to HTML)
4. Claude runs `curl -s -X POST http://localhost:8787/edits/clear` to reset
5. Page auto-reloads with new HTML defaults

### Special Edit Commands

Users may write `@claude remove` in an editable field to signal that element should be deleted from the HTML.

## Hover Tooltips

- Elements with `data-tip="..."` show tooltips on hover
- Positioned above the element, centred
- Dark background (#1a1a1a), 24px text, max-width 600px
- Used to describe what content should replace the lorem ipsum

## Commits

- Make frequent, granular commits (one per logical change)
- Use conventional commit prefixes: `feat:`, `fix:`, `style:`, `content:`
- Include `Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>`

## Column Measurement

To measure remaining space in each column, open `http://localhost:8787/measure.html`. It renders the poster in an
iframe at full size, measures each column's content height vs available height, and POSTs results to the
`_measurements` key in edits.json.
