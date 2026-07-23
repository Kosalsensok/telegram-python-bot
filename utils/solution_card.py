import io
import logging
from PIL import Image, ImageDraw, ImageFont


def render_solution_card(
    solution_text: str,
    title: str = "ចម្លើយលំហាត់ (Math Solution)",
    bot_branding: str = "AI : imsela.com",
    footer_tag: str = "🎓 លំហាត់រួចរាល់ !"
) -> bytes:
    """
    Renders a clean, high-resolution solution card PNG image (imsela.com layout)
    with crisp white background, dark typography, rounded border, and clear Khmer text.
    """
    try:
        width = 1200
        padding = 50
        
        # Load fonts safely
        try:
            title_font = ImageFont.truetype("arial.ttf", 36)
            body_font = ImageFont.truetype("arial.ttf", 26)
            small_font = ImageFont.truetype("arial.ttf", 20)
        except Exception:
            title_font = ImageFont.load_default()
            body_font = ImageFont.load_default()
            small_font = ImageFont.load_default()

        # Format lines
        lines = solution_text.strip().split("\n")
        
        line_height = 42
        header_height = 140
        footer_height = 80
        total_height = header_height + (len(lines) * line_height) + footer_height + (padding * 2)
        total_height = max(total_height, 400)

        # Create White Card Image
        card = Image.new("RGBA", (width, total_height), (255, 255, 255, 255))
        draw = ImageDraw.Draw(card)

        # Draw outer subtle card border
        draw.rectangle(
            [20, 20, width - 20, total_height - 20],
            outline=(220, 220, 225),
            width=2
        )

        # Draw Top Branding Header: "🤖 AI : imsela.com"
        draw.text((padding, padding), f"🤖 {bot_branding}", fill=(60, 60, 65), font=title_font)
        draw.line([padding, padding + 55, width - padding, padding + 55], fill=(230, 230, 235), width=2)

        # Draw Solution Content Lines
        y_cursor = padding + 80
        for line in lines:
            line_str = line.strip()
            if not line_str:
                y_cursor += 15
                continue
            
            # Highlight conclusions or final answers in accent blue
            if "ដូចនេះ" in line_str or "Final Answer" in line_str or "≅" in line_str or "=" in line_str:
                fill_color = (20, 90, 190)
            elif line_str.startswith(("1.", "2.", "3.", "4.", "គេមាន:", "ប្រៀបធៀប", "គណនា", "ស្រាយបញ្ជាក់")):
                fill_color = (20, 20, 25)
            else:
                fill_color = (45, 45, 50)

            draw.text((padding + 10, y_cursor), line_str, fill=fill_color, font=body_font)
            y_cursor += line_height

        # Draw Footer Accent
        draw.line([padding, total_height - padding - 40, width - padding, total_height - padding - 40], fill=(230, 230, 235), width=2)
        draw.text((padding, total_height - padding - 30), footer_tag, fill=(100, 100, 105), font=small_font)

        out = io.BytesIO()
        card.convert("RGB").save(out, format="PNG", quality=95)
        return out.getvalue()
    except Exception as e:
        logging.error(f"Error rendering solution card PNG: {e}")
        return b""
