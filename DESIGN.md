# Design

The project page is a modern laboratory notebook: each entry asks a question, pastes in a plate, records the verdict and cites in the margin. Tokens live in `src/styles/global.css`; layout in `src/styles/page.css`.

## Colour

| Token | Value | Use |
| --- | --- | --- |
| `--paper` | `#f4f2ec` | page ground (cool notebook white, not cream) |
| `--paper-2` | `#ebe8df` | quiet fills (verdict box, hover) |
| `--grid` / `--grid-strong` | `#d3dbe0` / `#b7c3cb` | 20 px quad grid, **only** under plates and the hero field; chart gridlines |
| `--ink` | `#1b1530` | text, rules, primary marks (hematoxylin violet-black) |
| `--ink-2` / `--ink-3` | `#463f5c` / `#6b6480` | secondary text, captions, axis labels |
| `--rule` | `#c9c4d4` | hairlines |
| `--tracer` | `#d10f63` | the single signal colour: DPP4⁺ / SSc / significant, margin rule, focus ring, selection |
| `--tracer-ink` | `#a10b4c` | tracer as text (AA on paper) |
| `--tracer-wash` | `#f7d9e5` | tracer fills, "supports" verdict chip |
| `--hema` / `--hema-wash` | `#4b3fa0` / `#e2dff2` | comparison channel: control, lower-in-SSc, "refines" verdict |

Rule: tracer means signal. Never decorate with it.

## Type

- **Display:** Gloock 400 (headings, node labels, big numbers). Max ~4.3 rem in the hero.
- **Text:** Source Serif 4 (variable, optical sizing) for prose, 66ch measure.
- **UI / captions:** Geist (variable).
- **Data:** Geist Mono, only for numbers, gene symbols (italic, `.gene`), accessions and axis ticks.

## Structure

- `.row`: a two-column grid, the notebook column (66ch) plus a 15 rem margin column of references (tracer left rule). The margin collapses below 1100 px, where citations open as popovers.
- `.plate`: a figure pasted into the notebook. It has a 1 px ink frame over the grid ground, an optional title, a caption and a "show the original figure" disclosure.
- Results follow the same order every time: verdict chip, question (h3), data line (sans, small), plate, finding (larger serif).
- No cards, no eyebrows, no section numbers. Corners are 2 px; chips are the only pill shape.

## Motion

- Plates "develop" once on entry: opacity 0.35 → 1 with a slight blur, through an exponential ease-out. Reduced motion disables it.
- The hero canvas runs only while visible and renders a static frame under reduced motion.

## Citations

Copy uses `[@key;key]`. `src/lib/cite.ts` numbers references by first appearance across the dictionary, compresses ranges (1–3,5) and renders superscripts, the margin notes and the reference list. `npm run check:refs` verifies the build.
