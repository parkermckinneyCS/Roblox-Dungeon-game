from pathlib import Path

from psd_tools import PSDImage


PSD_PATH = Path(r"C:\Users\ppark\Downloads\Nile Pixel art UI\Nile Pixel art UI.psd")
OUTPUT_DIR = Path(__file__).resolve().parent


def main():
    psd = PSDImage.open(PSD_PATH)
    root = next(layer for layer in psd.descendants() if layer.name == "EnemyOverhead")
    background = next(layer for layer in root if layer.name == "Bg")
    bar = next(layer for layer in root if layer.name == "Bar")
    frame = next(layer for layer in root if layer.name == "Frame")

    outputs = {
        "enemy_overhead_background.png": background.composite().convert("RGBA"),
        "enemy_overhead_fill.png": bar.composite().convert("RGBA"),
        "enemy_overhead_frame.png": frame.composite().convert("RGBA"),
        "enemy_overhead_reference.png": root.composite().convert("RGBA"),
    }

    for filename, image in outputs.items():
        image.save(OUTPUT_DIR / filename)
        print(filename, image.size)


if __name__ == "__main__":
    main()
