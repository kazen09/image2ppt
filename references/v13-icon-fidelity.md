# V13 图标保真协议

## 核心原则
- 默认 `full_editable`；不允许使用相似的符号、emoji、图标库来假装已经重建了源图图标。
- **full_editable 与 crop_first 不能同时完全满足**：裁剪出来的 PNG 是不可逐图形编辑的。V13 的 `crop_first` 是“高保真临时占位/待矢量重建”策略，必须在报告中登记为 `raster_fallback`，最终 full_editable 验收不得把它计为原生对象。
- 对于必须全可编辑的用户，默认 `editable_first`：只有通过局部图像对比与复杂度门禁的原生矢量重建才算通过；否则标记 `unresolved_editable`，不以风格近似图标替代。
- 用户显式选择 visual_exact 或批准可编辑例外时，允许 `crop_first` 把图标作为独立位图嵌入。
- 不做自动全图抠图或“图片轮廓 -> 数千 Freeform”转换，不要自动图标库匹配。

## 图标记录格式
用一份 `icons.json` 记录原图页索引（从1开始）、绝对像素 bbox、名称、scene 元素 id、相对关系和可编辑状态。例如 `examples/icons.json`。

## 局部验收步骤
1. 标记原图 icon_bbox，并截图保存原始区域。
2. 原生重建模式：仅用语义可编辑形状、数量有上限；生成候选后裁出渲染区域，计算 SSIM / MAE，质量差时拒收。
3. 裁图模式：crop icon_bbox，必须避免把原图相邻文本一起切入；如需保留完整底色，使用不透明裁图，不自动抠背景。
4. 锁定图标的像素 bbox；其与标题、正文之间的相对距离不得变更。
5. 每页报告 `accepted_editable`, `raster_fallback`, `unresolved_editable` 三类计数；`full_editable` 下后两项不算验收完成。
6. 保留最佳 PPTX 基线，不得为了更换图标重排页面。

## 工具
- `icon_asset_extract.py` 按 bbox 可靠裁图（不推测边界）。
- `icon_similarity_gate.py` 同尺寸对比源图 icon 和生成图标（结构和色彩误差）。
- `icon_layout_lock.py` 计算待发布 scene.json 的图标 bbox 是否相对源标注发生移动、缩放。
