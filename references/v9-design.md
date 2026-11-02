# V9 design and no-regression constraints

- Source PNG/JPG remains the only visual ground truth.
- Preserve previous stable builder; only add safe connectors and inspections.
- Native editable: text, card geometry, simple gradients, boundaries, straight/elbow connectors.
- Pixels: detailed icons, unusual shadows, photo/artwork, texture and poorly understood paths.
- All fragments must correspond to semantically meaningful objects, never Canny edges or glyph paths.
- Don't overlay an uncleaned full-image background with extracted editable text, or duplicates will appear.
- Local masks/inpainting are *not automatic*. If source pixels cannot be removed reliably, convert the region to one image and mark that portion noneditable.
- Quality gate: render/compare per page; character and field list completeness should be checked manually or via a separate trusted text ledger. Similarity score by itself does not validate text or flow correctness.
