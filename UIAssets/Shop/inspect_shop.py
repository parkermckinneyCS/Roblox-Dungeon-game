from pathlib import Path

from psd_tools import PSDImage


PSD_PATH = Path(r"C:\Users\ppark\Downloads\Nile Pixel art UI\Nile Pixel art UI.psd")


def style_summary(layer):
    if layer.kind != "type":
        return ""
    try:
        style = layer.engine_dict["StyleRun"]["RunArray"][0]["StyleSheet"]["StyleSheetData"]
        return f" text={layer.text!r} font_size={style.get('FontSize')} style={style} fonts={layer.resource_dict.get('FontSet')}"
    except Exception as exc:
        return f" text={getattr(layer, 'text', '')!r} style_error={exc!r}"


def print_tree(layer, depth=0):
    effects = list(layer.effects) if hasattr(layer, "effects") else []
    print(
        "  " * depth
        + f"{layer.name!r} kind={layer.kind} bbox={layer.bbox} visible={layer.visible} effects={effects}"
        + style_summary(layer)
    )
    if layer.is_group():
        for child in layer:
            print_tree(child, depth + 1)


def main():
    psd = PSDImage.open(PSD_PATH)
    matches = [layer for layer in psd.descendants() if "shop" in layer.name.lower().replace(" ", "")]
    print("document", psd.size, "matches", [(m.name, m.kind, m.bbox) for m in matches])
    roots = [m for m in matches if m.is_group() and m.name.lower().replace(" ", "") == "shop"]
    for root in roots:
        print("\n=== SHOP ROOT ===")
        print_tree(root)


if __name__ == "__main__":
    main()
