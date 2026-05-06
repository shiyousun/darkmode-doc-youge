#!/usr/bin/env python3
"""
darkmode_pdf.py — 把 PDF 转成护眼模式（温柔反色，兼容扫描件/复杂排版）

用法：
    python3 darkmode_pdf.py input.pdf [output.pdf] [--dpi 200] [--theme warm]

主题（--theme）：
    warm  暖杏色（默认推荐，类 Kindle Paperwhite Dark）
    paper 仿羊皮纸 sepia 暗色
    gray  暖灰色
    pure  纯黑底白字（旧版兼容）
"""
from __future__ import annotations

import argparse
import io
import sys
from pathlib import Path

import fitz  # PyMuPDF
from PIL import Image

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from themes import DEFAULT_THEME, THEMES, gentle_invert, get_theme


def convert_pdf_to_darkmode(
    input_path: Path,
    output_path: Path,
    dpi: int = 200,
    theme_name: str = DEFAULT_THEME,
) -> dict:
    theme = get_theme(theme_name)
    src = fitz.open(str(input_path))
    dst = fitz.open()

    page_count = len(src)
    scale = dpi / 72.0
    matrix = fitz.Matrix(scale, scale)

    for i in range(page_count):
        page = src[i]
        pix = page.get_pixmap(matrix=matrix, alpha=False)
        png_bytes = pix.tobytes("png")
        img = Image.open(io.BytesIO(png_bytes))
        warm = gentle_invert(img, theme)

        buf = io.BytesIO()
        warm.save(buf, format="PNG", optimize=True)
        buf.seek(0)

        new_page = dst.new_page(width=page.rect.width, height=page.rect.height)
        new_page.insert_image(page.rect, stream=buf.getvalue())

        if (i + 1) % 5 == 0 or i + 1 == page_count:
            print(f"  · 已处理 {i + 1}/{page_count} 页", flush=True)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    dst.save(str(output_path), garbage=4, deflate=True)
    dst.close()
    src.close()

    return {
        "pages": page_count,
        "theme": theme_name,
        "size_in": input_path.stat().st_size,
        "size_out": output_path.stat().st_size,
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="PDF 护眼模式转换器")
    parser.add_argument("input", help="输入 PDF 路径")
    parser.add_argument("output", nargs="?", help="输出 PDF 路径（默认 xxx_dark.pdf）")
    parser.add_argument("--dpi", type=int, default=200, help="渲染分辨率（默认 200）")
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
        output_path = input_path.with_name(f"{input_path.stem}_dark.pdf")

    theme = get_theme(args.theme)
    print(f"▶ PDF 护眼模式转换")
    print(f"  输入: {input_path}")
    print(f"  输出: {output_path}")
    print(f"  DPI : {args.dpi}")
    print(f"  主题: {args.theme} ({theme['name']}) bg=#{theme['bg']} fg=#{theme['fg']}")

    info = convert_pdf_to_darkmode(input_path, output_path, dpi=args.dpi, theme_name=args.theme)
    print(
        f"✅ 完成 · {info['pages']} 页 · "
        f"{info['size_in'] / 1024 / 1024:.2f} MB → {info['size_out'] / 1024 / 1024:.2f} MB"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
