---
name: darkmode-doc-youge
description: 把 Word/PDF/Excel/图片 批量转成护眼模式（暖色低对比黑底，比纯黑底白字更不刺眼）。v2.0 新增「两档模式」：默认只改文档背景+文字（保留插图原色，适合彩色照片/地图/截图），加 `--invert-images` 才同时反色所有插图（含 WMF 数学公式，需 wmf2gd）。性能优化：批处理大量 .doc 老格式时自动按目录分组复用 LibreOffice 进程，提速 10-20 倍。内置 4 套护眼主题：warm（暖杏色，类 Kindle Paperwhite Dark，默认）/ paper（仿羊皮纸 sepia）/ gray（暖灰色）/ pure（纯黑底白字，旧版兼容）。PDF 用图像反色（兼容扫描件/试卷/复杂排版），DOCX 改页面背景+文字色（可选反色插图，反色后整体压到主题暖色），XLSX 改单元格底色与字体色，单图（jpg/png/jpeg/bmp/gif/tiff/webp）直接温柔反色（适合拍照作业、纸质截图、网页截图）。支持单文件转换或递归批处理整个目录，每个文件独立异常隔离。只要用户提到"护眼模式"、"黑底白字"、"夜间阅读"、"暗色文档"、"试卷护眼"、"暖色护眼"、"刺眼"、"图片护眼"、"拍照作业护眼"，都应立即触发本 skill。触发词："护眼模式"、"黑底白字"、"暗色模式"、"darkmode"、"dark mode"、"夜间模式"、"反色文档"、"试卷护眼"、"PDF 黑底"、"Word 黑底"、"暖色护眼"、"刺眼"、"晃眼"、"换主题"、"图片护眼"、"拍照作业护眼"、"截图反色"、"插图反色"、"保留插图原色"。
---

# darkmode-doc-youge — 文档护眼模式转换大师

## 🆕 v2.0 重大升级（2026-05）

| 升级点 | 说明 |
|---|---|
| **两档模式** | 默认只改背景+文字保留插图原色；加 `--invert-images` 才反色所有插图 |
| **WMF 公式反色** | 数学公式 Word 老格式（WMF 矢量图）自动用 `wmf2gd` 转 PNG 后反色，覆盖率 95%+ |
| **.doc 批量提速** | 按子目录分组复用 soffice 进程，处理 100+ 个 .doc 提速 10-20 倍 |
| **默认行为变更** | DOCX/DOC 默认**不反色插图**（旧版默认反色），照片/地图保持原色 |

## 🎨 4 套护眼主题（科学护眼配色）

| 主题 | 背景 | 文字 | 边框 | 对比度 | 适用 |
|---|---|---|---|---|---|
| **warm**（默认 ⭐ 推荐） | `#1F1F1F` 暖深灰 | `#D4C9A8` 暖米杏 | `#5A5142` | ~11:1 | 类 Kindle Paperwhite Dark，最护眼 |
| `paper` | `#1B1A17` 烤纸黑 | `#D8C9A0` 旧纸黄 | `#5A5142` | ~12:1 | 仿羊皮纸 sepia 暗色，复古纸感 |
| `gray` | `#262626` 暖炭灰 | `#D4D4D4` 暖灰白 | `#555555` | ~12:1 | 偏冷淡的护眼方案 |
| `pure` | `#000000` 纯黑 | `#FFFFFF` 纯白 | `#FFFFFF` | 21:1 | 旧版纯黑白（最高对比，最刺眼） |

**为什么不用纯黑+纯白？**
- 纯白 #FFFFFF 配纯黑 #000000 对比度 21:1，是公认**最伤眼**的组合
- WCAG AAA 推荐对比度 ≥ 7:1 即可保证可读性，无需拉满
- Apple Dark Mode / VS Code Dark+ / GitHub Dark / Kindle 暗色阅读 **全部不用纯白纯黑**
- 暖色系（偏黄红）降低蓝光刺激，长时间阅读最舒适

## 核心能力

| 格式 | 默认（不反色插图） | `--invert-images`（反色插图） | 输出 |
|---|---|---|---|
| **PDF** | 整页栅格化反色 ⚠️ 始终整页反色，无法区分图文 | 同左 | `xxx_dark.pdf` |
| **DOCX** | 背景+文字+表格+边框变护眼色，**插图保持原色** | 同时温柔反色所有 PNG/JPEG/BMP/GIF/TIFF/WEBP 插图 + WMF 数学公式（需 `wmf2gd`） | `xxx_dark.docx` |
| **DOC** | 自动 `soffice` 转 DOCX 后同上 | 同上 | `xxx_dark.docx` |
| **XLSX** | 单元格 `PatternFill` 主题底色 + `Font` 主题色字体 + 主题边框 | 同左（XLSX 无内嵌图片处理） | `xxx_dark.xlsx` |
| **图片**（jpg/jpeg/png/bmp/gif/tiff/webp） | EXIF 旋转校正 + 温柔反色（单图工具本身就是反色目的） | 同左 | `xxx_dark.<ext>` |

## 何时选哪档？

**默认模式（推荐用于含彩色插图的文档）**
- 化学/物理 课本（含彩色实验照片、电路图）
- 地理/历史 教材（含彩色地图、文物照片）
- 商业报告（含品牌图标、产品截图、彩色图表）
- 食谱/旅游攻略（含食物照片、风景照片）

**`--invert-images` 模式（推荐用于黑白线条文档）**
- 数学/物理 试卷（公式、几何图、坐标图大量是黑白线条）
- 法律/医学 教材（图表多为黑白示意图）
- 学术论文（图表、流程图通常黑白）
- 任何"白底黑线条占主导"的文档

## 使用方法

### 一、批处理整个目录（推荐）

```bash
# 默认 warm 暖杏色主题，仅改背景+文字，不动插图
python3 ~/.cursor/skills/darkmode-doc-youge/scripts/darkmode_batch.py "/path/to/dir"

# 加 --invert-images 同时反色所有插图（含 WMF 数学公式）
python3 ~/.cursor/skills/darkmode-doc-youge/scripts/darkmode_batch.py "/path/to/dir" --invert-images

# 指定主题
python3 ~/.cursor/skills/darkmode-doc-youge/scripts/darkmode_batch.py "/path/to/dir" --theme paper
python3 ~/.cursor/skills/darkmode-doc-youge/scripts/darkmode_batch.py "/path/to/dir" --theme pure --invert-images
```

可选参数：
- `--invert-images` 同时反色 DOCX 内嵌插图（含 WMF 公式）。**默认不反色**
- `--theme {warm|paper|gray|pure}` 护眼主题（默认 warm）
- `--no-recursive` 只处理当前层不递归
- `--dpi 300` PDF 渲染分辨率（默认 200，调高更清晰但更慢）
- `--out /custom/dir` 自定义输出目录

### 二、单文件转换

```bash
# PDF
python3 ~/.cursor/skills/darkmode-doc-youge/scripts/darkmode_pdf.py input.pdf [output.pdf] [--dpi 200] [--theme warm]

# DOCX 默认（保留插图原色）
python3 ~/.cursor/skills/darkmode-doc-youge/scripts/darkmode_docx.py input.docx [output.docx] [--theme warm]

# DOCX 同时反色插图（含 WMF 公式）
python3 ~/.cursor/skills/darkmode-doc-youge/scripts/darkmode_docx.py input.docx [output.docx] --invert-images [--theme warm]

# XLSX
python3 ~/.cursor/skills/darkmode-doc-youge/scripts/darkmode_xlsx.py input.xlsx [output.xlsx] [--theme warm]

# 图片（jpg/png/jpeg/bmp/gif/tiff/webp）
python3 ~/.cursor/skills/darkmode-doc-youge/scripts/darkmode_image.py input.jpg [output.jpg] [--theme warm]
```

## 工作准则（铁律）

1. **绝不覆盖原文件**：所有输出统一加 `_dark` 后缀放到 `dark/` 子目录
2. **默认保留插图原色**：彩色照片、地图、产品截图反色后会很难看；只有用户明确要求 `--invert-images` 才反色插图
3. **DOCX 反色模式必须包含 WMF**：试卷数学公式大量用 WMF 矢量图存储，传统 PIL 解码器不支持。本 skill 自动调用 `wmf2gd` 转 PNG 后再反色，保证公式不留白底
4. **PDF 无法分图文**：PDF 渲染机制决定了整页栅格化反色，`--invert-images` 选项对 PDF 无差异
5. **异常隔离**：批处理时单个文件失败要继续处理下一个，最后汇总报告
6. **临时锁文件必须跳过**：`~$xxx.docx`、`.~xxx.docx` 是 Word 打开文件时的锁，处理会报错
7. **`.doc` 批量必走预转换**：100+ 个 .doc 必须按目录分组复用 soffice，否则单文件启动开销会让总时间×10
8. **如果用户说"刺眼/晃眼"**：默认 warm 太亮就换 `paper`，太黄就换 `gray`，从不退回 `pure`

## 温柔反色（gentle_invert）原理

传统反色是简单的 `255 - x`，结果是：
- 原图白底 (255,255,255) → 输出纯黑 (0,0,0)  → 刺眼边缘 + 黑度溢出
- 原图黑文字 (0,0,0)    → 输出纯白 (255,255,255) → 晃眼

温柔反色用主题 LUT 重新映射：
- 原图白底 → 输出主题背景色（如 #1F1F1F 暖深灰）
- 原图黑文字 → 输出主题前景色（如 #D4C9A8 暖米杏）
- 中间灰度按线性插值

这样图片完全融入文档色调，整页观感统一不刺眼。

## WMF 数学公式反色（v2.0 新增）

Word 老格式（.doc）的数学公式通常以 WMF 矢量图嵌入，Python PIL 默认无 WMF 解码器，
这导致传统反色方案下，公式块仍是白底，护眼效果大打折扣。

本 skill 集成 `libwmf` 的 `wmf2gd` 工具，流程：
1. 检测 docx 内 `*.wmf` → 调用 `wmf2gd` 转 PNG（5ms/张，极快）
2. 用 `gentle_invert` 反色新生成的 PNG
3. 修改 `[Content_Types].xml` 添加 PNG 默认类型
4. 修改 `*.rels` 把 `.wmf` 引用改为 `.png`
5. 删除原 WMF 文件，重新打包 docx

**仅在 `--invert-images` 模式下执行**。若环境没装 `wmf2gd`，自动跳过（不报错），仅普通图片反色。

启用：
```bash
brew install libwmf
```

## 依赖

| 依赖 | 用途 | 何时必需 |
|---|---|---|
| `PyMuPDF` (fitz) | PDF 渲染 | 处理 PDF |
| `python-docx` | DOCX 处理 | 处理 DOCX/DOC |
| `Pillow` | 图像反色 | 所有图片相关 |
| `openpyxl` | XLSX 处理 | 处理 XLSX |
| `LibreOffice` (`soffice`) | DOC→DOCX 转换 | 处理 .doc 老格式 |
| `libwmf` (`wmf2gd`) | WMF 矢量公式转 PNG | `--invert-images` 模式下含 WMF 的 docx |

安装：
```bash
pip3 install --user --break-system-packages PyMuPDF python-docx Pillow openpyxl
brew install libreoffice libwmf
```

## 触发词清单

`护眼模式` / `黑底白字` / `暗色模式` / `darkmode` / `dark mode` / `夜间模式` / `反色文档` / `试卷护眼` / `PDF 黑底` / `Word 黑底` / `给文档换底色` / `暖色护眼` / `刺眼` / `晃眼` / `换主题` / `图片护眼` / `拍照作业护眼` / `截图反色` / `插图反色` / `保留插图原色` / `只改背景文字`

## 输出示例

```
/path/to/dir/
├── 2024年深圳中考化学.docx          ← 原文件（含彩色实验图）
├── 2025年深圳中考数学.doc            ← Word 97-2003 老格式（含 WMF 公式）
├── 化学知识点考频统计.xlsx
└── dark/                              ← 护眼版（自动生成）
    ├── 2024年深圳中考化学_dark.docx  ← 默认：背景黑 + 文字暖，实验图原色
    ├── 2025年深圳中考数学_dark.docx  ← --invert-images: 公式 WMF 全部反色
    └── 化学知识点考频统计_dark.xlsx
```
