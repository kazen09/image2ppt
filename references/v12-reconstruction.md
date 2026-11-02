# V12 image-to-PPT fidelity guide

## Reference is binding
- Source image coordinates and original colors are authoritative. Preserve page ratio, all major containers and the 9 numbered flow cards on example architecture diagrams.
- Each object needs stable id, type, native bounds, z, source visual crop region, confidence, and style provenance. Unknown values remain unknown; do not invent exact gradient stops or font family and call them original.
- Before build: inspect header, legend, five architecture columns, nested cards, numbered arrows, footer; record measured box coordinates and flow directions.

## Prioritize failures
1. Missing or rewritten technical text/JSON; overflow or clipped text
2. Missing/wrong flow direction, arrow endpoints and overlaps
3. Container positions/width/height; internal padding
4. Native icon approximation where original detail was lost
5. Font family/weight/size/baselines
6. Gradients/borders/shadows and subtle colors

## Iteration rule
- Save best candidate and source-aligned element manifest.
- Render every page, inspect image diff by region, target 1-3 worst regions per revision.
- Rebuild only objects affected. If visual quality becomes worse or text decreases, reject and restore best.
- Preserve author-provided source images and accepted PPTX untouched.

## Editable integrity
- Text must be editable, not vector glyphs.
- Borders/cards/native shapes must remain distinct editable shapes.
- Arrow geometry must retain source route, not be randomly simplified.
- Complex visual source cannot be reliably reverse-engineered to 100% native objects from pixels alone. Mark exceptions and uncertainty; no fake pass.
