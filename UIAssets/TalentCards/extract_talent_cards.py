from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter
from psd_tools import PSDImage


PSD_PATH = Path(r"C:\Users\ppark\Downloads\Nile Pixel art UI\Nile Pixel art UI.psd")
OUTPUT_DIR = Path(__file__).resolve().parent


def padded_frame_with_glow(frame_image):
    padding = 8
    width, height = frame_image.size
    canvas_size = (width + padding * 2, height + padding * 2)
    alpha = Image.new("L", canvas_size)
    alpha.paste(frame_image.getchannel("A"), (padding, padding))
    blurred = alpha.filter(ImageFilter.GaussianBlur(4))
    glow_alpha = blurred.point(lambda value: round(value * 0.48))
    glow = Image.new("RGBA", canvas_size, (116, 71, 8, 0))
    glow.putalpha(glow_alpha)
    glow.alpha_composite(frame_image, (padding, padding))
    return glow


def padded_composite_with_glow(image, padding, radius, color, strength, spread=0):
    canvas_size = (image.width + padding * 2, image.height + padding * 2)
    alpha = Image.new("L", canvas_size)
    alpha.paste(image.getchannel("A"), (padding, padding))
    glow_source = alpha
    if spread > 0:
        spread_size = max(3, int(spread) | 1)
        glow_source = alpha.filter(ImageFilter.MaxFilter(spread_size))
    blurred = glow_source.filter(ImageFilter.GaussianBlur(radius))
    glow_alpha = blurred.point(lambda value: min(255, round(value * strength)))
    output = Image.new("RGBA", canvas_size, (*color, 0))
    output.putalpha(glow_alpha)
    output.alpha_composite(image, (padding, padding))
    return output


def complete_reward_medallion(inner_icon):
    size = 95
    padding = 8
    diameter = 79
    center = (size - 1) / 2
    radius = diameter / 2

    shadow_mask = Image.new("L", (size, size))
    shadow_draw = ImageDraw.Draw(shadow_mask)
    shadow_draw.ellipse(
        (padding, padding, padding + diameter - 1, padding + diameter - 1),
        fill=190,
    )
    shadow_mask = shadow_mask.filter(ImageFilter.GaussianBlur(5))
    output = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    shadow = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    shadow.putalpha(shadow_mask)
    output.alpha_composite(shadow)

    pixels = output.load()
    for y in range(size):
        vertical = max(0.0, min(1.0, (y - padding) / max(1, diameter - 1)))
        top = (142, 181, 205)
        bottom = (38, 43, 48)
        base = tuple(round(top[i] * (1 - vertical) + bottom[i] * vertical) for i in range(3))
        for x in range(size):
            distance = ((x - center) ** 2 + (y - center) ** 2) ** 0.5
            if distance <= radius:
                if distance > radius - 2.0:
                    color = (10, 12, 14)
                elif distance > radius - 5.0:
                    color = tuple(max(0, round(channel * 0.72)) for channel in base)
                else:
                    color = base
                pixels[x, y] = (*color, 255)

    output.alpha_composite(inner_icon, (padding, padding))
    return output


def main():
    psd = PSDImage.open(PSD_PATH)
    root = next(layer for layer in psd.descendants() if layer.name == "TalentCards")
    root.visible = True
    cards = next(layer for layer in root if layer.name == "Cards")
    card = next(layer for layer in cards if layer.name == "Card")
    main_body = next(layer for layer in card if layer.name == "MainBody")
    body_background = next(layer for layer in main_body if layer.name == "Bg")
    body_frame = next(layer for layer in main_body if layer.name == "Frame")
    item_window = next(layer for layer in card if layer.name == "ItemWindow")
    title = next(layer for layer in card if layer.name == "Title")
    title_background = next(layer for layer in title if layer.name == "Bg")
    title_frame = next(layer for layer in title if layer.name == "Frame")
    title_text = next(layer for layer in title if layer.kind == "type")
    description_text = next(layer for layer in main_body if layer.kind == "type")

    reward = next(layer for layer in root if layer.name == "+Talent")
    reward_outer = next(layer for layer in reward if layer.name == "Ellipse 3")
    reward_inner = next(layer for layer in reward if layer.name == "Ellipse 2")
    reward_title = next(layer for layer in reward if layer.kind == "type" and layer.text.strip() == "+1 Talent")
    reward_description = next(layer for layer in reward if layer.kind == "type" and layer is not reward_title)
    reward_icon = Image.new("RGBA", (79, 79))
    reward_icon.alpha_composite(reward_outer.composite(force=True).convert("RGBA"), (0, 0))
    reward_icon.alpha_composite(reward_inner.composite(force=True).convert("RGBA"), (8, 7))

    title_text.visible = False
    description_text.visible = False
    card_base_exact = card.composite().convert("RGBA")
    reward_title.visible = False
    reward_description.visible = False
    reward_icon_exact = reward.composite().convert("RGBA")
    reward_title.visible = True
    reward_title_exact = reward_title.composite(force=True).convert("RGBA")
    card_complete_exact = padded_composite_with_glow(
        card_base_exact, 25, 12.5, (255, 156, 0), 0.25
    )
    reward_icon_glow_exact = padded_composite_with_glow(
        reward_icon_exact, 12, 6, (76, 151, 199), 0.55
    )
    reward_medallion_complete = complete_reward_medallion(reward_icon_exact)

    body_frame_image = body_frame.composite(force=True).convert("RGBA")
    outputs = {
        "talent_card_background.png": body_background.composite(force=True).convert("RGBA"),
        "talent_card_frame.png": body_frame_image,
        "talent_card_frame_glow.png": padded_frame_with_glow(body_frame_image),
        "talent_card_item_window.png": item_window.composite(force=True).convert("RGBA"),
        "talent_card_title_background.png": title_background.composite(force=True).convert("RGBA"),
        "talent_card_title_frame.png": title_frame.composite(force=True).convert("RGBA"),
        "talent_reward_icon.png": reward_icon,
        "talent_card_base_exact.png": card_base_exact,
        "talent_reward_icon_exact.png": reward_icon_exact,
        "talent_reward_title_exact.png": reward_title_exact,
        "talent_card_complete_base_exact.png": card_complete_exact,
        "talent_reward_icon_glow_exact.png": reward_icon_glow_exact,
        "talent_reward_medallion_complete.png": reward_medallion_complete,
        "talent_card_reference.png": card.composite(force=True).convert("RGBA"),
    }

    visual = next((layer for layer in cards if layer.name == "VISUAL"), None)
    if visual is not None:
        outputs["talent_cards_visual_reference.png"] = visual.composite(force=True).convert("RGBA")

    for filename, image in outputs.items():
        image.save(OUTPUT_DIR / filename)
        print(filename, image.size)


if __name__ == "__main__":
    main()
