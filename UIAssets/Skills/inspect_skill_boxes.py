from pathlib import Path

from psd_tools import PSDImage


PSD_PATH = Path(r"C:\Users\ppark\Downloads\Nile Pixel art UI\Nile Pixel art UI.psd")


def print_tree(layer, depth=0):
    print(
        "  " * depth,
        repr(layer.name),
        layer.kind,
        layer.bbox,
        f"visible={layer.is_visible()}",
        f"effects={list(layer.effects) if hasattr(layer, 'effects') else []}",
    )
    if layer.is_group():
        for child in layer:
            print_tree(child, depth + 1)
    elif layer.kind == "type":
        print("  " * (depth + 1), "text=", repr(layer.text))
        print("  " * (depth + 1), "font_set=", layer.resource_dict.get("FontSet"))


def main():
    psd = PSDImage.open(PSD_PATH)
    for layer in psd:
        if "skill" in layer.name.lower():
            print_tree(layer)


if __name__ == "__main__":
    main()
