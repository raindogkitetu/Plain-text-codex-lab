#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone, timedelta
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter


ROOT = Path(__file__).resolve().parents[1]
PRODUCT_DIR = ROOT / "assets" / "villain_shop" / "product_images"
OUT_DIR = ROOT / "villain_post_images" / "wearable_stock"
DATA_PATH = ROOT / "data" / "villain_shop_wearable_stock.json"
REPORT_PATH = ROOT / "reports" / "villain_shop_wearable_stock.md"
JST = timezone(timedelta(hours=9))


def now_jst() -> str:
    return datetime.now(JST).replace(microsecond=0).isoformat()


def load_rgba(path: Path) -> Image.Image:
    return Image.open(path).convert("RGBA")


def cover_resize(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    width, height = image.size
    target_w, target_h = size
    scale = max(target_w / width, target_h / height)
    resized = image.resize((int(width * scale), int(height * scale)), Image.Resampling.LANCZOS)
    left = (resized.width - target_w) // 2
    top = (resized.height - target_h) // 2
    return resized.crop((left, top, left + target_w, top + target_h))


def product_cutout(path: Path, max_size: tuple[int, int]) -> Image.Image:
    image = load_rgba(path)
    if image.mode == "RGBA":
        alpha = image.getchannel("A")
        bbox = alpha.getbbox()
        if bbox:
            image = image.crop(bbox)
    image.thumbnail(max_size, Image.Resampling.LANCZOS)
    return image


def draw_noise(base: Image.Image, opacity: int = 18) -> None:
    noise = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(noise)
    for x in range(0, base.width, 11):
        for y in range((x * 7) % 13, base.height, 17):
            shade = 255 if (x + y) % 3 == 0 else 0
            draw.point((x, y), fill=(shade, shade, shade, opacity))
    base.alpha_composite(noise)


def paste_shadow(canvas: Image.Image, subject: Image.Image, xy: tuple[int, int], blur: int = 18) -> None:
    shadow = Image.new("RGBA", subject.size, (0, 0, 0, 0))
    alpha = subject.getchannel("A")
    shadow.putalpha(alpha)
    shadow = Image.new("RGBA", subject.size, (0, 0, 0, 125)).copy()
    shadow.putalpha(alpha.filter(ImageFilter.GaussianBlur(blur)))
    canvas.alpha_composite(shadow, (xy[0] + 10, xy[1] + 14))


def cap_late_night() -> dict:
    canvas = Image.new("RGBA", (1080, 1350), (20, 22, 24, 255))
    draw = ImageDraw.Draw(canvas)
    for y in range(canvas.height):
        tint = int(38 + y * 0.025)
        draw.line((0, y, canvas.width, y), fill=(tint, tint + 2, tint + 3, 255))
    draw.rectangle((0, 1020, 1080, 1350), fill=(32, 32, 30, 255))
    draw.ellipse((370, 235, 710, 575), fill=(42, 38, 34, 255))
    draw.rounded_rectangle((250, 565, 830, 1160), radius=80, fill=(18, 18, 17, 255))
    draw.polygon([(315, 1160), (765, 1160), (910, 1350), (170, 1350)], fill=(13, 13, 12, 255))

    cap = product_cutout(PRODUCT_DIR / "32_cap.png", (490, 265))
    cap = cap.rotate(-5, resample=Image.Resampling.BICUBIC, expand=True)
    paste_shadow(canvas, cap, (285, 250), blur=10)
    canvas.alpha_composite(cap, (285, 250))

    draw.rounded_rectangle((83, 1120, 345, 1165), radius=18, fill=(245, 244, 236, 32))
    draw.line((86, 1218, 408, 1218), fill=(238, 238, 226, 90), width=2)
    draw_noise(canvas)
    out = OUT_DIR / "wearable_stock_001_cap_afterhours.png"
    canvas.convert("RGB").save(out, quality=95)
    return {
        "id": "wearable_stock_001_cap_afterhours",
        "path": str(out.relative_to(ROOT)),
        "absolute_path": str(out),
        "source_products": ["32_cap.png"],
        "image_type": "wearable_poster",
        "prompt_family": "shop_wearable_cap_afterhours",
        "fit_notes": "Actual shop cap composited onto a quiet human silhouette. No invented cap shape.",
        "recommended_text_angle": "小物が空気を先に運ぶ / 服より軽いのに残る",
    }


def bucket_hat_street() -> dict:
    canvas = Image.new("RGBA", (1080, 1350), (236, 234, 226, 255))
    draw = ImageDraw.Draw(canvas)
    draw.rectangle((0, 0, 1080, 1350), fill=(221, 219, 209, 255))
    draw.rectangle((0, 720, 1080, 1350), fill=(188, 188, 178, 255))
    draw.line((0, 717, 1080, 690), fill=(120, 122, 118, 255), width=4)
    draw.ellipse((360, 280, 720, 640), fill=(64, 55, 48, 255))
    draw.rounded_rectangle((250, 618, 830, 1240), radius=72, fill=(24, 24, 23, 255))
    draw.rectangle((412, 585, 668, 720), fill=(55, 49, 43, 255))
    draw.polygon([(250, 1240), (830, 1240), (970, 1350), (110, 1350)], fill=(20, 20, 19, 255))

    hat = product_cutout(PRODUCT_DIR / "31_bucket_hat.png", (500, 305))
    paste_shadow(canvas, hat, (290, 275), blur=9)
    canvas.alpha_composite(hat, (290, 275))

    draw.rounded_rectangle((770, 970, 1005, 1030), radius=14, fill=(255, 255, 255, 35))
    draw.rectangle((806, 1060, 980, 1068), fill=(255, 255, 255, 65))
    draw_noise(canvas, opacity=12)
    out = OUT_DIR / "wearable_stock_002_bucket_street.png"
    canvas.convert("RGB").save(out, quality=95)
    return {
        "id": "wearable_stock_002_bucket_street",
        "path": str(out.relative_to(ROOT)),
        "absolute_path": str(out),
        "source_products": ["31_bucket_hat.png"],
        "image_type": "wearable_poster",
        "prompt_family": "shop_wearable_bucket_street",
        "fit_notes": "Actual shop bucket hat composited onto a street silhouette.",
        "recommended_text_angle": "置いてある時より、人が着た後の方が強い",
    }


def bag_workdesk() -> dict:
    canvas = Image.new("RGBA", (1080, 1350), (34, 35, 33, 255))
    draw = ImageDraw.Draw(canvas)
    draw.rectangle((0, 0, 1080, 760), fill=(48, 48, 45, 255))
    draw.polygon([(0, 790), (1080, 700), (1080, 1350), (0, 1350)], fill=(78, 72, 63, 255))
    draw.rounded_rectangle((130, 585, 960, 1215), radius=26, fill=(96, 88, 77, 255))
    draw.rounded_rectangle((165, 640, 475, 1040), radius=24, fill=(26, 25, 23, 255))
    draw.rounded_rectangle((610, 705, 900, 760), radius=14, fill=(228, 222, 205, 70))
    draw.rounded_rectangle((625, 805, 855, 850), radius=12, fill=(0, 0, 0, 85))
    draw.ellipse((720, 895, 830, 940), fill=(40, 35, 30, 255))

    bag = cover_resize(Image.open(PRODUCT_DIR / "29_haul_bag.jpg").convert("RGBA"), (440, 300))
    bag = bag.rotate(-8, resample=Image.Resampling.BICUBIC, expand=True)
    paste_shadow(canvas, bag, (305, 555), blur=18)
    canvas.alpha_composite(bag, (305, 555))

    draw.line((210, 1110, 890, 1082), fill=(235, 230, 214, 54), width=3)
    draw_noise(canvas, opacity=15)
    out = OUT_DIR / "wearable_stock_003_bag_workdesk.png"
    canvas.convert("RGB").save(out, quality=95)
    return {
        "id": "wearable_stock_003_bag_workdesk",
        "path": str(out.relative_to(ROOT)),
        "absolute_path": str(out),
        "source_products": ["29_haul_bag.jpg"],
        "image_type": "lifestyle_residue",
        "prompt_family": "shop_goods_bag_workdesk",
        "fit_notes": "Actual haul bag product image placed in a workdesk residue scene.",
        "recommended_text_angle": "持ち物が先にその人の空気を作る",
    }


def cap_mirror_crop() -> dict:
    canvas = Image.new("RGBA", (1080, 1350), (30, 31, 31, 255))
    draw = ImageDraw.Draw(canvas)
    draw.rectangle((0, 0, 1080, 1350), fill=(38, 39, 38, 255))
    draw.rounded_rectangle((120, 90, 960, 1260), radius=52, fill=(70, 70, 66, 255))
    draw.rounded_rectangle((155, 125, 925, 1225), radius=38, fill=(23, 24, 24, 255))
    draw.rectangle((155, 850, 925, 1225), fill=(16, 16, 16, 255))
    draw.ellipse((350, 295, 730, 675), fill=(48, 42, 37, 255))
    draw.rounded_rectangle((260, 625, 820, 1140), radius=84, fill=(14, 14, 14, 255))

    cap = product_cutout(PRODUCT_DIR / "32_cap.png", (560, 310))
    cap = cap.rotate(-8, resample=Image.Resampling.BICUBIC, expand=True)
    paste_shadow(canvas, cap, (248, 270), blur=12)
    canvas.alpha_composite(cap, (248, 270))

    draw.rounded_rectangle((650, 760, 815, 1110), radius=36, fill=(4, 4, 4, 255))
    draw.rounded_rectangle((684, 790, 792, 1050), radius=24, fill=(38, 38, 36, 255))
    draw.line((210, 1165, 875, 1165), fill=(235, 232, 220, 55), width=3)
    draw_noise(canvas, opacity=13)
    out = OUT_DIR / "wearable_stock_004_cap_mirror_crop.png"
    canvas.convert("RGB").save(out, quality=95)
    return {
        "id": "wearable_stock_004_cap_mirror_crop",
        "path": str(out.relative_to(ROOT)),
        "absolute_path": str(out),
        "source_products": ["32_cap.png"],
        "image_type": "wearable_lifestyle",
        "prompt_family": "shop_wearable_cap_mirror_crop",
        "fit_notes": "Actual shop cap composited into a mirror-crop silhouette. Face hidden, no invented product.",
        "recommended_text_angle": "小物の方が先に空気を運ぶ",
    }


def bucket_backview_after() -> dict:
    canvas = Image.new("RGBA", (1080, 1350), (205, 202, 191, 255))
    draw = ImageDraw.Draw(canvas)
    draw.rectangle((0, 0, 1080, 720), fill=(218, 216, 207, 255))
    draw.rectangle((0, 720, 1080, 1350), fill=(158, 157, 149, 255))
    draw.line((0, 716, 1080, 696), fill=(98, 99, 94, 255), width=4)
    draw.polygon([(170, 1350), (360, 705), (720, 705), (910, 1350)], fill=(22, 22, 21, 255))
    draw.rounded_rectangle((255, 610, 825, 1190), radius=95, fill=(13, 13, 12, 255))
    draw.rectangle((420, 535, 660, 735), fill=(61, 54, 47, 255))
    draw.ellipse((350, 250, 730, 630), fill=(58, 50, 44, 255))

    hat = product_cutout(PRODUCT_DIR / "31_bucket_hat.png", (585, 355))
    paste_shadow(canvas, hat, (245, 260), blur=13)
    canvas.alpha_composite(hat, (245, 260))

    draw.rounded_rectangle((82, 990, 280, 1042), radius=18, fill=(255, 255, 255, 42))
    draw.line((92, 1080, 410, 1070), fill=(255, 255, 255, 70), width=3)
    draw_noise(canvas, opacity=11)
    out = OUT_DIR / "wearable_stock_005_bucket_backview_after.png"
    canvas.convert("RGB").save(out, quality=95)
    return {
        "id": "wearable_stock_005_bucket_backview_after",
        "path": str(out.relative_to(ROOT)),
        "absolute_path": str(out),
        "source_products": ["31_bucket_hat.png"],
        "image_type": "wearable_lifestyle",
        "prompt_family": "shop_wearable_bucket_backview_after",
        "fit_notes": "Actual shop bucket hat used in a back-view after-scene. No temporal/event claim.",
        "recommended_text_angle": "人が着た後にだけ残る空気",
    }


def thermos_desk_residue() -> dict:
    canvas = Image.new("RGBA", (1080, 1350), (35, 34, 32, 255))
    draw = ImageDraw.Draw(canvas)
    draw.rectangle((0, 0, 1080, 770), fill=(45, 44, 41, 255))
    draw.polygon([(0, 760), (1080, 690), (1080, 1350), (0, 1350)], fill=(95, 86, 75, 255))
    draw.rounded_rectangle((125, 635, 955, 1190), radius=28, fill=(110, 99, 86, 255))
    draw.rounded_rectangle((170, 720, 475, 1045), radius=24, fill=(18, 18, 17, 255))
    draw.rounded_rectangle((610, 705, 920, 755), radius=12, fill=(245, 241, 226, 68))
    draw.rounded_rectangle((630, 805, 850, 845), radius=12, fill=(8, 8, 7, 120))

    thermos = product_cutout(PRODUCT_DIR / "33_thermos_with_villain.png", (270, 330))
    thermos = thermos.rotate(3, resample=Image.Resampling.BICUBIC, expand=True)
    paste_shadow(canvas, thermos, (540, 815), blur=16)
    canvas.alpha_composite(thermos, (540, 815))

    draw.rounded_rectangle((265, 1088, 775, 1125), radius=8, fill=(236, 230, 212, 46))
    draw.line((220, 1155, 870, 1126), fill=(235, 230, 214, 60), width=3)
    draw_noise(canvas, opacity=14)
    out = OUT_DIR / "wearable_stock_006_thermos_desk_residue.png"
    canvas.convert("RGB").save(out, quality=95)
    return {
        "id": "wearable_stock_006_thermos_desk_residue",
        "path": str(out.relative_to(ROOT)),
        "absolute_path": str(out),
        "source_products": ["33_thermos_with_villain.png"],
        "image_type": "lifestyle_residue",
        "prompt_family": "shop_goods_thermos_desk_residue",
        "fit_notes": "Actual thermos product image placed into a desk residue scene.",
        "recommended_text_angle": "グッズは使われた瞬間に文化っぽくなる",
    }


def write_report(items: list[dict]) -> None:
    DATA_PATH.write_text(
        json.dumps(
            {
                "version": "1.0",
                "updated_at_jst": now_jst(),
                "source": "official_shop_product_images",
                "source_url": "https://shop.0xmavillain.com/",
                "policy": {
                    "use_raw_shop_image_as_post": False,
                    "generated_from_actual_products": True,
                    "tracking_code_generation": "FORBIDDEN",
                    "posting_executed": "NO",
                    "upload_media_executed": "NO",
                    "create_tweet_executed": "NO",
                },
                "items": items,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    lines = [
        "# Villain Shop Wearable Stock",
        "",
        f"- updated_at_jst: `{now_jst()}`",
        "- source: official shop product images",
        "- posting_executed: `NO`",
        "- upload_media_executed: `NO`",
        "- create_tweet_executed: `NO`",
        "",
        "## Purpose",
        "",
        "ショップ画像をそのまま投稿せず、実物商品の形を保ったまま人物着用・生活痕・ポスター素材へ変換するためのローカルストック。",
        "",
        "## Items",
    ]
    for item in items:
        lines.extend(
            [
                "",
                f"### {item['id']}",
                f"- path: `{item['path']}`",
                f"- source_products: `{', '.join(item['source_products'])}`",
                f"- image_type: `{item['image_type']}`",
                f"- prompt_family: `{item['prompt_family']}`",
                f"- fit_notes: {item['fit_notes']}",
                f"- recommended_text_angle: {item['recommended_text_angle']}",
            ]
        )
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    items = [
        cap_late_night(),
        bucket_hat_street(),
        bag_workdesk(),
        cap_mirror_crop(),
        bucket_backview_after(),
        thermos_desk_residue(),
    ]
    write_report(items)
    print(json.dumps({"status": "SUCCESS", "items": len(items), "output_dir": str(OUT_DIR)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
