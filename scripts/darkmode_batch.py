#!/usr/bin/env python3
"""
darkmode_batch.py — 批量把目录下所有 Word/PDF/Excel/图片 转成护眼模式

两档模式（v2.0 新增）：
- 默认（不加任何参数）：DOCX/DOC 只改背景+文字+表格+边框，不动插图
- 加 `--invert-images`：DOCX/DOC 同时温柔反色所有内嵌图片（含 WMF 公式）

性能优化（v2.0）：
- .doc → .docx 改为按子目录分组批量调用 soffice（复用启动开销），处理大量 .doc 提速 10-20 倍
- WMF 矢量公式图（Word 老格式常见）自动用 libwmf 的 wmf2gd 工具反色（需 brew install libwmf）

用法：
    python3 darkmode_batch.py /path/to/dir
    python3 darkmode_batch.py /path/to/dir --theme paper
    python3 darkmode_batch.py /path/to/dir --invert-images --theme warm
    python3 darkmode_batch.py /path/to/dir --no-recursive --dpi 300
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
from collections import defaultdict
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from darkmode_pdf import convert_pdf_to_darkmode
from darkmode_docx import convert_docx_to_darkmode, find_wmf2gd
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


def batch_pre_convert_docs(
    doc_files: list[Path], soffice: str
) -> dict[Path, Path]:
    """
    按 parent 目录分组批量调用 soffice 把 .doc 转成 .docx，输出到临时目录。
    复用 soffice 启动开销，处理大量 .doc 提速 10-20 倍。

    返回 {原 doc 路径: 转换后 docx 临时路径}
    """
    if not doc_files:
        return {}

    groups: dict[Path, list[Path]] = defaultdict(list)
    for d in doc_files:
        groups[d.parent].append(d)

    result: dict[Path, Path] = {}
    tmproot = Path(tempfile.mkdtemp(prefix="darkmode_doc_batch_"))

    print(
        f"\n🚀 .doc 批量预转换：{len(doc_files)} 个文件分布在 {len(groups)} 个目录"
    )

    for i, (parent, docs) in enumerate(groups.items(), 1):
        out_subdir = tmproot / f"g{i:03d}"
        out_subdir.mkdir(parents=True, exist_ok=True)
        cmd = [
            soffice,
            "--headless",
            "--convert-to",
            "docx",
            "--outdir",
            str(out_subdir),
        ] + [str(d) for d in docs]
        try:
            subprocess.run(cmd, capture_output=True, timeout=900)
        except subprocess.TimeoutExpired:
            print(f"   ⚠️  [{i}/{len(groups)}] {parent} soffice 超时，跳过")
            continue

        success = 0
        for d in docs:
            out_docx = out_subdir / (d.stem + ".docx")
            if out_docx.exists():
                result[d] = out_docx
                success += 1
        print(f"   [{i}/{len(groups)}] {parent.name}/ : {success}/{len(docs)}")

    return result


def doc_to_docx(input_path: Path) -> Path | None:
    """单文件转换（兜底，正常批处理会用 batch_pre_convert_docs 提前转好）"""
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
    doc_pre_converted: dict[Path, Path] | None = None,
) -> tuple[bool, str, dict | None]:
    out_dir.mkdir(parents=True, exist_ok=True)
    suffix = src.suffix.lower()
    info: dict | None = None

    try:
        if suffix == ".pdf":
            output = out_dir / f"{src.stem}_dark.pdf"
            info = convert_pdf_to_darkmode(
                src, output, dpi=pdf_dpi, theme_name=theme_name
            )
            return True, str(output), info
        if suffix == ".docx":
            output = out_dir / f"{src.stem}_dark.docx"
            info = convert_docx_to_darkmode(
                src,
                output,
                invert_images=invert_images,
                theme_name=theme_name,
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
            converted = (
                doc_pre_converted.get(src) if doc_pre_converted else None
            )
            if converted is None or not converted.exists():
                converted = doc_to_docx(src)
            if not converted:
                return False, "缺少 LibreOffice (soffice)，无法处理 .doc", None
            output = out_dir / f"{src.stem}_dark.docx"
            info = convert_docx_to_darkmode(
                converted,
                output,
                invert_images=invert_images,
                theme_name=theme_name,
            )
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
        description="批量把 Word/PDF/Excel/图片 转成护眼模式"
    )
    parser.add_argument("root", help="要处理的根目录")
    parser.add_argument(
        "--no-recursive",
        action="store_true",
        help="只处理当前目录，不递归子目录",
    )
    parser.add_argument(
        "--invert-images",
        action="store_true",
        help="DOCX/DOC 同时温柔反色内嵌图片（含 WMF 公式）。默认不反色插图。",
    )
    parser.add_argument(
        "--no-images",
        action="store_true",
        help="（兼容旧版，与默认行为一致：不反色插图）",
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

    invert_images = bool(args.invert_images) and not bool(args.no_images)

    print("=" * 70)
    print(f"📂 源目录: {root}")
    print(f"📂 输出目录: {out_root}")
    print(
        f"🎨 护眼主题: {args.theme} ({theme['name']}) bg=#{theme['bg']} fg=#{theme['fg']}"
    )
    print(f"🔍 递归: {'否' if args.no_recursive else '是'}")
    print(f"🖼  反色 DOCX 插图: {'是' if invert_images else '否（仅改背景+文字）'}")
    if invert_images:
        wmf2gd = find_wmf2gd()
        print(
            f"   WMF 公式反色: "
            + ("是 (" + wmf2gd + ")" if wmf2gd else "否（未找到 wmf2gd，brew install libwmf 启用）")
        )
    print(f"📐 PDF 渲染 DPI: {args.dpi}")
    print(f"📄 待处理文件: {len(files)}")
    print("=" * 70)

    if not files:
        print(
            "⚠️  没有找到可处理的文件 (.pdf / .docx / .doc / .xlsx / .jpg / .png 等)"
        )
        return 0

    # 性能优化：先批量预转换所有 .doc → .docx
    doc_pre: dict[Path, Path] = {}
    doc_files = [f for f in files if f.suffix.lower() == ".doc"]
    if doc_files:
        soffice = find_soffice()
        if soffice:
            t_pre = time.time()
            doc_pre = batch_pre_convert_docs(doc_files, soffice)
            print(
                f"✅ .doc 批量预转换完成 · {len(doc_pre)}/{len(doc_files)} 成功 · "
                f"耗时 {time.time() - t_pre:.1f}s"
            )

    succeeded: list[tuple[Path, str, dict]] = []
    failed: list[tuple[Path, str]] = []

    t0 = time.time()
    for idx, src in enumerate(files, 1):
        rel = src.relative_to(root)
        print(f"\n[{idx}/{len(files)}] {rel}")

        sub_dir = out_root / rel.parent
        ok, msg, info = process_one(
            src,
            sub_dir,
            invert_images,
            args.dpi,
            args.theme,
            doc_pre_converted=doc_pre,
        )
        if ok:
            succeeded.append((src, msg, info or {}))
            extras = []
            if info:
                if "pages" in info:
                    extras.append(f"{info['pages']} 页")
                elif src.suffix.lower() in (".docx", ".doc"):
                    if info.get("images_inverted"):
                        extras.append(f"反色插图 {info['images_inverted']} 张")
                    if info.get("wmf_inverted"):
                        extras.append(f"反色 WMF {info['wmf_inverted']} 张")
                elif "sheets" in info:
                    extras.append(f"{info['sheets']} 工作表")
                elif src.suffix.lower() in IMAGE_EXTS:
                    extras.append("单图护眼")
                size_in = info.get("size_in", 0)
                size_out = info.get("size_out", 0)
                if size_in and size_out:
                    extras.append(f"{fmt_size(size_in)} → {fmt_size(size_out)}")
            extra_str = (" · " + " · ".join(extras)) if extras else ""
            print(f"   ✅ {Path(msg).name}{extra_str}")
        else:
            failed.append((src, msg))
            print(f"   ❌ {msg}")

    elapsed = time.time() - t0

    # 清理预转换的临时 .docx
    if doc_pre:
        tmp_root_candidates = {p.parent.parent for p in doc_pre.values()}
        for tr in tmp_root_candidates:
            shutil.rmtree(tr, ignore_errors=True)

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
