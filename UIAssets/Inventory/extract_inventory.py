from pathlib import Path

from PIL import Image
from psd_tools import PSDImage


PSD_PATH = Path(r"C:\Users\ppark\Downloads\Nile Pixel art UI\Nile Pixel art UI.psd")
MAIN_REFERENCE = Path(r"C:\Users\ppark\AppData\Local\Temp\codex-clipboard-e29ae016-a0d6-4e9c-b5c7-1f9383642e9e.png")
SHOP_ALPHA = Path(__file__).resolve().parents[1] / "Shop" / "shop_base_exact.png"
SHOP_REFERENCE_BASE = Path(__file__).resolve().parents[1] / "Shop" / "shop_base_reference_exact.png"
OUTPUT_DIR = Path(__file__).resolve().parent
MAIN_CROP = (20, 0, 926, 518)


def child(parent, name):
    return next(layer for layer in parent if layer.name == name)


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


def extract_main():
    reference = Image.open(MAIN_REFERENCE).convert("RGBA")
    crop = reference.crop(MAIN_CROP)
    alpha = Image.open(SHOP_ALPHA).convert("RGBA").getchannel("A")
    if crop.size != alpha.size:
        raise RuntimeError(f"Inventory crop {crop.size} does not match alpha {alpha.size}")

    base = crop.copy()
    base.putalpha(alpha)

    # Reuse the identical main-frame top-right strip after the Photoshop guide boxes were removed.
    shop_reference = Image.open(SHOP_REFERENCE_BASE).convert("RGBA")
    base.paste(shop_reference.crop((570, 0, 906, 26)), (570, 0))

    pixels = base.load()
    for y in range(0, 21):
        for x in range(34, 170):
            pixels[x, y] = (0, 0, 0, 0)

    # Remove the baked search placeholder while retaining its icon and exact bar surface.
    patch_rows(base, crop, (646, 102, 860, 122), ((642, 646), (860, 866)))

    # Remove baked stat values; live values are placed over these exact dark value plates.
    for top in (110, 156, 202, 248, 294, 340):
        patch_rows(base, crop, (530, top, 552, top + 16), ((524, 530), (552, 558)))

    base.save(OUTPUT_DIR / "inventory_base_reference_exact.png")
    print("inventory_base_reference_exact.png", base.size)

    # Equipped items cover the baked reference icon with this clean slot interior.
    cover_source = crop.crop((97, 124, 130, 157))
    cover = Image.new("RGBA", cover_source.size, (0, 0, 0, 255))
    cover_pixels = cover.load()
    for y in range(cover.height):
        sample_y = max(3, min(29, y))
        color = row_median_color(cover_source, sample_y, ((3, 6), (27, 30)))
        for x in range(cover.width):
            cover_pixels[x, y] = (*color, 255)
    cover.save(OUTPUT_DIR / "inventory_equipment_slot_cover.png")
    print("inventory_equipment_slot_cover.png", cover.size)

    # Exact selected/equipped slot art from the reference. Only its center is
    # cleaned, so the original gold pixel border is never recreated by code.
    equipped_frame = crop.crop((93, 120, 134, 161))
    equipped_frame.paste(cover.resize((27, 27), Image.Resampling.NEAREST), (7, 7))
    equipped_frame.save(OUTPUT_DIR / "inventory_equipment_equipped_frame.png")
    print("inventory_equipment_equipped_frame.png", equipped_frame.size)


def hide_types(layer):
    for descendant in layer.descendants():
        if descendant.kind == "type":
            descendant.visible = False


def normalize_frame(image, canvas=(72, 72)):
    output = Image.new("RGBA", canvas, (0, 0, 0, 0))
    output.alpha_composite(image, ((canvas[0] - image.width) // 2, (canvas[1] - image.height) // 2))
    return output


def make_common_white(uncommon):
    output = uncommon.copy()
    pixels = output.load()
    for y in range(output.height):
        for x in range(output.width):
            r, g, b, a = pixels[x, y]
            if a > 0 and g > r * 1.12 and g > b * 1.08:
                if g >= 70:
                    brightness = max(190, min(255, round(max(r, g, b) * 1.25)))
                    pixels[x, y] = (brightness, brightness, brightness, a)
                else:
                    neutral = max(10, round((r + g + b) / 3))
                    pixels[x, y] = (neutral, neutral, neutral, a)
    return output


def deepen_legendary_red(image):
    output = image.copy()
    pixels = output.load()
    for y in range(output.height):
        for x in range(output.width):
            r, g, b, a = pixels[x, y]
            # Recolor the crisp Epic frame instead of retaining the Legendary
            # layer's broad neon glow. Gold/dark engraved details stay intact.
            if a > 0 and r > g * 1.12 and b > g * 1.18:
                intensity = max(r, b)
                pixels[x, y] = (
                    min(155, round(intensity * 0.68)),
                    max(6, round(intensity * 0.11)),
                    max(5, round(intensity * 0.09)),
                    round(a * 0.35) if a < 210 else a,
                )
    return output


def extract_psd_assets():
    psd = PSDImage.open(PSD_PATH)
    root = next(layer for layer in psd.descendants() if layer.is_group() and layer.name == "Inventory")
    root.visible = True

    item_popup = child(root, "ItemPopUp")
    hide_types(item_popup)
    popup = item_popup.composite(force=True).convert("RGBA")
    popup.save(OUTPUT_DIR / "inventory_item_popup_base.png")
    print("inventory_item_popup_base.png", popup.size)

    rarity_boxes = child(child(root, "Items"), "RarityBoxes")
    rarity_layers = {
        "Uncommon": child(rarity_boxes, "Common"),
        "Rare": child(rarity_boxes, "Rare"),
        "Epic": child(rarity_boxes, "Epic"),
        "Legendary": child(rarity_boxes, "Legendary"),
    }
    outputs = {}
    for rarity, layer in rarity_layers.items():
        hide_types(layer)
        outputs[rarity] = normalize_frame(layer.composite(force=True).convert("RGBA"))

    outputs["Common"] = make_common_white(outputs["Uncommon"])
    outputs["Legendary"] = deepen_legendary_red(outputs["Epic"])
    for rarity, image in outputs.items():
        filename = f"inventory_slot_{rarity.lower()}.png"
        image.save(OUTPUT_DIR / filename)
        print(filename, image.size)


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    extract_main()
    extract_psd_assets()


if __name__ == "__main__":
    main()
