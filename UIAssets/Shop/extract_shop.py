from pathlib import Path

from psd_tools import PSDImage


PSD_PATH = Path(r"C:\Users\ppark\Downloads\Nile Pixel art UI\Nile Pixel art UI.psd")
OUTPUT_DIR = Path(__file__).resolve().parent
SHOP_BOUNDS = (507, 288, 1413, 806)


def child(parent, name):
    return next(layer for layer in parent if layer.name == name)


def shop_root(psd):
    return next(layer for layer in psd.descendants() if layer.is_group() and layer.name == "Shop")


def hide_type_descendants(layer):
    for descendant in layer.descendants():
        if descendant.kind == "type":
            descendant.visible = False


def extract_group_asset(group, filename):
    hide_type_descendants(group)
    image = group.composite(force=True).convert("RGBA")
    image.save(OUTPUT_DIR / filename)
    print(filename, image.size)


def extract_base():
    psd = PSDImage.open(PSD_PATH)
    root = shop_root(psd)
    for layer in psd:
        layer.visible = layer is root
    root.visible = True

    main_body = child(root, "MainBody")
    equipment = child(root, "Equipment")
    items = child(root, "Items")

    child(equipment, "EquipmentSlots").visible = False
    child(items, "EquipmentSlots").visible = False
    child(items, "PurchaseSlots").visible = False

    for descendant in main_body.descendants():
        if descendant.kind == "type":
            descendant.visible = False

    buttons = child(items, "Buttons")
    price_group = child(buttons, "$PRICE")
    for descendant in price_group.descendants():
        if descendant.kind == "type":
            descendant.visible = False

    image = psd.composite().convert("RGBA").crop(SHOP_BOUNDS)
    image.save(OUTPUT_DIR / "shop_base_exact.png")
    print("shop_base_exact.png", image.size)


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    extract_base()

    psd = PSDImage.open(PSD_PATH)
    root = shop_root(psd)
    root.visible = True
    equipment = child(root, "Equipment")
    inventory_slot = child(child(equipment, "EquipmentSlots"), "EquipmentSlot")
    extract_group_asset(inventory_slot, "shop_inventory_slot_exact.png")

    psd = PSDImage.open(PSD_PATH)
    root = shop_root(psd)
    root.visible = True
    items = child(root, "Items")
    sell_slot = child(child(items, "EquipmentSlots"), "EquipmentSlot")
    extract_group_asset(sell_slot, "shop_sell_slot_exact.png")

    psd = PSDImage.open(PSD_PATH)
    root = shop_root(psd)
    root.visible = True
    items = child(root, "Items")
    purchase_slot = child(child(items, "PurchaseSlots"), "PurchaseSlot")
    extract_group_asset(purchase_slot, "shop_purchase_slot_exact.png")


if __name__ == "__main__":
    main()
