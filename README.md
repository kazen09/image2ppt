# Image2PPT 1:1 Pro

[简体中文](README.md) | [English](README_EN.md)

> 将 PNG / JPG 参考设计图重建为尽可能贴近原图的 PowerPoint。优先保留文本、形状、边框、渐变与连接线的可编辑性；图标采用原图裁剪，以避免风格失真。

**当前版本：V21.2（图标来源强制校验）** · **本地运行** · **Codex Skill + Python 工具链**

## 项目介绍

Image2PPT 1:1 Pro 是面向技术架构图、流程图和信息密集型演示稿的图片转 PPTX 工作流。它结合 AI 辅助的视觉理解与场景建模、PowerPoint 原生对象生成、源图图标裁剪和渲染差异检查。Skill 负责指导 Codex 按流程执行；仓库脚本提供场景到 PPTX 的构建、检查与素材处理工具。

**请注意：本项目不是“传入任何图片即可无误获得 100% 原生可编辑 PPT”的一键式转换引擎。** 当前生成流程仍依赖 Codex 或操作者构建/校核结构化 `scene.json`。对于没有原始图层信息的图片，字体、遮挡关系与复杂特效可能无法精确恢复。

## 主要特性

- **布局与层级**：根据 `scene.json` 的元素坐标、尺寸和 `z` 顺序生成页面，减少自动重排。
- **原生文本与形状**：文本框、矩形、圆角矩形、圆形、边框、部分渐变与阴影可以编辑。
- **单对象折线**：支持包含多个拐点的完整路径；按设计记录端点和路径。
- **双向箭头**：支持在一条线的两端设置箭头端点，避免用两条平行箭头模拟查询/响应。
- **图标保真**：标记为 `role=icon` 的元素必须来自源图裁剪；禁止被通用自绘图标悄悄替代。
- **视觉验收**：支持逐页渲染、差异图、区域比较与文字、图例、样式检查。
- **多页支持**：场景文件可包含多个页面，并可分别检查。

## 可编辑性说明

| 对象 | 当前处理 | 是否可编辑 |
|---|---|---|
| 标题、正文、列表 | PowerPoint 文本框 | 是 |
| 矩形、圆角容器、圆形 | PowerPoint 原生形状 | 是 |
| 直线、折线、双向箭头 | 原生连接线或单一自由路径 | 是（自由路径不等于自动吸附连接器） |
| 简单渐变、边框、阴影 | 原生样式（支持范围内） | 是 |
| 从原图裁剪的图标 | 独立 PNG 图片对象 | 可移动/缩放，内部图形**不可**逐个编辑 |
| 复杂视觉效果 | 视可重建程度处理 | 无法保证全可编辑 |

`full_editable` 是优先目标，而非对每一个图标与像素的完成保证。项目当前优先让源图裁剪图标保持保真，并在输出中明确其非原生性质。

## 环境要求

- Python **3.11 或 3.12**
- 推荐安装 [uv](https://docs.astral.sh/uv/) 管理虚拟环境与依赖
- Windows / macOS / Linux：实际兼容性取决于 Python 与 OCR 推理环境
- [LibreOffice](https://www.libreoffice.org/)：可选，用于自动渲染 PPTX；也可以用 PowerPoint 手动导出预览
- PaddleOCR 3.x：可选，用于 OCR；需要另行配置兼容的 PaddlePaddle 推理引擎，并下载模型

## 安装

```powershell
# 将项目放到 Codex Skill 目录（以下为 Windows 示例）
cd "$env:USERPROFILE\.codex\skills\image2ppt-1to1-pro"

# 安装基础依赖
uv sync

# 需要 OCR 时安装 OCR 可选依赖
uv sync --extra ocr

# 检查环境
uv run python scripts/doctor.py
uv run python scripts/check_module_shadowing.py
```

如果 `uv` 未安装，可按 [uv 官方安装指南](https://docs.astral.sh/uv/getting-started/installation/) 安装。**PaddleOCR 的安装不保证 PaddlePaddle 推理引擎已经可用**；首次运行可能需要单独配置和下载模型。

## Codex 中使用

将项目目录放入 `~/.codex/skills/image2ppt-1to1-pro/`，确保根目录存在 `SKILL.md`。然后在 Codex 中输入：

```text
$image2ppt-1to1-pro 把这张图片尽量 1:1 还原为可编辑 PPT。
```

也可直接说“将这张架构图还原为 PPT”，但显式指定 Skill 更可靠。

## 手动转换流程

本项目的转换器**需要场景描述文件**，不能仅凭以下命令自动从任意图片推导出全部对象。Codex 或开发者需先识别图片，建立 `scene.json` 并标记图标。

1. 根据源图建立 `scene.json`，记录文本、形状、坐标、图层及连接路径。
2. 为图标准备 `icons-manifest.json`，记录原图文件及图标裁剪区域。
3. 裁剪图标、改写场景中的图标元素，并构建 PPTX：

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

4. 对 PPTX 进行渲染和对比：

```powershell
uv run python scripts/render.py --pptx output.pptx --out preview
uv run python scripts/compare.py --reference reference.png --rendered preview --out qa
```

如果是多页输入，`--reference` 可指向按照页面顺序命名的图片目录。其他检查脚本可参阅 `scripts/` 与 `references/`。

## 目录说明

```text
image2ppt-1to1-pro/
├── SKILL.md                     # Codex Skill 指令
├── README.md                    # 中文说明
├── README_EN.md                 # English README
├── pyproject.toml               # uv / Python 依赖
├── requirements.txt             # pip 依赖清单
├── scripts/
│   ├── build_pptx_connectors.py  # 场景生成 PPTX
│   ├── icon_crop_apply.py        # 原图裁剪与图标替换
│   ├── icon_gate.py              # 图标来源校验
│   ├── ocr_extract.py            # OCR 辅助
│   ├── render.py                 # PPTX 渲染
│   ├── compare.py                # 原图与渲染结果比较
│   └── ...
├── references/                  # 规范和流程说明
└── examples/                    # 场景及清单示例
```

## 质量与限制

- 一张图片无法直接提供原始字体文件、真正的图层树或精确的渐变参数；还原通常需要人工校核。
- 单个自由路径与 PowerPoint 可自动吸附的连接器不同。折线“单对象”不意味着端点会自动跟随其他形状移动。
- OCR 可能误识别中英文混排的字段，尤其是 `partyId`、`tnCode`、`recordType`、`answerIp` 等；请核对生成文字。
- 图标裁剪准确度依赖边界坐标及源图片质量。裁剪后的 PNG 不是原生可编辑矢量图标。
- 不同 PowerPoint / LibreOffice 版本以及缺失字体，可能引起渲染差异。

## 开源发布清单

发布前建议：

1. 确认项目名称、仓库地址和维护者信息。
2. **确定许可证并新增 `LICENSE` 文件**。本包没有擅自声明任何开源协议。
3. 检查第三方代码及素材许可；不要上传无权分发的字体、图标、模型权重或用户设计稿。
4. 添加有权公开的输入图、输出 PPT 与对比截图，并注明生成条件。
5. 在 GitHub 上设置 Issues / Contributions 规则（可选）。

## 鸣谢与参考

项目的设计思路借鉴了开源社区中的 PPT 还原与转换工作流，包括 [ppt-image2-editable-rebuild](https://github.com/wwe-dog/ppt-image2-editable-rebuild) 与 [svg2pptx-skill](https://github.com/JamieJustTang/svg2pptx-skill) 的公开理念。**此说明不意味着本项目复用了上述仓库的代码或得到其官方背书**。若后续复制第三方代码，请按实际来源保留版权声明并遵守其许可证。

---

欢迎通过 Issues 提交还原误差、兼容性问题和可复现的测试样例。
