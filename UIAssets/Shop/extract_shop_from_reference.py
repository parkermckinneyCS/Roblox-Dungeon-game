from pathlib import Path

from PIL import Image


REFERENCE = Path(r"C:\Users\ppark\AppData\Local\Temp\codex-clipboard-ddcd690e-b862-4fe7-903d-cdb2889bc34a.png")
OUTPUT_DIR = Path(__file__).resolve().parent
OLD_BASE = OUTPUT_DIR / "shop_base_exact.png"
SHOP_CROP = (15, 9, 921, 527)


def non_background_bbox(image, tolerance=3):
    rgba = image.convert("RGBA")
    background = rgba.getpixel((0, 0))[:3]
    xs = []
    ys = []
    for y in range(rgba.height):
        for x in range(rgba.width):
            pixel = rgba.getpixel((x, y))[:3]
            if max(abs(pixel[i] - background[i]) for i in range(3)) > tolerance:
                xs.append(x)
                ys.append(y)
    return background, (min(xs), min(ys), max(xs) + 1, max(ys) + 1)


def row_median_color(image, y, ranges):
    channels = [[], [], []]
    for start, end in ranges:
        for x in range(start, end):
            pixel = image.getpixel((x, y))[:3]
            for channel in range(3):
                channels[channel].append(pixel[channel])
    return tuple(sorted(values)[len(values) // 2] for values in channels)


def patch_rows(output, source, box, sample_ranges):
    left, top, right, bottom = box
    pixels = output.load()
    for y in range(top, bottom):
        color = row_median_color(source, y, sample_ranges)
        for x in range(left, right):
            pixels[x, y] = (*color, 255)


def make_dynamic_cover(source, patches, filename):
    cover = Image.new("RGBA", source.size, (0, 0, 0, 0))
    for box, sample_ranges in patches:
        patch_rows(cover, source, box, sample_ranges)
    cover.save(OUTPUT_DIR / filename)
    print(filename, cover.size)


def main():
    image = Image.open(REFERENCE).convert("RGBA")
    background, bbox = non_background_bbox(image)
    print("reference", image.size, "background", background, "content_bbox", bbox)

    samples = {
        "left_panel": (100, 300),
        "right_panel": (600, 450),
        "inventory_slot": (75, 105),
        "sell_slot": (390, 310),
        "purchase_window": (450, 150),
    }
    for name, point in samples.items():
        print(name, point, image.getpixel(point))

    reference_crop = image.crop(SHOP_CROP)
    old_base = Image.open(OLD_BASE).convert("RGBA")
    if reference_crop.size != old_base.size:
        raise RuntimeError(f"Reference crop {reference_crop.size} does not match old base {old_base.size}")

    base = reference_crop.copy()
    base.putalpha(old_base.getchannel("A"))
    base_pixels = base.load()
    for y in range(0, 21):
        for x in range(34, 170):
            base_pixels[x, y] = (0, 0, 0, 0)
    patch_rows(base, reference_crop, (625, 451, 728, 470), ((619, 625), (728, 734)))
    base.save(OUTPUT_DIR / "shop_base_reference_exact.png")
    print("shop_base_reference_exact.png", base.size)

    inventory = reference_crop.crop((36, 71, 94, 131))
    make_dynamic_cover(
        inventory,
        [((6, 36, 52, 55), ((6, 12), (46, 52)))],
        "shop_inventory_dynamic_cover.png",
    )

    sell = reference_crop.crop((334, 260, 420, 349))
    make_dynamic_cover(
        sell,
        [((7, 67, 79, 85), ((7, 14), (72, 79)))],
        "shop_sell_dynamic_cover.png",
    )

    purchase = reference_crop.crop((360, 72, 513, 251))
    make_dynamic_cover(
        purchase,
        [
            ((19, 13, 134, 33), ((19, 26), (127, 134))),
            ((19, 108, 134, 130), ((19, 26), (127, 134))),
            ((22, 143, 131, 160), ((22, 31), (122, 131))),
        ],
        "shop_purchase_dynamic_cover.png",
    )


if __name__ == "__main__":
    main()
