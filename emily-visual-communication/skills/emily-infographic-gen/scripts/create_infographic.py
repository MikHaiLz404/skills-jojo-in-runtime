#!/usr/bin/env python3
"""
Infographic Generator - Create professional infographics from text.

Usage:
    python3 create_infographic.py --title "Title" --data "Key1:Val1|Key2:Val2" --output output.png
    python3 create_infographic.py --interactive  # Interactive mode

As module:
    from infographic import create_infographic
    create_infographic("Title", {"Item": "Description"}, output_path="out.png")
"""

import argparse
import sys
from pathlib import Path

# Add parent dir to path for import
sys.path.insert(0, str(Path(__file__).parent))


def create_infographic(
    title: str,
    items: dict = None,
    subtitle: str = "",
    theme: str = "modern",
    accent_color: str = None,
    output_path: str = "infographic.png",
    width: int = 1920,
    height: int = 1080,
    style: str = "timeline"  # timeline | cards | list
):
    """Create infographic and save to file.

    Args:
        title: Main title text
        items: Dict of {category: [(label, description), ...]} or {label: description}
        subtitle: Subtitle text
        theme: "modern" (white) or "dark" (navy)
        accent_color: Hex color without # (e.g., "22c55e")
        output_path: Output file path
        width: Image width
        height: Image height
        style: "timeline" | "cards" | "list"
    """
    from PIL import Image, ImageDraw, ImageFont

    # Default accent colors
    default_accents = {
        "green": (82, 196, 150),
        "blue": (69, 129, 224),
        "red": (230, 61, 70),
        "gold": (255, 186, 0),
    }

    # Theme colors
    if theme == "dark":
        BG = (15, 23, 42)
        BG_CARD = (30, 41, 59)
        TEXT = (255, 255, 255)
        TEXT_DIM = (148, 163, 184)
        SEPARATOR = (71, 85, 105)
    else:
        BG = (245, 247, 250)
        BG_CARD = (255, 255, 255)
        TEXT = (45, 52, 64)
        TEXT_DIM = (120, 125, 140)
        SEPARATOR = (180, 185, 194)

    if accent_color:
        if accent_color.startswith("#"):
            accent_color = accent_color[1:]
        r = int(accent_color[0:2], 16)
        g = int(accent_color[2:4], 16)
        b = int(accent_color[4:6], 16)
        ACCENT = (r, g, b)
    else:
        ACCENT = default_accents["green"]

    def load_font(size, bold=False):
        paths = [
            "/System/Library/Fonts/Avenir.ttc",
            "/System/Library/Fonts/Avenir Next.ttc",
            "/System/Library/Fonts/SF Pro Display.ttc",
            "/System/Library/Fonts/Helvetica.ttc",
            "/System/Library/Fonts/Arial.ttf",
            "/System/Library/Fonts/Georgia.ttc",
        ]
        for fp in paths:
            try:
                return ImageFont.truetype(fp, size)
            except:
                continue
        return ImageFont.load_default()

    # Create image
    img = Image.new("RGB", (width, height), BG)
    draw = ImageDraw.Draw(img)

    # Helper functions
    def draw_text(text, x, y, font, color):
        draw.text((x, y), text, font=font, fill=color)

    def center_text(text, y, font, color, max_width=None):
        bbox = font.getbbox(text)
        w = bbox[2] - bbox[0]
        if max_width and w > max_width:
            scale = max_width / w
            new_size = int(font.size * scale * 0.9)
            try:
                small_font = font.font_variant(size=new_size)
                bbox = small_font.getbbox(text)
                w = bbox[2] - bbox[0]
                x = (width - w) // 2
                draw.text((x, y), text, font=small_font, fill=color)
                return
            except:
                pass
        x = (width - w) // 2
        draw.text((x, y), text, font=font, fill=color)

    # === HEADER ===
    # Top accent bar
    draw.rectangle([(0, 0), (width, 8)], fill=ACCENT)

    # Title
    title_font = load_font(64, bold=True)
    subtitle_font = load_font(28)

    draw_text(title, 80, 50, title_font, TEXT)
    if subtitle:
        draw_text(subtitle, 80, 130, subtitle_font, TEXT_DIM)

    # Header separator
    draw.rectangle([(80, 170), (width - 80, 174)], fill=SEPARATOR)

    # === CONTENT AREA ===
    content_y = 220
    card_h = height - content_y - 120
    card_w = (width - 200) // 2
    card_gap = 40
    card_start_x = (width - (2 * card_w + card_gap)) // 2

    if items is None:
        items = {}

    # Convert simple dict to categories
    if items and not any(isinstance(v, list) for v in items.values()):
        # Simple {label: description} format
        simple_items = {}
        for k, v in items.items():
            simple_items[k] = [(k, v)]
        items = simple_items
    elif items:
        # Check if values are tuples/lists
        new_items = {}
        for k, v in items.items():
            if isinstance(v, list):
                new_items[k] = v
            else:
                new_items[k] = [(k, str(v))]
        items = new_items
    else:
        items = {"Items": []}

    # Draw section cards
    categories = list(items.keys())

    # Card 1: First category
    if len(categories) >= 1:
        cat1 = categories[0]
        card1_x = card_start_x

        draw.rounded_rectangle(
            [(card1_x, content_y), (card1_x + card_w, content_y + card_h)],
            radius=20, fill=BG_CARD, outline=ACCENT, width=3
        )

        # Header
        header_h = 80
        draw.rounded_rectangle(
            [(card1_x, content_y), (card1_x + card_w, content_y + header_h)],
            radius=20, fill=ACCENT
        )
        draw.rectangle([(card1_x, content_y + 50), (card1_x + card_w, content_y + header_h)], fill=ACCENT)

        header_font = load_font(28, bold=True)
        draw_text(cat1, card1_x + 30, content_y + 20, header_font, (255, 255, 255))

        # Items
        item_y = content_y + 110
        col_w = card_w // 2
        item_list = items[cat1] if items[cat1] else [(cat1, "")]

        for idx, item_data in enumerate(item_list):
            if isinstance(item_data, tuple):
                label, desc = item_data
            else:
                label = str(item_data)
                desc = ""

            col = idx % 2
            row = idx // 2
            x = card1_x + 30 + col * col_w
            y = item_y + row * 50

            # Bullet
            bullet_size = 10 if theme == "dark" else 8
            draw.ellipse([(x, y + 4), (x + bullet_size, y + 4 + bullet_size)], fill=ACCENT)

            # Text
            cf = load_font(18, bold=True)
            draw_text(label, x + 18, y, cf, TEXT)
            if desc:
                df = load_font(14)
                draw_text(desc, x + 18, y + 24, df, TEXT_DIM)

    # Card 2: Second category (or combined)
    if len(categories) >= 2:
        cat2 = categories[1]
        card2_x = card_start_x + card_w + card_gap

        # Different accent for card 2
        card2_accent = default_accents.get("blue", ACCENT)

        draw.rounded_rectangle(
            [(card2_x, content_y), (card2_x + card_w, content_y + card_h)],
            radius=20, fill=BG_CARD, outline=card2_accent, width=3
        )

        # Header
        draw.rounded_rectangle(
            [(card2_x, content_y), (card2_x + card_w, content_y + header_h)],
            radius=20, fill=card2_accent
        )
        draw.rectangle([(card2_x, content_y + 50), (card2_x + card_w, content_y + header_h)], fill=card2_accent)

        draw_text(cat2, card2_x + 30, content_y + 20, header_font, (255, 255, 255))

        # Items
        item_y = content_y + 110
        item_list = items[cat2] if items[cat2] else [(cat2, "")]

        for idx, item_data in enumerate(item_list):
            if isinstance(item_data, tuple):
                label, desc = item_data
            else:
                label = str(item_data)
                desc = ""

            col = idx % 2
            row = idx // 2
            x = card2_x + 30 + col * col_w
            y = item_y + row * 50

            draw.ellipse([(x, y + 4), (x + 8, y + 12)], fill=card2_accent)

            cf = load_font(18, bold=True)
            draw_text(label, x + 18, y, cf, TEXT)
            if desc:
                df = load_font(14)
                draw_text(desc, x + 18, y + 24, df, TEXT_DIM)
    elif len(categories) == 1 and len(item_list) > 6:
        # Single category with many items - show in 2 columns within one card
        # Already handled above
        pass

    # === FOOTER ===
    footer_y = height - 60
    draw.rectangle([(80, footer_y - 10), (width - 80, footer_y - 8)], fill=SEPARATOR)

    footer_font = load_font(16)
    draw_text("Generated with infographic-gen skill", 80, footer_y + 10, footer_font, TEXT_DIM)

    # Save
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    img.save(output_path, "PNG", quality=95)
    print(f"Saved to {output_path}")
    return output_path


def interactive_mode():
    """Interactive CLI mode."""
    print("=== Infographic Generator ===\n")

    title = input("Title: ").strip() or "Infographic"
    subtitle = input("Subtitle (optional): ").strip()
    theme = input("Theme (modern/dark) [modern]: ").strip() or "modern"

    print("\nEnter items (label: description), one per line.")
    print("Press Enter twice to finish.\n")

    items = {}
    current_category = "Category 1"
    items[current_category] = []

    while True:
        line = input(f"{current_category} item: ").strip()
        if not line:
            if items[current_category]:
                # Check if want to add another category
                more = input("Add another category? (y/n): ").strip().lower()
                if more == 'y':
                    cat_num = len(items) + 1
                    current_category = f"Category {cat_num}"
                    items[current_category] = []
                    print(f"\nNew category: {current_category}")
                    continue
            break

        if ':' in line:
            label, desc = line.split(':', 1)
            label, desc = label.strip(), desc.strip()
        else:
            label, desc = line, ""

        items[current_category].append((label, desc))

    output = input("\nOutput file [infographic.png]: ").strip() or "infographic.png"

    create_infographic(
        title=title,
        subtitle=subtitle,
        items=items,
        theme=theme,
        output_path=output
    )


def main():
    parser = argparse.ArgumentParser(description="Create professional infographics")
    parser.add_argument("--title", "-t", help="Main title")
    parser.add_argument("--subtitle", "-s", help="Subtitle text")
    parser.add_argument("--data", "-d", help="Pipe-separated items (Key:Val|Key2:Val2)")
    parser.add_argument("--theme", default="modern", choices=["modern", "dark"], help="Visual theme")
    parser.add_argument("--accent", "-a", help="Accent color (hex without #)")
    parser.add_argument("--output", "-o", default="infographic.png", help="Output file path")
    parser.add_argument("--interactive", "-i", action="store_true", help="Interactive mode")
    parser.add_argument("--width", "-w", type=int, default=1920, help="Image width")
    parser.add_argument("--height", "-H", type=int, default=1080, help="Image height")

    args = parser.parse_args()

    if args.interactive:
        interactive_mode()
        return

    if not args.title:
        print("Error: --title is required (or use --interactive)")
        parser.print_help()
        sys.exit(1)

    items = {}
    if args.data:
        for item in args.data.split('|'):
            if ':' in item:
                key, val = item.split(':', 1)
                items[key.strip()] = [(key.strip(), val.strip())]
            else:
                items[f"Item {len(items)+1}"] = [(item.strip(), "")]

    create_infographic(
        title=args.title,
        subtitle=args.subtitle or "",
        items=items,
        theme=args.theme,
        accent_color=args.accent,
        output_path=args.output,
        width=args.width,
        height=args.height
    )


if __name__ == "__main__":
    main()