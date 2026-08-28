from pathlib import Path

from PIL import Image, ImageFilter
from psd_tools import PSDImage


PSD_PATH = Path(r"C:\Users\ppark\Downloads\Nile Pixel art UI\Nile Pixel art UI.psd")
OUTPUT_DIR = Path(__file__).resolve().parent


def remove_canvas(image, canvas_rgb):
    rgba = image.convert("RGBA")
    rgba.putdata(
        [
            (red, green, blue, 0 if (red, green, blue) == canvas_rgb else alpha)
            for red, green, blue, alpha in rgba.getdata()
        ]
    )
    return rgba


def build_text_effect_mask(group, text_layer, size):
    mask = Image.new("L", size, 0)
    rendered = text_layer.composite()
    mask.paste(
        rendered.getchannel("A"),
        (text_layer.left - group.left, text_layer.top - group.top),
    )
    return mask.filter(ImageFilter.MaxFilter(7))


def erase_mask(image, mask):
    pixels = image.load()
    mask_pixels = mask.load()
    width, height = image.size

    for y in range(height):
        masked = {x for x in range(width) if mask_pixels[x, y] > 0}
        for x in range(width):
            if x not in masked:
                continue

            left = x - 1
            while left >= 0 and left in masked:
                left -= 1
            right = x + 1
            while right < width and right in masked:
                right += 1
            if left < 0 or right >= width:
                continue

            blend = (x - left) / (right - left)
            pixels[x, y] = tuple(
                round(a + (b - a) * blend)
                for a, b in zip(pixels[left, y], pixels[right, y])
            )


def main():
    psd = PSDImage.open(PSD_PATH)
    merged = psd.topil()
    canvas_rgb = merged.convert("RGB").getpixel((0, 0))
    floor_group = next(layer for layer in psd if layer.name == "Floor")
    text_layer = next(layer for layer in floor_group if layer.kind == "type")

    plate = remove_canvas(merged.crop(floor_group.bbox), canvas_rgb)
    erase_mask(plate, build_text_effect_mask(floor_group, text_layer, plate.size))
    plate.save(OUTPUT_DIR / "floor_plate.png")
    print(f"Floor: {plate.size} -> floor_plate.png")


if __name__ == "__main__":
    main()
