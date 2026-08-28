from pathlib import Path

from psd_tools import PSDImage


PSD_PATH = Path(r"C:\Users\ppark\Downloads\Nile Pixel art UI\Nile Pixel art UI.psd")


def main():
    psd = PSDImage.open(PSD_PATH)
    root = next(layer for layer in psd.descendants() if layer.name == "TalentCards")
    root.visible = True
    for layer in root.descendants():
        if layer.kind == "type" or layer.name == "Card":
            print("LAYER", repr(layer.name), layer.bbox)
            for effect in layer.effects:
                print(" ", type(effect).__name__, repr(effect))
                for name in dir(effect):
                    if name.startswith("_") or name in {"enabled", "shown"}:
                        continue
                    try:
                        value = getattr(effect, name)
                    except Exception:
                        continue
                    if not callable(value):
                        print("   ", name, repr(value))


if __name__ == "__main__":
    main()
