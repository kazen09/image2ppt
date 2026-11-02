# 图标强制来源校验

图标不是需要由 PPT 原生形状自由发挥的对象。固定图标必须在场景标记 `role: icon` 和 `icon_id`，且 `type:image`、`asset_origin:source_crop`。

1. 建立 icons-manifest.json（id, page, x, y, w, h 和 source_image）。
2. 原图裁剪写回场景：`python scripts/icon_crop_apply.py --scene scene.json --manifest icons-manifest.json --out-scene scene-cropped.json --asset-dir icons`。
3. 可选对完整图标清单使用 `icon_gate.py`，确保每个要求图标都已裁剪。
4. 构建器对标记为 icon 但非 source_crop 图片的对象直接抛错，而不是悄悄自绘。
5. 图标是独立的可移动/缩放图片对象，**内部并非完全可编辑**；用户要求 full_editable 时应在报告中明确例外。
6. 若源图中的图标无法干净裁切，请标记未完成，不得使用近似的 PowerPoint 图标代替。
