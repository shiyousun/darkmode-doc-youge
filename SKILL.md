---
name: darkmode-doc-youge
description: 把 Word/PDF/Excel/图片 批量转成护眼模式（暖色低对比黑底，比纯黑底白字更不刺眼）。内置 4 套护眼主题：warm（暖杏色，类 Kindle Paperwhite Dark，默认）/ paper（仿羊皮纸 sepia）/ gray（暖灰色）/ pure（纯黑底白字，旧版兼容）。PDF 用图像反色（兼容扫描件/试卷/复杂排版），DOCX 改页面背景+文字色并对内嵌图片做温柔反色（反色后整体压到主题暖色，色调与文档一致），XLSX 改单元格底色与字体色，单图（jpg/png/jpeg/bmp/gif/tiff/webp）也能直接温柔反色（适合拍照作业、纸质截图、网页截图）。支持单文件转换或递归批处理整个目录，每个文件独立异常隔离。只要用户提到"护眼模式"、"黑底白字"、"夜间阅读"、"暗色文档"、"试卷护眼"、"暖色护眼"、"刺眼"、"图片护眼"、"拍照作业护眼"，都应立即触发本 skill。触发词："护眼模式"、"黑底白字"、"暗色模式"、"darkmode"、"dark mode"、"夜间模式"、"反色文档"、"试卷护眼"、"PDF 黑底"、"Word 黑底"、"暖色护眼"、"刺眼"、"晃眼"、"换主题"、"图片护眼"、"拍照作业护眼"、"截图反色"。
---

# darkmode-doc-youge — 文档护眼模式转换大师

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

| 格式 | 处理方式 | 输出 |
|---|---|---|
| **PDF** | 每页 200dpi 渲染→**温柔反色（反色+主题色 LUT 映射）**→嵌入新 PDF | `xxx_dark.pdf` |
| **DOCX** | 设置页面背景为主题深色 + 所有 run 字体改主题前景色 + 表格底色改深色 + 边框改主题边框色 + **内嵌图片温柔反色**（反色后压到主题暖色，与文档融为一体） | `xxx_dark.docx` |
| **DOC** | 自动调用 `soffice` 转 DOCX 后再处理 | `xxx_dark.docx` |
| **XLSX** | 全部单元格 `PatternFill` 主题底色 + `Font` 主题色字体 + 主题边框 | `xxx_dark.xlsx` |
| **图片**（jpg/jpeg/png/bmp/gif/tiff/webp） | 自动 EXIF 旋转校正 → **温柔反色** → 按原扩展名保存 | `xxx_dark.<ext>` |

## 使用方法

### 一、批处理整个目录（推荐）

```bash
# 默认 warm 暖杏色主题
python3 ~/.cursor/skills/darkmode-doc-youge/scripts/darkmode_batch.py "/path/to/dir"

# 指定主题
python3 ~/.cursor/skills/darkmode-doc-youge/scripts/darkmode_batch.py "/path/to/dir" --theme paper
python3 ~/.cursor/skills/darkmode-doc-youge/scripts/darkmode_batch.py "/path/to/dir" --theme gray
python3 ~/.cursor/skills/darkmode-doc-youge/scripts/darkmode_batch.py "/path/to/dir" --theme pure
```

可选参数：
- `--theme {warm|paper|gray|pure}` 护眼主题（默认 warm）
- `--no-recursive` 只处理当前层不递归
- `--no-images` DOCX 不反色内嵌图片
- `--dpi 300` PDF 渲染分辨率（默认 200，调高更清晰但更慢）
- `--out /custom/dir` 自定义输出目录

### 二、单文件转换

```bash
# PDF
python3 ~/.cursor/skills/darkmode-doc-youge/scripts/darkmode_pdf.py input.pdf [output.pdf] [--dpi 200] [--theme warm]

# DOCX
python3 ~/.cursor/skills/darkmode-doc-youge/scripts/darkmode_docx.py input.docx [output.docx] [--no-images] [--theme warm]

# XLSX
python3 ~/.cursor/skills/darkmode-doc-youge/scripts/darkmode_xlsx.py input.xlsx [output.xlsx] [--theme warm]

# 图片（jpg/png/jpeg/bmp/gif/tiff/webp）
python3 ~/.cursor/skills/darkmode-doc-youge/scripts/darkmode_image.py input.jpg [output.jpg] [--theme warm]
```

## 工作准则（铁律）

1. **绝不覆盖原文件**：所有输出统一加 `_dark` 后缀放到 `dark/` 子目录
2. **DOCX 内嵌图片必须温柔反色**：试卷题图、化学方程式图大多白底，简单 invert 会变纯白线条仍刺眼，必须用 LUT 把白线条压到主题暖色，跟文字融为一体
3. **PDF 用图像方案而非文本染色**：保证扫描件、复杂排版、含公式的 PDF 都能正确护眼
4. **异常隔离**：批处理时单个文件失败要继续处理下一个，最后汇总报告
5. **临时锁文件必须跳过**：`~$xxx.docx`、`.~xxx.docx` 是 Word 打开文件时的锁，处理会报错
6. **如果用户说"刺眼/晃眼"**：默认 warm 太亮就换 `paper`，太黄就换 `gray`，从不退回 `pure`

## 温柔反色（gentle_invert）原理

传统反色是简单的 `255 - x`，结果是：
- 原图白底 (255,255,255) → 输出纯黑 (0,0,0)  → 刺眼边缘 + 黑度溢出
- 原图黑文字 (0,0,0)    → 输出纯白 (255,255,255) → 晃眼

温柔反色用主题 LUT 重新映射：
- 原图白底 → 输出主题背景色（如 #1F1F1F 暖深灰）
- 原图黑文字 → 输出主题前景色（如 #D4C9A8 暖米杏）
- 中间灰度按线性插值

这样图片完全融入文档色调，整页观感统一不刺眼。

## 依赖

- `PyMuPDF` (fitz) — PDF 渲染
- `python-docx` — DOCX 处理
- `Pillow` — 图像反色
- `openpyxl` — XLSX 处理
- `LibreOffice` (`soffice`) — 仅在转 .doc 时需要

安装：
```bash
pip3 install --user --break-system-packages PyMuPDF python-docx Pillow openpyxl
```

## 触发词清单

`护眼模式` / `黑底白字` / `暗色模式` / `darkmode` / `dark mode` / `夜间模式` / `反色文档` / `试卷护眼` / `PDF 黑底` / `Word 黑底` / `给文档换底色` / `暖色护眼` / `刺眼` / `晃眼` / `换主题` / `图片护眼` / `拍照作业护眼` / `截图反色`

## 输出示例

```
/path/to/dir/
├── 2024年深圳中考化学.docx          ← 原文件
├── 2025年深圳中考化学.docx
├── 化学知识点考频统计.xlsx
└── dark/                              ← 护眼版（自动生成）
    ├── 2024年深圳中考化学_dark.docx
    ├── 2025年深圳中考化学_dark.docx
    └── 化学知识点考频统计_dark.xlsx
```
