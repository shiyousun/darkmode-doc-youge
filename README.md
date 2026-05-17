# 🌙 darkmode-doc-youge

> **把 Word / PDF / Excel / 图片 一键转成「真护眼」文档** —— 暖色低对比黑底，比纯黑底白字更不刺眼。
> 让晚上看试卷、长时间看资料、看拍照作业不再伤眼睛。

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 🆕 v2.0 重大升级（2026-05）

| 升级点 | 说明 |
|---|---|
| **两档模式** | 默认只改背景+文字，**保留插图原色**（适合照片/地图/截图）；加 `--invert-images` 才反色所有插图 |
| **WMF 公式反色** | 数学公式的 Word 老格式（WMF 矢量图）也能反色，覆盖率 95%+（需 `libwmf` 的 `wmf2gd`） |
| **.doc 批量提速** | 按子目录分组复用 LibreOffice 进程，处理 100+ 个 .doc **提速 10-20 倍** |
| **默认行为变更** | DOCX/DOC 默认**不反色插图**（旧版默认反色），让彩色照片保持原色 |

> **实测**：处理 202 个中考真题文件（30 PDF + 39 DOCX + 133 DOC，含 3021 张数学公式 WMF），仅用 **6.4 分钟**，0 失败。

---

## 🎨 为什么不用纯黑 + 纯白？

很多人以为 "黑底白字" 就是护眼。**错。**

- 纯白 `#FFFFFF` 配纯黑 `#000000` 对比度 **21:1**，是公认**最伤眼**的组合
- WCAG AAA 推荐对比度 ≥ 7:1 即可保证可读性，**无需拉满**
- Apple Dark Mode / VS Code Dark+ / GitHub Dark / Kindle 暗色阅读 **全部不用纯白纯黑**
- 暖色系（偏黄红）降低蓝光刺激，长时间阅读最舒适

本工具内置 **4 套科学护眼配色**，默认 `warm` 暖杏色（类 Kindle Paperwhite Dark Mode），对比度 ~11:1，清晰但不刺眼。

| 主题 | 背景 | 文字 | 对比度 | 适用 |
|---|---|---|---|---|
| **warm**（默认 ⭐） | `#1F1F1F` 暖深灰 | `#D4C9A8` 暖米杏 | ~11:1 | 类 Kindle Paperwhite Dark |
| `paper` | `#1B1A17` 烤纸黑 | `#D8C9A0` 旧纸黄 | ~12:1 | 仿羊皮纸 sepia 暗色 |
| `gray` | `#262626` 暖炭灰 | `#D4D4D4` 暖灰白 | ~12:1 | 偏冷淡的护眼方案 |
| `pure` | `#000000` 纯黑 | `#FFFFFF` 纯白 | 21:1 | 旧版（最高对比，最刺眼） |

---

## ✨ 核心特性

- 📄 **5 类格式**：PDF / DOCX / DOC / XLSX / 图片（jpg/png/jpeg/bmp/gif/tiff/webp）
- 🎨 **4 套主题**：warm / paper / gray / pure，一键切换
- 🌗 **两档模式**：默认保留插图原色 / `--invert-images` 反色所有插图（含 WMF 数学公式）
- 🌟 **温柔反色（gentle_invert）**：图片不是简单 invert，而是反色后用 LUT 把白色压到主题暖色，跟文档融为一体
- 🚀 **.doc 批量提速**：按子目录分组复用 soffice，100+ 个 .doc 比逐个调用快 10-20 倍
- ➗ **WMF 公式反色**：用 `libwmf` 的 `wmf2gd` 把数学公式矢量图转 PNG 再反色，传统 Python 处理不到的"白底公式"也能护眼
- 📁 **批量处理**：递归扫描整个目录，输出到 `dark/` 子目录，**保留原层级结构**
- 🛡️ **异常隔离**：单个文件失败不影响其他，最后输出汇总报告
- 🔒 **绝不覆盖原文件**：所有输出加 `_dark` 后缀，原文件零修改

---

## 🚀 快速开始

### 安装依赖

```bash
# Python 库
pip3 install --user --break-system-packages PyMuPDF python-docx Pillow openpyxl

# macOS 系统工具（处理 .doc 老格式 + WMF 数学公式必装）
brew install libreoffice libwmf
```

### 何时选哪档？

| 场景 | 推荐模式 |
|---|---|
| 化学/物理课本（含彩色实验照片、电路图） | **默认**（保留照片原色） |
| 地理/历史教材（含彩色地图、文物照片） | **默认** |
| 商业报告、产品截图 | **默认** |
| 食谱、旅游攻略 | **默认** |
| 数学/物理试卷（公式、几何图大量黑白线条） | `--invert-images` |
| 法律/医学教材、学术论文 | `--invert-images` |

### 批处理整个目录（推荐）

```bash
# 默认 warm 主题，仅改背景+文字，不动插图
python3 scripts/darkmode_batch.py "/path/to/your/dir"

# 加 --invert-images 同时反色所有插图（含 WMF 数学公式）
python3 scripts/darkmode_batch.py "/path/to/your/dir" --invert-images

# 指定其他主题
python3 scripts/darkmode_batch.py "/path/to/your/dir" --theme paper
python3 scripts/darkmode_batch.py "/path/to/your/dir" --theme pure --invert-images
```

可选参数：
- `--invert-images` 同时反色 DOCX 内嵌插图（含 WMF 公式）。**默认不反色**
- `--theme {warm|paper|gray|pure}` 护眼主题（默认 warm）
- `--no-recursive` 只处理当前层不递归
- `--dpi 300` PDF 渲染分辨率（默认 200）
- `--out /custom/dir` 自定义输出目录

### 单文件转换

```bash
# PDF（始终整页栅格化反色，无图文区分能力）
python3 scripts/darkmode_pdf.py input.pdf [output.pdf] [--dpi 200] [--theme warm]

# DOCX 默认（保留插图原色）
python3 scripts/darkmode_docx.py input.docx [output.docx] [--theme warm]

# DOCX 同时反色插图（含 WMF 公式）
python3 scripts/darkmode_docx.py input.docx [output.docx] --invert-images [--theme warm]

# XLSX
python3 scripts/darkmode_xlsx.py input.xlsx [output.xlsx] [--theme warm]

# 单图护眼（拍照作业、纸质截图、网页截图）
python3 scripts/darkmode_image.py input.jpg [output.jpg] [--theme warm]
```

---

## 🧠 核心算法

### 温柔反色（gentle_invert）

传统反色是简单的 `255 - x`，结果是：
- 原图白底 (255,255,255) → 输出纯黑 (0,0,0) → **刺眼边缘 + 黑度溢出**
- 原图黑文字 (0,0,0) → 输出纯白 (255,255,255) → **晃眼**

本工具用主题 LUT 重新映射：
- 原图白底 → 输出主题背景色（如 `#1F1F1F` 暖深灰）
- 原图黑文字 → 输出主题前景色（如 `#D4C9A8` 暖米杏）
- 中间灰度按线性插值

这样图片完全融入文档色调，**整页观感统一不刺眼**。

```python
def make_warm_lut(bg_rgb, fg_rgb):
    """生成 R/G/B 三通道 LUT，把反色后值线性映射到主题色域。"""
    bg_r, bg_g, bg_b = bg_rgb
    fg_r, fg_g, fg_b = fg_rgb
    r_lut = [bg_r + (fg_r - bg_r) * i // 255 for i in range(256)]
    g_lut = [bg_g + (fg_g - bg_g) * i // 255 for i in range(256)]
    b_lut = [bg_b + (fg_b - bg_b) * i // 255 for i in range(256)]
    return r_lut + g_lut + b_lut
```

### WMF 数学公式反色（v2.0 新增）

Word 老格式（.doc）的数学公式通常以 WMF 矢量图嵌入，Python PIL 默认无 WMF 解码器，导致传统反色方案下，公式块仍是白底——尤其数学/物理试卷护眼效果大打折扣。

本工具集成 `libwmf` 的 `wmf2gd` 工具（5ms/张），流程：
1. 检测 docx 内 `*.wmf` → `wmf2gd` 转 PNG（保留主题最大宽高 2400px）
2. 用 `gentle_invert` 反色新生成的 PNG
3. 修改 `[Content_Types].xml` 添加 PNG 默认类型
4. 修改 `*.rels` 把 `.wmf` 引用改为 `.png`
5. 删除原 WMF 文件，重新打包 docx

**仅在 `--invert-images` 模式下执行**。若环境没装 `wmf2gd`，自动跳过（不报错）。

### .doc 批量提速（v2.0 新增）

`.doc` 老格式必须通过 LibreOffice 转 `.docx` 才能处理。原版逐文件调用 soffice，每次冷启动 5 秒，100 个 .doc = 8 分钟启动开销。

新版按子目录分组批量调用：
```bash
soffice --headless --convert-to docx --outdir /tmp/g1 a.doc b.doc c.doc ...
```
每个目录只启动一次 soffice，**133 个 .doc 实测 28.9 秒搞定**（提速 23 倍）。

---

## 📁 输出示例

```
/path/to/dir/
├── 2024年深圳中考化学.docx          ← 原文件（含彩色实验图）
├── 2025年深圳中考数学.doc            ← Word 97-2003 老格式（含 WMF 公式）
├── 化学知识点考频统计.xlsx
├── 拍照作业.jpg
└── dark/                              ← 护眼版（自动生成）
    ├── 2024年深圳中考化学_dark.docx  ← 默认：背景黑+文字暖，实验图原色
    ├── 2025年深圳中考数学_dark.docx  ← --invert-images: 公式 WMF 全部反色
    ├── 化学知识点考频统计_dark.xlsx
    └── 拍照作业_dark.jpg
```

---

## 📊 实测案例

### 案例 1：202 个中考真题文档（含数学公式）

| 处理项 | 数量 | 耗时 |
|---|---|---|
| `.doc` → `.docx` 批量预转换 | 133 个 | **28.9 秒** |
| skill batch 主流程 | 335 个文件 | 298.1 秒 |
| WMF 数学公式反色 | 3021 张 | **55.9 秒** |
| **合计** | **202 → 202 成功，0 失败** | **~6.4 分钟** |

数学/物理 答案卷里，**单个解析卷含 400+ 张公式 WMF**，全部温柔反色到暖深灰底 + 暖米杏字，护眼效果直接拉满。

### 案例 2：24 个中考试卷（v1.0 历史数据）

| 文件类型 | 数量 | 处理 |
|---|---|---|
| PDF（含数学/物理/英语/语文/作文） | 12 | 200dpi 渲染 + 温柔反色 |
| DOCX（含化学/英语/道法） | 11 | 文档背景 + 文字 + 116 张内嵌题图反色 |
| XLSX（化学考点统计） | 1 | 单元格底色 + 字体 |
| **合计** | **24/24 成功** | **耗时 134 秒** |

---

## 🛠 各脚本说明

| 脚本 | 用途 |
|---|---|
| `scripts/themes.py` | 4 套护眼主题配置 + `gentle_invert` 核心算法 |
| `scripts/darkmode_pdf.py` | PDF 反色（PyMuPDF 渲染 + PIL 温柔反色） |
| `scripts/darkmode_docx.py` | DOCX 反色（背景 + 文字 + 表格 +（可选）插图 + WMF 公式） |
| `scripts/darkmode_xlsx.py` | XLSX 反色（单元格 + 字体 + 边框） |
| `scripts/darkmode_image.py` | 单图反色（含 EXIF 旋转校正） |
| `scripts/darkmode_batch.py` | 批处理入口（递归扫描 + .doc 批量预转换 + 异常隔离 + 汇总报告） |

---

## 📦 依赖

| 依赖 | 用途 | 何时必需 |
|---|---|---|
| `PyMuPDF` (fitz) | PDF 渲染 | 处理 PDF |
| `python-docx` | DOCX 处理 | 处理 DOCX/DOC |
| `Pillow` | 图像反色 | 所有图片相关 |
| `openpyxl` | XLSX 处理 | 处理 XLSX |
| `LibreOffice` (`soffice`) | DOC→DOCX 转换 | 处理 .doc 老格式 |
| `libwmf` (`wmf2gd`) | WMF 矢量公式转 PNG | `--invert-images` 模式下含 WMF 的 docx |

---

## ⚠️ 已知限制

1. **PDF 无法保留图片原色**：PDF 渲染机制决定了整页栅格化反色，无法分离图片与文字。`--invert-images` 选项对 PDF 无差异。
2. **WMF 公式需要 wmf2gd**：未装 `libwmf` 时，`--invert-images` 模式下 WMF 会跳过（不影响普通图片反色）。
3. **`.doc` 必须装 LibreOffice**：headless soffice 命令必须可用。

---

## 🤝 作者

由 **友哥 & AI** 共同创造，献给所有长时间用电脑、手机看文档的眼睛。

希望你的眼睛不再因为白底文档而疲劳。

---

## 📜 License

MIT License — 自由使用、修改、分发。
