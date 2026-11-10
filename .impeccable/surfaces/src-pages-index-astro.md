---
version: 1
slug: "src-pages-index-astro"
primary_target: "src/pages/index.astro"
related_targets: ["src/pages/pt/index.astro"]
---

# Surface: project page (EN `/`, PT `/pt/`)

Mode: Persuade/Experience hybrid. A portfolio visitor (recruiter, PI, biotech founder) decides in a minute whether the author does rigorous computational biology and tells it well. Action: follow the evidence to the decision; secondary: notebook repo, back to castlelli.github.io.
Proof: deck evidence, own D3 re-plots (exact where code holds values, digitized + labeled otherwise), every claim cited Nature-style.
Constraints: bilingual; no names; no claims beyond deck; hypothesis, not treatment advice.

## Direction contract

THESIS: The page is the lab notebook of one hypothesis: each entry asks a question, shows the plate, records the verdict, cites in the margin. Refuses the biotech landing template (dark hero, glowing molecule, metric row, card grid).

OWN-WORLD: Notebook paper (#F4F2EC, not cream) with a 5 mm blue-grey quad grid that appears only under data plates; hematoxylin violet-black ink (#1B1530) for type and marks; one fluorescent eosin tracer (#E5126F) reserved for DPP4+/SSc signal and the margin rule. Gloock display, Source Serif 4 text, Geist Mono strictly for numbers, genes, accessions. Hairline plate frames, figure labels "a b c", superscript citations, margin column of references.

STORY: Visitor learns the disease and the bet, watches seven independent evidence layers tested, sees which held and which the data refused, believes the decision is honest, ends at the designed experiment and the author's role.

FIRST VIEWPORT: Left 5/12: the question set in Gloock at ~5.5rem, one-line answer status below ("Verdict: advance to proof-of-mechanism — not an efficacy claim"), actions "Follow the evidence" + "Jump to the verdict", EN/PT toggle top right. Right 7/12, bleeding to the edge: live canvas fibroblast field on the grid, DPP4+ cells in tracer laying eosin collagen strands; a vertical dose slider (pointer or keyboard) inhibits DPP-4 and the margin readout logs deposition rate. Labelled "schematic, not data".

FORM: Modern laboratory notebook / Nature paper re-set by a studio; seed: none (pinned) — user: "Lab notebook, modern — Warm paper-white, ink-black serif display, one saturated tracer color (like a fluorescent stain). Margin notes with citations, like a Nature paper redesigned by a studio."

Signature interaction: the dose control (hero) returning as the PK explorer (Kpu × IC50 sliders). Motion grammar: ink "develops" (stroke-draw + fade from visible default) when a plate enters; nothing else animates on scroll.

FINISH: unreviewed and undocumented is unfinished; this build ends with the finish review, the verdict, DESIGN.md, and every shipping raster carrying its provenance
