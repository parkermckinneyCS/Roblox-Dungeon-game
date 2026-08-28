from pathlib import Path

from psd_tools import PSDImage


PSD_PATH = Path(r"C:\Users\ppark\Downloads\Nile Pixel art UI\Nile Pixel art UI.psd")


def print_tree(layer, depth=0):
    print(
        "  " * depth,
        repr(layer.name),
        layer.kind,
        layer.bbox,
        f"effects={list(layer.effects) if hasattr(layer, 'effects') else []}",
    )
    if layer.is_group():
        for child in layer:
            print_tree(child, depth + 1)
    elif layer.kind == "type":
        style = layer.engine_dict["StyleRun"]["RunArray"][0]["StyleSheet"]["StyleSheetData"]
        print("  " * (depth + 1), f"text={layer.text!r}", f"font_size={style.get('FontSize')}")
        print("  " * (depth + 1), "font_set=", layer.resource_dict.get("FontSet"))


def main():
    psd = PSDImage.open(PSD_PATH)
    for layer in psd:
        if any(word in layer.name.lower() for word in ("health", "boss", "mana")):
            print_tree(layer)


if __name__ == "__main__":
    main()
