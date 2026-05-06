#!/usr/bin/env python3
"""
darkmode_batch.py — 批量把目录下所有 Word/PDF/Excel 文件转成护眼模式

用法：
    python3 darkmode_batch.py /path/to/dir
    python3 darkmode_batch.py /path/to/dir --theme paper
    python3 darkmode_batch.py /path/to/dir --no-recursive --no-images --dpi 300
    python3 darkmode_batch.py /path/to/dir --out /custom/output

主题（--theme）：
    warm  暖杏色（默认推荐，类 Kindle Paperwhite Dark）
    paper 仿羊皮纸 sepia 暗色
    gray  暖灰色
    pure  纯黑底白字（旧版兼容）
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from darkmode_pdf import convert_pdf_to_darkmode
from darkmode_docx import convert_docx_to_darkmode
from darkmode_xlsx import convert_xlsx_to_darkmode
from darkmode_image import convert_image_to_darkmode
from themes import DEFAULT_THEME, THEMES, get_theme

DOC_EXTS = {".pdf", ".docx", ".doc", ".xlsx"}
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".tiff", ".tif", ".webp"}
SUPPORTED_EXTS = DOC_EXTS | IMAGE_EXTS


def is_temp_lock(name: str) -> bool:
    return name.startswith("~$") or name.startswith(".~")


def should_skip(path: Path) -> bool:
    if is_temp_lock(path.name):
        return True
    if path.stem.endswith("_dark"):
        return True
    if "/dark/" in str(path).replace("\\", "/"):
        return True
    return False


def find_files(root: Path, recursive: bool = True) -> list[Path]:
    iterator = root.rglob("*") if recursive else root.glob("*")
    results: list[Path] = []
    for path in iterator:
        if not path.is_file():
            continue
        if path.suffix.lower() not in SUPPORTED_EXTS:
            continue
        if should_skip(path):
            continue
        results.append(path)
    results.sort()
    return results


def find_soffice() -> str | None:
    for cand in (
        "soffice",
        "/Applications/LibreOffice.app/Contents/MacOS/soffice",
        "/usr/local/bin/soffice",
        "/opt/homebrew/bin/soffice",
    ):
        if cand.startswith("/"):
            if Path(cand).exists():
                return cand
        else:
            found = shutil.which(cand)
            if found:
                return found
    return None


def doc_to_docx(input_path: Path) -> Path | None:
    soffice = find_soffice()
    if not soffice:
        return None
    tmpdir = Path(tempfile.mkdtemp(prefix="darkmode_doc_"))
    try:
        result = subprocess.run(
            [
                soffice,
                "--headless",
                "--convert-to",
                "docx",
                "--outdir",
                str(tmpdir),
                str(input_path),
            ],
            capture_output=True,
            timeout=180,
        )
        if result.returncode != 0:
            return None
        out = tmpdir / (input_path.stem + ".docx")
        if out.exists():
            return out
    except Exception:
        return None
    return None


def process_one(
    src: Path,
    out_dir: Path,
    invert_images: bool,
    pdf_dpi: int,
    theme_name: str,
) -> tuple[bool, str, dict | None]:
    out_dir.mkdir(parents=True, exist_ok=True)
    suffix = src.suffix.lower()
    info: dict | None = None

    try:
        if suffix == ".pdf":
            output = out_dir / f"{src.stem}_dark.pdf"
            info = convert_pdf_to_darkmode(src, output, dpi=pdf_dpi, theme_name=theme_name)
            return True, str(output), info
        if suffix == ".docx":
            output = out_dir / f"{src.stem}_dark.docx"
            info = convert_docx_to_darkmode(
                src, output, invert_images=invert_images, theme_name=theme_name
            )
            return True, str(output), info
        if suffix == ".xlsx":
            output = out_dir / f"{src.stem}_dark.xlsx"
            info = convert_xlsx_to_darkmode(src, output, theme_name=theme_name)
            return True, str(output), info
        if suffix in IMAGE_EXTS:
            output = out_dir / f"{src.stem}_dark{src.suffix}"
            info = convert_image_to_darkmode(src, output, theme_name=theme_name)
            return True, str(output), info
        if suffix == ".doc":
            converted = doc_to_docx(src)
            if not converted:
                return False, "缺少 LibreOffice (soffice)，无法处理 .doc", None
            output = out_dir / f"{src.stem}_dark.docx"
            info = convert_docx_to_darkmode(
                converted, output, invert_images=invert_images, theme_name=theme_name
            )
            try:
                shutil.rmtree(converted.parent, ignore_errors=True)
            except Exception:
                pass
            return True, str(output), info
        return False, f"不支持的格式: {suffix}", None
    except Exception as e:
        return False, f"{type(e).__name__}: {e}", None


def fmt_size(n: int) -> str:
    if n < 1024:
        return f"{n} B"
    if n < 1024 * 1024:
        return f"{n / 1024:.1f} KB"
    return f"{n / 1024 / 1024:.2f} MB"


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="批量把 Word/PDF/Excel 文档转成护眼模式"
    )
    parser.add_argument("root", help="要处理的根目录")
    parser.add_argument(
        "--no-recursive",
        action="store_true",
        help="只处理当前目录，不递归子目录",
    )
    parser.add_argument(
        "--no-images",
        action="store_true",
        help="DOCX 不反色内嵌图片",
    )
    parser.add_argument(
        "--dpi",
        type=int,
        default=200,
        help="PDF 渲染分辨率（默认 200）",
    )
    parser.add_argument(
        "--out",
        default=None,
        help="自定义输出目录（默认在源目录下建 dark/ 子目录）",
    )
    parser.add_argument(
        "--theme",
        default=DEFAULT_THEME,
        choices=list(THEMES.keys()),
        help=f"护眼主题（默认 {DEFAULT_THEME}）",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv if argv is not None else sys.argv[1:])

    root = Path(args.root).expanduser().resolve()
    if not root.exists() or not root.is_dir():
        print(f"❌ 目录不存在: {root}", file=sys.stderr)
        return 2

    out_root = (
        Path(args.out).expanduser().resolve() if args.out else (root / "dark")
    )

    files = find_files(root, recursive=not args.no_recursive)
    theme = get_theme(args.theme)

    print("=" * 70)
    print(f"📂 源目录: {root}")
    print(f"📂 输出目录: {out_root}")
    print(f"🎨 护眼主题: {args.theme} ({theme['name']}) bg=#{theme['bg']} fg=#{theme['fg']}")
    print(f"🔍 递归: {'否' if args.no_recursive else '是'}")
    print(f"🖼  反色 DOCX 图片: {'否' if args.no_images else '是'}")
    print(f"📐 PDF 渲染 DPI: {args.dpi}")
    print(f"📄 待处理文件: {len(files)}")
    print("=" * 70)

    if not files:
        print("⚠️  没有找到可处理的文件 (.pdf / .docx / .doc / .xlsx / .jpg / .png 等)")
        return 0

    succeeded: list[tuple[Path, str, dict]] = []
    failed: list[tuple[Path, str]] = []

    t0 = time.time()
    for idx, src in enumerate(files, 1):
        rel = src.relative_to(root)
        print(f"\n[{idx}/{len(files)}] {rel}")

        sub_dir = out_root / rel.parent
        ok, msg, info = process_one(
            src, sub_dir, not args.no_images, args.dpi, args.theme
        )
        if ok:
            succeeded.append((src, msg, info or {}))
            extra = ""
            if info:
                if "pages" in info:
                    extra = f" · {info['pages']} 页"
                elif "images_inverted" in info:
                    extra = f" · 反色图片 {info['images_inverted']} 张"
                elif "sheets" in info:
                    extra = f" · {info['sheets']} 工作表"
                elif src.suffix.lower() in IMAGE_EXTS:
                    extra = " · 单图护眼"
                size_in = info.get("size_in", 0)
                size_out = info.get("size_out", 0)
                if size_in and size_out:
                    extra += f" · {fmt_size(size_in)} → {fmt_size(size_out)}"
            print(f"   ✅ {Path(msg).name}{extra}")
        else:
            failed.append((src, msg))
            print(f"   ❌ {msg}")

    elapsed = time.time() - t0

    print("\n" + "=" * 70)
    print(f"📊 汇总 (耗时 {elapsed:.1f}s)")
    print(f"   ✅ 成功: {len(succeeded)}")
    print(f"   ❌ 失败: {len(failed)}")
    if failed:
        print("\n❌ 失败列表:")
        for src, msg in failed:
            print(f"   · {src.relative_to(root)}: {msg}")
    print("=" * 70)
    print(f"📂 输出目录: {out_root}")

    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
