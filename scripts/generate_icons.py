"""Generate PWA icons from logo.png in the repo root."""
from PIL import Image
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
logo = Image.open(os.path.join(ROOT, "logo.png")).convert("RGBA")

os.makedirs(os.path.join(ROOT, "icons"), exist_ok=True)

for size in [192, 512]:
    icon = logo.resize((size, size), Image.LANCZOS)
    icon.save(os.path.join(ROOT, "icons", f"icon-{size}.png"))
    print(f"Created icons/icon-{size}.png ({size}x{size})")

print("Done. Commit and push to update the PWA icons.")
