# backend.py
import fitz  # PyMuPDF
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps
import io
import os
import time
import random

# ---------------- Silent Backend Flags ----------------
ENABLE_SUBUI = True
INCLUDE_SYNONYMS = True
INITIAL_READING_PROGRESS = 0.03  # Reserved for future logic

# ---------------- Hand-Drawn Line ----------------
def draw_hand_line(draw, x0, y0, x1, y1, jitter=True):
    if jitter:
        jitter_val = lambda v: v + random.randint(-2, 2)
        draw.line([jitter_val(x0), jitter_val(y0), jitter_val(x1), jitter_val(y1)], fill=(0, 0, 0), width=2)
    else:
        draw.line([x0, y0, x1, y1], fill=(0, 0, 0), width=2)

# ---------------- Sketch Filter ----------------
def convert_to_sketch(pil_img):
    gray = pil_img.convert("L")
    inverted = ImageOps.invert(gray)
    blur = inverted.filter(ImageFilter.GaussianBlur(5))
    sketch = ImageOps.invert(Image.blend(gray, blur, 0.5))
    return sketch.convert("RGB")

# ---------------- Handwriting Renderer ----------------
def draw_handwriting(draw, x, y, text, font_path, font_size, ink_intensity=20):
    try:
        font = ImageFont.truetype(font_path, font_size)
    except Exception:
        font = ImageFont.load_default()
    jitter_x = x + random.randint(-1, 1)
    jitter_y = y + random.randint(-1, 1)
    draw.text((jitter_x, jitter_y), text, font=font, fill=(0, 0, 0))
    if random.randint(0, 100) < ink_intensity:
        r = random.randint(1, 3)
        draw.ellipse((jitter_x, jitter_y, jitter_x + r, jitter_y + r), fill=(0, 0, 0))

# ---------------- Text Correction Layer ----------------
def correct_text(text):
    corrections = {
        "Shane": "Share", "khale": "Whole", "ba'": "ba", "Doing": "Doing",
        "stun": "stuff", "pang": "Doing", "canqul": "careful", "acting": "solving",
        "hining": "hiring", "stay": "stuff", "Danq": "Doing", "Anawch": "Answer"
    }
    for wrong, right in corrections.items():
        text = text.replace(wrong, right)
    return text

# ---------------- Shape Renderer ----------------
def draw_shape(draw, item, scale=1):
    try:
        shape_type, coords = item
        if shape_type == "l":
            x0, y0, x1, y1 = [int(c * scale) for c in coords]
            draw_hand_line(draw, x0, y0, x1, y1, jitter=False)
        elif shape_type == "re":
            x0, y0, w, h = [int(c * scale) for c in coords]
            draw.rectangle([x0, y0, x0 + w, y0 + h], outline=(0, 0, 0), width=2)
        elif shape_type == "poly":
            points = [(int(x * scale), int(y * scale)) for x, y in coords]
            draw.line(points, fill=(0, 0, 0), width=2)
        elif shape_type == "path":
            for segment in coords:
                if len(segment) == 2:
                    x0, y0 = [int(c * scale) for c in segment[0]]
                    x1, y1 = [int(c * scale) for c in segment[1]]
                    draw_hand_line(draw, x0, y0, x1, y1, jitter=False)
    except Exception:
        pass

# ---------------- Main Conversion Function ----------------
def process_pdf(digital_path, font_path, output_dir,
                enable_sketch=True, ink_intensity=30, include_diagrams=True):

    doc = fitz.open(digital_path)
    output_pages = []
    dpi_scale = 2  # High-resolution rendering

    for page_index, page in enumerate(doc):
        page_width = int(page.rect.width * dpi_scale)
        page_height = int(page.rect.height * dpi_scale)
        img = Image.new("RGB", (page_width, page_height), "white")
        draw = ImageDraw.Draw(img)

        # Render text blocks
        for block in page.get_text("dict")["blocks"]:
            if "lines" not in block:
                continue
            for line in block["lines"]:
                for span in line["spans"]:
                    text = span["text"]
                    if not text.strip():
                        continue
                    text = correct_text(text)
                    x0 = int(span["bbox"][0] * dpi_scale)
                    y0 = int(span["bbox"][1] * dpi_scale)
                    font_size = max(int(span["size"] * dpi_scale), 16)

                    # LaTeX-style formatting mimicry
                    if font_size > 30 or text.strip().endswith(":"):
                        draw_handwriting(draw, x0, y0, text.upper(), font_path, font_size + 4, ink_intensity)
                    elif text.strip().startswith(("-", "•", "1.", "2.", "3.")):
                        draw_handwriting(draw, x0 + 20, y0, text, font_path, font_size, ink_intensity)
                    else:
                        draw_handwriting(draw, x0, y0, text, font_path, font_size, ink_intensity)

        # Render diagrams and layout lines
        if include_diagrams:
            for d in page.get_drawings():
                for item in d["items"]:
                    draw_shape(draw, item, scale=dpi_scale)

        # Convert embedded images to sketch
        if enable_sketch:
            for img_info in page.get_images(full=True):
                try:
                    xref = img_info[0]
                    for rect in page.get_image_rects(xref):
                        x0, y0, x1, y1 = [int(v * dpi_scale) for v in rect]
                        base_image = doc.extract_image(xref)
                        image_bytes = base_image["image"]
                        pil_img = Image.open(io.BytesIO(image_bytes))
                        sketch_img = convert_to_sketch(pil_img).resize((x1 - x0, y1 - y0))
                        img.paste(sketch_img, (x0, y0))
                except Exception:
                    continue

        output_pages.append(img)

    # Save final PDF and individual pages
    timestamp = int(time.time())
    base_name = f"handwritten_{timestamp}"
    output_pdf = os.path.join(output_dir, f"{base_name}.pdf")
    output_pages[0].save(output_pdf, save_all=True, append_images=output_pages[1:])

    for i, page_img in enumerate(output_pages):
        page_img.save(os.path.join(output_dir, f"{base_name}_{i}.png"), format="PNG")
        page_img.convert("RGB").save(os.path.join(output_dir, f"{base_name}_{i}.jpg"), format="JPEG")

    return output_pdf, output_pages