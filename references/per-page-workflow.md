# Per-page native editable reconstruction protocol

## Input contract
An existing screenshot is the visual source of truth. Do **not** call imagegen to redraw it. A new picture created by imagegen is not a valid substitute for source pixels. Read one image per page; never use a contact sheet as a page source.

## Output contract
One scene JSON, PPTX slide, rendered preview, OCR ledger and QA JSON for every page. Freeze an accepted page before moving to the next. Preserve previous candidate for rollback.

## Scene reconstruction checklist
- Record canvas resolution and slide aspect ratio exactly, then normalized boundaries, units, visibility and z-index of every semantic object.
- OCR extract, manually/visually reconcile ambiguous technical fields and numbers, never rewrite semantic content. Preserve explicit breaks for JSON, code and tables; prose should wrap naturally when the rendering is validated.
- Measure font family candidates, weight, size, kerning approximation, baseline, line spacing, alignment and text box padding. Candidate fonts aren't proof of original family.
- Map cards and backgrounds to native shapes; map simple gradients and shadows to native DrawingML if supported; do not flatten or substitute images silently.
- Map connectors to native endpoints and arrowheads; verify their visible direction and route. No independent triangle heads.
- Never trace image contours or glyphs into hundreds of Freeforms. A complex raster logo cannot be guaranteed fully editable: report exception instead of claiming success.
- z-order is based on visible occlusion. Do not presume invisible layers from screenshot. Record ambiguous cases.

## Acceptance gates
1. Source content complete: all manually verified text and labels accounted for.
2. Structure: no full-slide picture; connectors native; no Freeform explosion; no clipped content.
3. Render: compare against original, inspect per region, especially fonts, line baseline, borders, layers, gradients and shadows. Pixel metrics are diagnostic, not proof.
4. Regression: candidate must not be worse than prior accepted result. A failing repair is reverted.
5. Publish the editability exceptions (including icons), unresolved mismatches, and previews honestly.

## Commands
```sh
python scripts/reference_manifest.py source1.png source2.png --out work/manifest.json
python scripts/page_qa.py work/result.pptx --out work/qa-structure.json
python scripts/regression_gate.py --baseline work/best.pptx --candidate work/result.pptx --out work/regression.json
```
