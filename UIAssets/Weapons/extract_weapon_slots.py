from pathlib import Path

from psd_tools import PSDImage


PSD_PATH = Path(r"C:\Users\ppark\Downloads\Nile Pixel art UI\Nile Pixel art UI.psd")
OUTPUT_DIR = Path(__file__).resolve().parent


def make_transparent(image, canvas_rgb):
    """Remove only the PSD's flat mockup canvas while preserving rendered effects."""
    rgba = image.convert("RGBA")
    rgba.putdata(
        [
            (red, green, blue, 0 if (red, green, blue) == canvas_rgb else alpha)
            for red, green, blue, alpha in rgba.getdata()
        ]
    )
    return rgba


def main() -> None:
    psd = PSDImage.open(PSD_PATH)
    merged = psd.topil()
    canvas_rgb = merged.convert("RGB").getpixel((0, 0))
    boxes = next(layer for layer in psd if layer.name == "EquipmentBoxes")
    exports = {
        "EquipmentBoxSelected": "weapon_slot_selected.png",
        "EquipmentBox": "weapon_slot_unselected.png",
    }

    for layer in boxes:
        output_name = exports.get(layer.name)
        if output_name is None:
            continue

        # PSDImage.topil() uses Photoshop's stored composite, retaining the
        # authored overlays, strokes, shadows, and glows that layer.composite()
        # does not render.
        image = make_transparent(merged.crop(layer.bbox), canvas_rgb)
        image.save(OUTPUT_DIR / output_name)
        print(f"{layer.name}: {image.size} -> {output_name}")


if __name__ == "__main__":
    main()
