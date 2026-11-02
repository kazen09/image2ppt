---
name: image2ppt-1to1-pro
description: 将 PNG/JPG 原始设计图高保真重建为 PPTX。
---

# Image2PPT V21.2 — Full merged icon-enforced edition

## 强制执行流程
1. 以原始截图为唯一视觉参考，OCR 和版面分析生成场景文件。
2. 识别所有图标并生成 `icons-manifest.json`，在场景元素中标注 `role=icon` 与 `icon_id`。
3. **必须**调用 `scripts/icon_crop_apply.py` 从原图裁剪图标，生成新的 scene JSON。**不许用内置图标或原生 PPT 形状替代**。
4. 在调用 `build_pptx_connectors.py` 前，检查裁剪结果。构建器会拒绝缺少 `asset_origin=source_crop` 的图标元素。
5. 保留 V19 单对象多拐点折线；对双向语义连接使用**一条线、首尾各一个箭头端点**，不要绘制两条平行单向线。
6. 使用 V20 的 `text_layout_gate.py`、`legend_layout_lock.py` 和 `style_lock_report.py` 检查文字、图例和渐变/边框/阴影。
7. 渲染 PPTX 和原图比较。禁止随意重新排版。

图标需要源图片裁剪，插入的是独立图片对象：**可移动、可缩放，但图标内部不具备全原生编辑能力**。不得把这一例外宣称为 fully editable。

## 必须阅读
- `references/icon-enforcement.md`
- `references/per-page-workflow.md`

## 常用命令
```powershell
uv sync --extra ocr
uv run python scripts/icon_crop_apply.py --scene scene.json --manifest icons-manifest.json --out-scene scene-cropped.json --asset-dir icons
uv run python scripts/build_pptx_connectors.py --scene scene-cropped.json --out output.pptx
```
