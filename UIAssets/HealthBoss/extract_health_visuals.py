from pathlib import Path
from statistics import median

from PIL import Image
from psd_tools import PSDImage


PSD_PATH = Path(r"C:\Users\ppark\Downloads\Nile Pixel art UI\Nile Pixel art UI.psd")
OUTPUT_DIR = Path(__file__).resolve().parent


def median_color(colors, fallback):
    if not colors:
        return fallback
    return tuple(int(median(channel)) for channel in zip(*colors))


def row_styled_image(rendered, raw_alpha, sample_range, predicate, fallback):
    rendered = rendered.convert("RGBA")
    raw_alpha = raw_alpha.convert("RGBA")
    output = Image.new("RGBA", rendered.size)
    source = rendered.load()
    alpha_source = raw_alpha.load()
    target = output.load()
    width, height = rendered.size
    start, stop = sample_range

    for y in range(height):
        color = median_color(
            [source[x, y][:3] for x in range(start, min(stop, width)) if predicate(source[x, y][:3])],
            fallback,
        )
        for x in range(width):
            target[x, y] = (*color, alpha_source[x, y][3])
    return output


def frame_from_merged(merged, group, frame_layer):
    rendered = merged.crop(group.bbox).convert("RGBA")
    raw = frame_layer.composite().convert("RGBA")
    output = Image.new("RGBA", rendered.size)
    source = rendered.load()
    mask = raw.load()
    target = output.load()

    for y in range(output.height):
        for x in range(output.width):
            target[x, y] = (*source[x, y][:3], mask[x, y][3])
    return output


def x_components(alpha_image):
    alpha = alpha_image.convert("RGBA")
    occupied = [
        any(alpha.getpixel((x, y))[3] > 0 for y in range(alpha.height))
        for x in range(alpha.width)
    ]
    components = []
    start = None
    for x, present in enumerate(occupied + [False]):
        if present and start is None:
            start = x
        elif not present and start is not None:
            components.append((start, x))
            start = None
    return components


def repeat_star_style(rendered, alpha_mask, source_component):
    rendered = rendered.convert("RGBA")
    alpha_mask = alpha_mask.convert("RGBA")
    components = x_components(alpha_mask)
    output = Image.new("RGBA", rendered.size)
    source = rendered.load()
    mask = alpha_mask.load()
    target = output.load()
    source_left, source_right = components[source_component]
    source_width = source_right - source_left

    for target_left, target_right in components:
        target_width = target_right - target_left
        for x in range(target_left, target_right):
            fraction = 0 if target_width <= 1 else (x - target_left) / (target_width - 1)
            source_x = source_left + min(source_width - 1, round(fraction * (source_width - 1)))
            for y in range(rendered.height):
                alpha = mask[x, y][3]
                if alpha > 0:
                    target[x, y] = (*source[source_x, y][:3], alpha)
    return output


def main():
    psd = PSDImage.open(PSD_PATH)
    merged = psd.topil().convert("RGBA")
    root = next(layer for layer in psd if layer.name == "Heatlh/Boss")

    health = next(layer for layer in root if layer.name == "Health")
    health_bg_layer = next(layer for layer in health if layer.name == "Bg")
    health_bar_group = next(layer for layer in health if layer.name == "HealthBar")
    health_bar_layer = next(layer for layer in health_bar_group if layer.name == "HealthBar")
    health_frame_group = next(layer for layer in health if layer.name == "Frame")

    health_bg_rendered = merged.crop(health_bg_layer.bbox)
    health_bg_raw = health_bg_layer.composite()
    health_bg = row_styled_image(
        health_bg_rendered,
        health_bg_raw,
        (420, 515),
        lambda c: c[0] > c[1] * 1.18 and c[0] > c[2] * 1.45,
        (73, 46, 31),
    )
    health_bg.save(OUTPUT_DIR / "health_bg_exact.png")

    health_fill = row_styled_image(
        merged.crop(health_bar_layer.bbox),
        health_bar_layer.composite(),
        (0, 280),
        lambda c: c[1] > c[0] * 1.25 and c[1] > c[2] * 1.25,
        (53, 162, 54),
    )
    health_fill_pixels = health_fill.load()
    for y in range(health_fill.height):
        for x in range(8, health_fill.width):
            red, green, blue, _ = health_fill_pixels[x, y]
            health_fill_pixels[x, y] = (red, green, blue, 255)
    health_fill.save(OUTPUT_DIR / "health_fill_exact.png")

    health_frame = frame_from_merged(merged, health, health_frame_group)
    health_frame.save(OUTPUT_DIR / "health_frame_exact.png")

    boss = next(layer for layer in root if layer.name == "Boss")
    boss_bg_layer = next(layer for layer in boss if layer.name == "Bg")
    boss_bar_layer = next(layer for layer in boss if layer.name == "BossBar")
    boss_frame_group = next(layer for layer in boss if layer.name == "Frame")

    boss_bg_raw = boss_bg_layer.composite().convert("RGBA")
    boss_bg = Image.new("RGBA", boss_bg_raw.size)
    for y in range(boss_bg.height):
        source_y = min(health_bg.height - 1, round((y + 0.5) * health_bg.height / boss_bg.height - 0.5))
        for x in range(boss_bg.width):
            source_x = min(health_bg.width - 1, round(x * (health_bg.width - 1) / max(1, boss_bg.width - 1)))
            red, green, blue, _ = health_bg.getpixel((source_x, source_y))
            boss_bg.putpixel((x, y), (red, green, blue, boss_bg_raw.getpixel((x, y))[3]))
    boss_bg.save(OUTPUT_DIR / "boss_bg_exact.png")

    boss_fill = row_styled_image(
        merged.crop(boss_bar_layer.bbox),
        boss_bar_layer.composite(),
        (55, 500),
        lambda c: c[0] > 80 and c[0] > c[1] * 1.45 and c[0] > c[2] * 1.15,
        (177, 52, 72),
    )
    boss_fill.save(OUTPUT_DIR / "boss_fill_exact.png")

    boss_frame = frame_from_merged(merged, boss, boss_frame_group)
    boss_frame.save(OUTPUT_DIR / "boss_frame_exact.png")

    mana = next(layer for layer in root if layer.name == "Mana")
    mana_bg_layer = next(layer for layer in mana if layer.name == "Bg")
    mana_bar_layer = next(layer for layer in mana if layer.name == "Bar")
    mana_rendered = merged.crop(mana_bg_layer.bbox)
    mana_mask = mana_bg_layer.composite()

    mana_bg = repeat_star_style(mana_rendered, mana_mask, -2)
    mana_bg.save(OUTPUT_DIR / "mana_bg_exact.png")

    mana_fill = repeat_star_style(mana_rendered, mana_mask, 2)
    mana_fill.save(OUTPUT_DIR / "mana_fill_exact.png")

    for filename, image in (
        ("health_bg_exact.png", health_bg),
        ("health_fill_exact.png", health_fill),
        ("health_frame_exact.png", health_frame),
        ("boss_bg_exact.png", boss_bg),
        ("boss_fill_exact.png", boss_fill),
        ("boss_frame_exact.png", boss_frame),
        ("mana_bg_exact.png", mana_bg),
        ("mana_fill_exact.png", mana_fill),
    ):
        print(filename, image.size)


if __name__ == "__main__":
    main()
