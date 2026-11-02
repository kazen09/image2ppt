# Scene JSON (source-pixel coordinates)

Top-level: `{ "slide":{"width_px":1920,"height_px":1080,"width_in":13.333333}, "pages":[{"name":"page-01","background":{"color":"#FFFFFF"},"elements":[...] }]}`

`background` may be `{"color":"#FFFFFF"}` or `{"image":"assets/clean_plate.png"}`. Background image must be **free of any text reconstructed on top**.

All element `x/y/w/h` in original source **pixels** (not inches), optional `z` numeric. Missing `z` means list position; builder sorts by `z` with stable order.

Types:
- `text`: `text`, `x,y,w,h`, `font_family`, `font_size_pt`, `color`, `bold`, `italic`, `align`, `valign`, `margin_px`, `line_spacing`, `rotation`, `opacity`, `shadow` (simple outer), `fill`, `border`. Optionally `runs:[{text,font_family,font_size_pt,bold,italic,color}]`. `font_size_pt` must be measured/inferred separately (coordinate scaling doesn't determine original text size).
- `shape`: `geometry: rect|roundRect|ellipse|line`, `x,y,w,h`, `fill:{color,opacity}|{gradient:{angle,stops:[{pos,color,opacity}]}}`, `border:{color,width_pt,opacity}`, `radius` for rounded rect approximate shape (PowerPoint preset radius not pixel-exact), `shadow:{color,blur_pt,distance_pt,angle,opacity}`.
- `image`: `src`, `x,y,w,h`, `opacity` (opacity currently unsupported: pre-render the alpha into the source asset for exactness), `rotation`.

A background may be a photo/gradient preserved from a clean source image. Gradients and shadows supported by XML are approximations; verify in PowerPoint.

Example in `examples/scene.json`. Images are resolved relative to the scene JSON directory. No remote URLs supported. No missing-file fallback.
