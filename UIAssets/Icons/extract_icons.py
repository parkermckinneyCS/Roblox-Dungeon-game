from pathlib import Path

from psd_tools import PSDImage


PSD_PATH = Path(r"C:\Users\ppark\Downloads\Nile Pixel art UI\Nile Pixel art UI.psd")
OUTPUT_DIR = Path(__file__).resolve().parent
ICON_LAYERS = {
    "PotionIcon": "potion_icon.png",
    "BombIcon": "bomb_icon.png",
    "KeyIcon": "key_icon.png",
    "GoldIcon": "gold_icon.png",
    "DashIcon": "dash_icon.png",
}


def main() -> None:
    psd = PSDImage.open(PSD_PATH)
    icons_group = next(layer for layer in psd if layer.name == "Icons")

    for layer in icons_group:
        output_name = ICON_LAYERS.get(layer.name)
        if output_name is None:
            continue

        image = layer.composite()
        if image is None:
            raise RuntimeError(f"Could not composite PSD layer {layer.name!r}")
        image.save(OUTPUT_DIR / output_name)
        print(f"{layer.name}: {image.size} -> {output_name}")


if __name__ == "__main__":
    main()
