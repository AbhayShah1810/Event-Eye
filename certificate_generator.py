import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import qrcode
import os
import uuid

# --- CONFIGURATION (User adjustable) ---
# --- CONFIGURATION (User adjustable) ---
CERT_TEMPLATE_PATH = "assets/base_certificate.png"
NAME_FONT_PATH = "arial.ttf"  # Ensure available on system or replace with a path
NAME_COLOR = (0, 0, 0, 255)  # Black color for the name (RGBA)

# 1. Name Placement (On the underline)
# X coordinate is placeholder for centering logic in the script.
# Y coordinate places the name just above the underline.
NAME_POSITION = (500, 310)
NAME_FONT_SIZE = 45          # Adjusted for good visibility over the underline

# 2. QR Code Placement (Between "GeeksforGeeks" and "EventEye" logos)
# This places the QR code roughly centered in the top half of the certificate.
QR_POSITION = (450, 150)    
QR_SIZE = (120, 120)        # Size of the QR code image

def _resolve_template_path() -> str:
    """Return an existing certificate template path. Prefer configured path, else any PNG/JPG in assets."""
    if os.path.exists(CERT_TEMPLATE_PATH):
        return CERT_TEMPLATE_PATH
    assets_dir = "assets"
    if not os.path.isdir(assets_dir):
        raise FileNotFoundError("assets/ directory not found. Place a template image in assets/.")
    for fname in os.listdir(assets_dir):
        lower = fname.lower()
        if lower.endswith((".png", ".jpg", ".jpeg")):
            return os.path.join(assets_dir, fname)
    raise FileNotFoundError("No template image found in assets/. Expected a PNG/JPG.")


def generate_certificate(name: str, unique_id: str, event_name: str = "EventEye Hackathon", date: str = "Oct 2025") -> str | None:
    """Generate a personalized certificate saved as PDF and return its path."""
    try:
        # Generate QR Code for authenticity
        verification_link = f"https://eventeye-verify.com/check?id={unique_id}"
        qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=5, border=4)
        qr.add_data(verification_link)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white").convert("RGBA")
        qr_img = qr_img.resize(QR_SIZE)

        # Load template and draw text/QR
        template_path = _resolve_template_path()
        img = Image.open(template_path).convert("RGBA")
        draw = ImageDraw.Draw(img)
        try:
            font = ImageFont.truetype(NAME_FONT_PATH, NAME_FONT_SIZE)
        except Exception:
            # Fallback to default font if TTF not found
            font = ImageFont.load_default()

        # Center the name horizontally
        bbox = draw.textbbox(NAME_POSITION, name, font=font)
        text_width = bbox[2] - bbox[0]
        centered_x = NAME_POSITION[0] - (text_width / 2)

        # Draw name
        draw.text((centered_x, NAME_POSITION[1]), name, font=font, fill=(0, 0, 0, 255))

        # Overlay QR code
        img.paste(qr_img, QR_POSITION, qr_img)

        # Save as PDF (must be RGB for PDF)
        if not os.path.exists("certs"):
            os.makedirs("certs")
        output_filename = f"certs/{unique_id}_{name.replace(' ', '_')}.pdf"
        img_rgb = img.convert("RGB")
        img_rgb.save(output_filename, "PDF", resolution=100.0)
        return output_filename
    except Exception as e:
        print(f"Error generating certificate for {name}: {e}")
        return None


def process_participants(csv_filepath: str):
    """Read CSV, validate names, generate certificates. Returns a DataFrame of results."""
    if not os.path.exists("certs"):
        os.makedirs("certs")

    df = pandas.read_csv(csv_filepath) if False else pd.read_csv(csv_filepath)
    results: list[dict] = []

    for index, row in df.iterrows():
        name = str(row.get("name", "Participant")).strip()
        email = str(row.get("email", "")).strip()

        # Basic "AI" name verification
        if not name or len(name) < 3 or any(char.isdigit() for char in name):
            print(f"Skipping row {index}: Name '{name}' failed basic verification.")
            results.append({"name": name, "email": email, "status": "Verification Failed", "filepath": None})
            continue

        unique_id = str(uuid.uuid4())[:8]
        filepath = generate_certificate(name, unique_id)

        results.append({
            "name": name,
            "email": email,
            "status": "Generated" if filepath else "Generation Failed",
            "filepath": filepath,
            "unique_id": unique_id,
        })

    return pd.DataFrame(results)


if __name__ == "__main__":
    pass


