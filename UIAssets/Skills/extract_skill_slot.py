from pathlib import Path
from PIL import Image, ImageFilter
from psd_tools import PSDImage


PSD_PATH = Path(r"C:\Users\ppark\Downloads\Nile Pixel art UI\Nile Pixel art UI.psd")
OUTPUT_PATH = Path(__file__).resolve().parent / "skill_slot.png"


def remove_canvas(image, canvas_rgb):
    rgba = image.convert("RGBA")
    rgba.putdata(
        [
            (red, green, blue, 0 if (red, green, blue) == canvas_rgb else alpha)
            for red, green, blue, alpha in rgba.getdata()
        ]
    )
    return rgba


def build_text_effect_mask(slot, text_layer, slot_size):
    mask = Image.new("L", slot_size, 0)
    rendered = text_layer.composite()
    mask.paste(
        rendered.getchannel("A"),
        (text_layer.left - slot.left, text_layer.top - slot.top),
    )
    return mask.filter(ImageFilter.MaxFilter(7))


def erase_mask(image, mask):
    """Restore only masked type pixels from their nearest clean neighbors."""
    pixels = image.load()
    mask_pixels = mask.load()
    width, height = image.size

    for y in range(height):
        masked = {x for x in range(width) if mask_pixels[x, y] > 0}
        for x in range(width):
            if x not in masked:
                continue

            left_source = x - 1
            while left_source >= 0 and left_source in masked:
                left_source -= 1
            right_source = x + 1
            while right_source < width and right_source in masked:
                right_source += 1

            if left_source < 0 or right_source >= width:
                continue

            left_color = pixels[left_source, y]
            right_color = pixels[right_source, y]
            span = max(1, right_source - left_source)
            blend = (x - left_source) / span
            pixels[x, y] = tuple(
                round(left_channel + (right_channel - left_channel) * blend)
                for left_channel, right_channel in zip(left_color, right_color)
            )


def main():
    psd = PSDImage.open(PSD_PATH)
    merged = psd.topil()
    canvas_rgb = merged.convert("RGB").getpixel((0, 0))
    boxes = next(layer for layer in psd if layer.name == "SkillBoxes")
    slot = next(layer for layer in boxes if layer.name == "SkillBox")

    output = remove_canvas(merged.crop(slot.bbox), canvas_rgb)
    # The frame is kept byte-for-byte from Photoshop. The masks are grown from
    # the real type glyphs to include their authored stroke and drop shadow.
    for layer in slot:
        if layer.kind == "type":
            erase_mask(output, build_text_effect_mask(slot, layer, output.size))

    # Remove only the dark-brown inner strip beneath the skill name. The full
    # black/gold/black bottom frame at rows 67-69 remains untouched.
    pixels = output.load()
    for y in range(63, 67):
        for x in range(9, 62):
            pixels[x, y] = pixels[x, 62]

    output.save(OUTPUT_PATH)
    print(f"SkillBox: {output.size} -> {OUTPUT_PATH.name}")


if __name__ == "__main__":
    main()
