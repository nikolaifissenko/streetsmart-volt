from PIL import Image, ImageDraw
import math

def draw_icon(size):
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx, cy = size / 2, size / 2

    # Background rounded rect
    pad = int(size * 0.05)
    radius = int(size * 0.18)
    d.rounded_rectangle([pad, pad, size - pad, size - pad], radius=radius, fill=(237, 232, 223, 255))

    # Outer circle
    r_outer = int(size * 0.36)
    sw = max(2, int(size * 0.04))
    d.ellipse([cx - r_outer, cy - r_outer, cx + r_outer, cy + r_outer], outline=(58, 53, 48, 255), width=sw)

    # Compass lines
    line_w = max(1, int(size * 0.025))
    angles = [0, 60, 120, 180, 240, 300]
    r_line = int(size * 0.32)
    for a_deg in angles:
        a = math.radians(a_deg - 90)
        ex = cx + r_line * math.cos(a)
        ey = cy + r_line * math.sin(a)
        d.line([(cx, cy), (ex, ey)], fill=(58, 53, 48, 255), width=line_w)

    # Center dot
    r_center = int(size * 0.055)
    d.ellipse([cx - r_center, cy - r_center, cx + r_center, cy + r_center], fill=(58, 53, 48, 255))

    # North star (green)
    star_y = cy - r_outer + int(size * 0.02)
    star_size = int(size * 0.1)
    star_points = []
    for i in range(10):
        a = math.radians(i * 36 - 90)
        r = star_size if i % 2 == 0 else star_size * 0.4
        star_points.append((cx + r * math.cos(a), star_y + r * math.sin(a)))
    d.polygon(star_points, fill=(39, 174, 96, 255))

    return img

for s in [192, 512]:
    img = draw_icon(s)
    img.save(f'/home/user/streetsmart-volt/icon-{s}.png')
    print(f'icon-{s}.png created')
