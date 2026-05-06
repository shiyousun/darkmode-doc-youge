#!/usr/bin/env python3
"""
darkmode_image.py — 把单张图片（jpg/png/jpeg/bmp/gif/tiff/webp）转成护眼模式

适用场景：
- 拍照作业 / 拍照试卷 / 截图笔记，纸质白底刺眼
- 教辅资料截图、网页截图，长时间阅读伤眼

处理逻辑：温柔反色（gentle_invert） — 反色后整体压到主题暖色，
原图白底 → 主题暖深灰，原图黑字 → 主题暖米杏，色调统一不刺眼。

用法：
    python3 darkmode_image.py input.jpg [output.jpg] [--theme warm]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from PIL import Image

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from themes import DEFAULT_THEME, THEMES, gentle_invert, get_theme

SUPPORTED_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".tiff", ".tif", ".webp"}


def _save_format(ext: str) -> str:
    ext = ext.lower().lstrip(".")
    return {
        "jpg": "JPEG",
        "jpeg": "JPEG",
        "png": "PNG",
        "bmp": "BMP",
        "gif": "GIF",
        "tif": "TIFF",
        "tiff": "TIFF",
        "webp": "WEBP",
    }.get(ext, "PNG")


def convert_image_to_darkmode(
    input_path: Path,
    output_path: Path,
    theme_name: str = DEFAULT_THEME,
) -> dict:
    theme = get_theme(theme_name)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with Image.open(input_path) as img:
        # 处理 EXIF 旋转（手机拍的图常有方向元数据）
        try:
            from PIL import ImageOps as _IO
            img = _IO.exif_transpose(img)
        except Exception:
            pass

        warm = gentle_invert(img, theme)

        save_format = _save_format(output_path.suffix)
        save_kwargs: dict = {}
        if save_format == "JPEG":
            if warm.mode in ("RGBA", "LA"):
                warm = warm.convert("RGB")
            save_kwargs["quality"] = 92
            save_kwargs["optimize"] = True
        elif save_format == "PNG":
            save_kwargs["optimize"] = True
        elif save_format == "WEBP":
            save_kwargs["quality"] = 92

        warm.save(output_path, format=save_format, **save_kwargs)

    return {
        "theme": theme_name,
        "size_in": input_path.stat().st_size,
        "size_out": output_path.stat().st_size,
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="单图护眼模式转换器")
    parser.add_argument("input", help="输入图片路径")
    parser.add_argument("output", nargs="?", help="输出路径（默认 xxx_dark.<原扩展名>）")
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

    if input_path.suffix.lower() not in SUPPORTED_EXTS:
        print(
            f"❌ 不支持的图片格式: {input_path.suffix}（支持 {sorted(SUPPORTED_EXTS)}）",
            file=sys.stderr,
        )
        return 2

    if args.output:
        output_path = Path(args.output).expanduser().resolve()
    else:
        output_path = input_path.with_name(f"{input_path.stem}_dark{input_path.suffix}")

    theme = get_theme(args.theme)
    print(f"▶ 单图护眼模式转换")
    print(f"  输入: {input_path}")
    print(f"  输出: {output_path}")
    print(f"  主题: {args.theme} ({theme['name']}) bg=#{theme['bg']} fg=#{theme['fg']}")

    info = convert_image_to_darkmode(input_path, output_path, theme_name=args.theme)
    print(
        f"✅ 完成 · {info['size_in'] / 1024:.1f} KB → {info['size_out'] / 1024:.1f} KB"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
