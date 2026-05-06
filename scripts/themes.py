#!/usr/bin/env python3
"""
themes.py — 护眼主题配色 + 温柔反色函数

科学依据：
- 纯白 #FFFFFF 配纯黑 #000000 对比度 21:1，是公认最伤眼的组合
- WCAG AAA 推荐对比度 ≥ 7:1 即可，无需拉满
- Apple Dark Mode / VS Code / Kindle 暗色阅读 全部不用纯白纯黑
- 暖色系（偏黄红）降低蓝光刺激，长时间阅读最舒适

主题配色：
| 主题   | 背景       | 文字       | 对比度 | 适用                        |
|--------|------------|------------|--------|------------------------------|
| warm   | #1F1F1F    | #D4C9A8    | ~11:1  | 类 Kindle Paperwhite Dark   |
| paper  | #1B1A17    | #D8C9A0    | ~12:1  | 仿羊皮纸 sepia 暗色          |
| gray   | #262626    | #D4D4D4    | ~12:1  | 偏冷淡的护眼方案             |
| pure   | #000000    | #FFFFFF    | 21:1   | 旧版纯黑白（兼容）           |
"""
from __future__ import annotations

from PIL import Image, ImageOps


THEMES = {
    "warm": {
        "name": "暖杏色（推荐）",
        "bg": "1F1F1F",
        "fg": "D4C9A8",
        "border": "5A5142",
        "bg_rgb": (31, 31, 31),
        "fg_rgb": (212, 201, 168),
    },
    "paper": {
        "name": "仿羊皮纸 sepia",
        "bg": "1B1A17",
        "fg": "D8C9A0",
        "border": "5A5142",
        "bg_rgb": (27, 26, 23),
        "fg_rgb": (216, 201, 160),
    },
    "gray": {
        "name": "暖灰",
        "bg": "262626",
        "fg": "D4D4D4",
        "border": "555555",
        "bg_rgb": (38, 38, 38),
        "fg_rgb": (212, 212, 212),
    },
    "pure": {
        "name": "纯黑白（旧版）",
        "bg": "000000",
        "fg": "FFFFFF",
        "border": "FFFFFF",
        "bg_rgb": (0, 0, 0),
        "fg_rgb": (255, 255, 255),
    },
}

DEFAULT_THEME = "warm"


def get_theme(name: str | None) -> dict:
    if not name:
        name = DEFAULT_THEME
    name = name.lower().strip()
    if name not in THEMES:
        raise ValueError(
            f"未知主题: {name}, 可选: {list(THEMES.keys())}"
        )
    return THEMES[name]


def make_warm_lut(bg_rgb: tuple[int, int, int], fg_rgb: tuple[int, int, int]) -> list[int]:
    """
    生成 R/G/B 三通道 LUT，把反色后的图像值线性映射到 [bg_rgb, fg_rgb] 区间。

    映射逻辑：
        反色后值 0   (原图最亮 / 通常是白底) → 输出 bg_rgb（深背景色）
        反色后值 255 (原图最暗 / 通常是黑文字) → 输出 fg_rgb（暖前景色）
        中间值线性插值

    这样原图白底变成暖深灰，黑字变成暖米色，整张图的色调与文档背景/文字一致。
    """
    bg_r, bg_g, bg_b = bg_rgb
    fg_r, fg_g, fg_b = fg_rgb
    r_lut = [bg_r + (fg_r - bg_r) * i // 255 for i in range(256)]
    g_lut = [bg_g + (fg_g - bg_g) * i // 255 for i in range(256)]
    b_lut = [bg_b + (fg_b - bg_b) * i // 255 for i in range(256)]
    return r_lut + g_lut + b_lut


def gentle_invert(img: Image.Image, theme: dict) -> Image.Image:
    """
    温柔反色：先做 RGB 反色，再用主题色 LUT 重新映射到护眼色域。
    保留 alpha 通道。

    输入：任意 PIL.Image
    输出：经过温柔反色 + 主题色映射的图像
    """
    bg_rgb = theme["bg_rgb"]
    fg_rgb = theme["fg_rgb"]
    lut = make_warm_lut(bg_rgb, fg_rgb)

    original_mode = img.mode

    if original_mode == "RGBA":
        r, g, b, a = img.split()
        rgb = Image.merge("RGB", (r, g, b))
        inv = ImageOps.invert(rgb)
        warm = inv.point(lut)
        r2, g2, b2 = warm.split()
        return Image.merge("RGBA", (r2, g2, b2, a))

    if original_mode == "LA":
        l, a = img.split()
        inv = ImageOps.invert(l)
        warm = inv.convert("RGB").point(lut)
        # 转回灰度（用绿通道近似）
        r2, g2, b2 = warm.split()
        return Image.merge("LA", (g2, a))

    if original_mode == "P":
        converted = img.convert("RGBA")
        return gentle_invert(converted, theme)

    if original_mode == "1":
        return gentle_invert(img.convert("L"), theme)

    if original_mode == "L":
        inv = ImageOps.invert(img)
        warm = inv.convert("RGB").point(lut)
        return warm

    if original_mode == "CMYK":
        return gentle_invert(img.convert("RGB"), theme)

    rgb = img.convert("RGB")
    inv = ImageOps.invert(rgb)
    return inv.point(lut)
