# Image2PPT 1:1 Pro

[简体中文](README.md) | [English](README_EN.md)

> Rebuild PowerPoint presentations from PNG/JPG reference images while aiming for high visual fidelity and editable text, shapes, gradients, borders, and connectors. Icons are cropped from the source image to avoid inaccurate substitutions.

**Version: V21.2 (enforced icon provenance)** · **Local workflow** · **Codex Skill + Python utilities**

## Overview

Image2PPT 1:1 Pro is an image-to-PPTX reconstruction workflow for architecture diagrams, flowcharts, and information-dense slides. It combines AI-assisted scene interpretation, native PowerPoint object generation, source-image icon cropping, and visual regression checks. The Skill guides Codex through the workflow; included scripts process assets, inspect scenes, and build PPTX files.

**This is not a guaranteed one-click, pixel-perfect, 100%-native-editable converter.** Creating and verifying a structured `scene.json` still requires Codex or an operator. A flat image does not reveal its exact original font, layer hierarchy, or visual-effect parameters.

## Features

- **Layout and z-order:** Generate pages from element coordinates, dimensions, and `z` ordering stored in a scene file.
- **Native PowerPoint elements:** Editable text boxes, rectangles, rounded rectangles, circles, borders, and supported gradients/shadows.
- **Single-object polyline:** Multi-bend paths are represented as one editable path object.
- **Bidirectional arrows:** Arrowheads at both ends of a single path instead of two parallel one-way lines.
- **Icon fidelity:** Elements marked `role=icon` must use source-image crops; unexpected placeholder drawings are rejected.
- **Visual QA:** Slide rendering, diff images, region-level comparisons, and checks for text, legends, and styling.
- **Multi-slide workflows:** Scene files can describe multiple pages.

## What Is Editable?

| Element | Representation | Editability |
|---|---|---|
| Titles, body text, lists | Native PowerPoint text boxes | Editable |
| Rectangles, rounded cards, circles | Native shapes | Editable |
| Straight lines, polylines, two-ended arrows | Native connectors or a single freeform path | Editable; freeform paths do not auto-snap like connectors |
| Supported gradients, borders, shadows | Native PowerPoint styles | Editable |
| Cropped icons | Individual PNG image objects | Movable/resizable; internal artwork **not** individually editable |
| Complex effects | Best-effort reconstruction | Not guaranteed fully editable |

`full_editable` is the preferred reconstruction goal, not a guarantee for every pixel or icon. Cropped source icons deliberately prioritize visual fidelity over native vector editability.

## Prerequisites

- Python **3.11 or 3.12**
- [uv](https://docs.astral.sh/uv/) recommended for environment and dependency management
- Windows, macOS, or Linux, subject to package and OCR backend compatibility
- [LibreOffice](https://www.libreoffice.org/) (optional) for automated PPTX rendering; PowerPoint can export previews manually
- PaddleOCR 3.x (optional); requires a compatible PaddlePaddle inference runtime and model files

## Installation

```powershell
# Windows example: enter the installed Codex Skill directory
cd "$env:USERPROFILE\.codex\skills\image2ppt-1to1-pro"

uv sync
uv sync --extra ocr  # Optional OCR dependencies
uv run python scripts/doctor.py
uv run python scripts/check_module_shadowing.py
```

If `uv` is unavailable, follow the [official installation instructions](https://docs.astral.sh/uv/getting-started/installation/). Installing the PaddleOCR package alone may not install a working PaddlePaddle runtime; model downloads and additional setup may be required.

## Use with Codex

Place the project in `~/.codex/skills/image2ppt-1to1-pro/`, with `SKILL.md` at the root. In Codex, prompt:

```text
$image2ppt-1to1-pro Rebuild this image as an editable PowerPoint, matching the reference as closely as possible.
```

Explicitly naming the Skill is more reliable than relying on automatic matching.

## Manual Pipeline

The builder requires a **structured scene description**. The commands below do not automatically detect and reconstruct every element from an arbitrary input image.

1. Build `scene.json` from the reference image, recording text, geometry, coordinates, z-order, and connector paths.
2. Prepare `icons-manifest.json`, listing icon IDs, their source images, and pixel crop rectangles.
3. Crop icons and generate the PowerPoint:

```powershell
uv run python scripts/icon_crop_apply.py `
  --scene scene.json `
  --manifest icons-manifest.json `
  --out-scene scene-cropped.json `
  --asset-dir icons

uv run python scripts/build_pptx_connectors.py `
  --scene scene-cropped.json `
  --out output.pptx
```

4. Render and compare:

```powershell
uv run python scripts/render.py --pptx output.pptx --out preview
uv run python scripts/compare.py --reference reference.png --rendered preview --out qa
```

For multiple slides, `--reference` can be a directory containing ordered reference images. See `scripts/` and `references/` for additional validators.

## Repository Structure

```text
image2ppt-1to1-pro/
├── SKILL.md                     # Codex Skill instructions
├── README.md                    # Chinese README
├── README_EN.md                 # English README
├── pyproject.toml               # uv / Python dependencies
├── requirements.txt             # pip dependency list
├── scripts/
│   ├── build_pptx_connectors.py  # Scene -> PPTX
│   ├── icon_crop_apply.py        # Crop and replace icons
│   ├── icon_gate.py              # Icon provenance validation
│   ├── ocr_extract.py            # OCR helper
│   ├── render.py                 # PPTX rendering
│   ├── compare.py                # Image comparison
│   └── ...
├── references/                  # Workflow and QA guidance
└── examples/                    # Sample scenes and manifests
```

## Limitations

- A raster image does not contain the original font files, layer tree, or exact gradient/effect parameters. Human review is often necessary.
- A single freeform path is editable but does not provide all auto-attachment behaviors of a native PowerPoint connector.
- OCR can confuse technical tokens such as `partyId`, `tnCode`, `recordType`, and `answerIp`; check all generated text.
- Icon crop accuracy depends on image quality and bounding-box coordinates. A cropped PNG is not an editable vector icon.
- Fonts and rendering engines differ across PowerPoint and LibreOffice versions.

## Before Publishing as Open Source

1. Verify the repository name, owner, and contact information.
2. **Choose a license and add a `LICENSE` file.** This package intentionally does not claim a license on your behalf.
3. Audit any third-party source code and assets; do not redistribute fonts, artwork, model weights, or user designs without permission.
4. Include sample source images and PPTX outputs you are permitted to share, with documented reproduction steps.
5. Optionally add contribution guidelines and issue templates.

## Acknowledgments and Inspiration

The workflow draws inspiration from publicly discussed approaches in projects such as [ppt-image2-editable-rebuild](https://github.com/wwe-dog/ppt-image2-editable-rebuild) and [svg2pptx-skill](https://github.com/JamieJustTang/svg2pptx-skill). **This does not imply code reuse, endorsement, or affiliation.** If you later incorporate third-party code, retain the relevant notices and comply with the source licenses.

---

Issues reporting visual discrepancies, environment problems, and reproducible test cases are welcome.
