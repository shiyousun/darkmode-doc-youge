#!/usr/bin/env python3
"""
darkmode_docx.py — 把 Word (.docx) 转成护眼模式

处理项：
- 页面背景改主题深色（启用 displayBackgroundShape）
- 所有正文 / 表格 / 页眉 / 页脚 中的文字改主题前景色
- 表格单元格底色改主题深色
- 表格边框改主题边框色
- 内嵌图片温柔反色（反色 + 主题色映射，色调与文档一致）

用法：
    python3 darkmode_docx.py input.docx [output.docx] [--no-images] [--theme warm]
"""
from __future__ import annotations

import argparse
import io
import shutil
import sys
from pathlib import Path

from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from PIL import Image

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from themes import DEFAULT_THEME, THEMES, gentle_invert, get_theme


def _ensure_setting(settings_element, tag: str) -> None:
    el = settings_element.find(qn(tag))
    if el is None:
        el = OxmlElement(tag)
        settings_element.append(el)


def set_page_background(doc, color_hex: str) -> None:
    """设置 Word 页面背景色 + 启用打开时显示背景。"""
    settings = doc.settings.element
    _ensure_setting(settings, "w:displayBackgroundShape")

    document_element = doc.element
    background = document_element.find(qn("w:background"))
    if background is None:
        background = OxmlElement("w:background")
        document_element.insert(0, background)
    background.set(qn("w:color"), color_hex)


def set_run_color(run, color_hex: str) -> None:
    """把一个 run 的字体颜色设置为指定色。"""
    rPr = run._element.get_or_add_rPr()
    color_el = rPr.find(qn("w:color"))
    if color_el is None:
        color_el = OxmlElement("w:color")
        rPr.append(color_el)
    color_el.set(qn("w:val"), color_hex)
    if color_el.get(qn("w:themeColor")) is not None:
        del color_el.attrib[qn("w:themeColor")]


def set_paragraph_default_color(paragraph, color_hex: str) -> None:
    """段落默认字体色（兜底没有 run 的情况）。"""
    pPr = paragraph._p.get_or_add_pPr()
    rPr = pPr.find(qn("w:rPr"))
    if rPr is None:
        rPr = OxmlElement("w:rPr")
        pPr.append(rPr)
    color_el = rPr.find(qn("w:color"))
    if color_el is None:
        color_el = OxmlElement("w:color")
        rPr.append(color_el)
    color_el.set(qn("w:val"), color_hex)


def set_cell_background(cell, color_hex: str) -> None:
    tcPr = cell._tc.get_or_add_tcPr()
    shd = tcPr.find(qn("w:shd"))
    if shd is None:
        shd = OxmlElement("w:shd")
        tcPr.append(shd)
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), color_hex)


def set_table_borders(table, color_hex: str) -> None:
    tblPr = table._element.find(qn("w:tblPr"))
    if tblPr is None:
        tblPr = OxmlElement("w:tblPr")
        table._element.insert(0, tblPr)
    borders = tblPr.find(qn("w:tblBorders"))
    if borders is None:
        borders = OxmlElement("w:tblBorders")
        tblPr.append(borders)
    for tag in ("top", "left", "bottom", "right", "insideH", "insideV"):
        el = borders.find(qn(f"w:{tag}"))
        if el is None:
            el = OxmlElement(f"w:{tag}")
            borders.append(el)
        el.set(qn("w:val"), "single")
        el.set(qn("w:sz"), "4")
        el.set(qn("w:space"), "0")
        el.set(qn("w:color"), color_hex)


def process_paragraph(paragraph, font_color: str) -> None:
    set_paragraph_default_color(paragraph, font_color)
    for run in paragraph.runs:
        set_run_color(run, font_color)


def process_table(table, font_color: str, cell_bg: str, border_color: str) -> None:
    set_table_borders(table, border_color)
    for row in table.rows:
        for cell in row.cells:
            if cell_bg:
                set_cell_background(cell, cell_bg)
            for paragraph in cell.paragraphs:
                process_paragraph(paragraph, font_color)
            for nested in cell.tables:
                process_table(nested, font_color, cell_bg, border_color)


def invert_image_blob(blob: bytes, fmt_hint: str, theme: dict) -> bytes | None:
    """对 docx 内嵌图片做温柔反色。失败返回 None。"""
    try:
        img = Image.open(io.BytesIO(blob))
        original_mode = img.mode
        warm = gentle_invert(img, theme)

        ext = fmt_hint.lower().lstrip(".")
        save_format = {
            "jpg": "JPEG",
            "jpeg": "JPEG",
            "png": "PNG",
            "bmp": "BMP",
            "gif": "GIF",
            "tif": "TIFF",
            "tiff": "TIFF",
            "webp": "WEBP",
        }.get(ext)

        if save_format is None:
            save_format = (img.format or "PNG").upper()

        if save_format == "JPEG" and warm.mode in ("RGBA", "LA"):
            warm = warm.convert("RGB")

        out = io.BytesIO()
        save_kwargs = {}
        if save_format == "JPEG":
            save_kwargs["quality"] = 90
        warm.save(out, format=save_format, **save_kwargs)
        return out.getvalue()
    except Exception as e:
        print(f"  ! 图片反色失败 ({fmt_hint}): {e}", flush=True)
        return None


def invert_docx_images(doc, theme: dict) -> int:
    """遍历 docx 中所有 image part，做温柔反色。返回成功反色的图片数。"""
    seen = set()
    counter = {"n": 0}

    def visit(part):
        if id(part) in seen:
            return
        seen.add(id(part))
        for rel in list(part.rels.values()):
            if rel.is_external:
                continue
            try:
                target = rel.target_part
            except Exception:
                continue
            content_type = getattr(target, "content_type", "") or ""
            if content_type.startswith("image/"):
                ext = content_type.split("/")[-1]
                blob = target.blob
                new_blob = invert_image_blob(blob, ext, theme)
                if new_blob:
                    target._blob = new_blob
                    counter["n"] += 1
            else:
                visit(target)

    visit(doc.part)
    return counter["n"]


def process_section_part(
    part_obj, font_color: str, cell_bg: str, border_color: str
) -> None:
    """处理 header/footer。"""
    if part_obj is None:
        return
    for paragraph in getattr(part_obj, "paragraphs", []):
        process_paragraph(paragraph, font_color)
    for table in getattr(part_obj, "tables", []):
        process_table(table, font_color, cell_bg, border_color)


def convert_docx_to_darkmode(
    input_path: Path,
    output_path: Path,
    invert_images: bool = True,
    theme_name: str = DEFAULT_THEME,
) -> dict:
    theme = get_theme(theme_name)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(str(input_path), str(output_path))

    doc = Document(str(output_path))

    bg = theme["bg"]
    fg = theme["fg"]
    border = theme["border"]

    set_page_background(doc, bg)

    for paragraph in doc.paragraphs:
        process_paragraph(paragraph, fg)

    for table in doc.tables:
        process_table(table, fg, bg, border)

    for section in doc.sections:
        for hf_attr in (
            "header",
            "footer",
            "first_page_header",
            "first_page_footer",
            "even_page_header",
            "even_page_footer",
        ):
            try:
                hf = getattr(section, hf_attr)
            except Exception:
                hf = None
            process_section_part(hf, fg, bg, border)

    images_inverted = 0
    if invert_images:
        images_inverted = invert_docx_images(doc, theme)

    doc.save(str(output_path))

    return {
        "images_inverted": images_inverted,
        "theme": theme_name,
        "size_in": input_path.stat().st_size,
        "size_out": output_path.stat().st_size,
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="DOCX 护眼模式转换器")
    parser.add_argument("input", help="输入 .docx 路径")
    parser.add_argument("output", nargs="?", help="输出路径（默认 xxx_dark.docx）")
    parser.add_argument("--no-images", action="store_true", help="不反色内嵌图片")
    parser.add_argument(
        "--theme",
        default=DEFAULT_THEME,
        choices=list(THEMES.keys()),
        help=f"护眼主题（默认 {DEFAULT_THEME}）",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv if argv is not None else sys.argv[1:])
    input_path = Path(args.input).expanduser().resolve()
    if not input_path.exists():
        print(f"❌ 输入文件不存在: {input_path}", file=sys.stderr)
        return 2

    if args.output:
        output_path = Path(args.output).expanduser().resolve()
    else:
        output_path = input_path.with_name(f"{input_path.stem}_dark.docx")

    theme = get_theme(args.theme)
    print(f"▶ DOCX 护眼模式转换")
    print(f"  输入: {input_path}")
    print(f"  输出: {output_path}")
    print(f"  反色内嵌图片: {'否' if args.no_images else '是'}")
    print(f"  主题: {args.theme} ({theme['name']}) bg=#{theme['bg']} fg=#{theme['fg']}")

    info = convert_docx_to_darkmode(
        input_path,
        output_path,
        invert_images=not args.no_images,
        theme_name=args.theme,
    )
    print(
        f"✅ 完成 · 反色图片 {info['images_inverted']} 张 · "
        f"{info['size_in'] / 1024 / 1024:.2f} MB → {info['size_out'] / 1024 / 1024:.2f} MB"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
