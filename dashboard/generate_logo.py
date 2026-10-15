"""
Generate high-fidelity NetTelemetry logo assets (PNG and SVG).
Production-grade NOC observability branding.
"""

import os
from PIL import Image, ImageDraw

def generate_logo_png(output_path: str, size: int = 128):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # 4x supersampling for ultra-crisp antialiasing
    scale = 4
    canvas_size = size * scale
    img = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Colors
    bg_color = (13, 46, 50, 255)       # #0D2E32
    border_color = (20, 184, 166, 255) # #14B8A6
    line_dim = (19, 78, 74, 180)       # #134E4A
    wave_color = (45, 212, 191, 255)   # #2DD4BF
    node1_color = (20, 184, 166, 255)  # #14B8A6
    node2_color = (16, 185, 129, 255)  # #10B981
    node3_color = (52, 211, 153, 255)  # #34D399
    node_border = (11, 31, 36, 255)    # #0B1F24
    
    # Rounded squircle background
    pad = 4 * scale
    radius = 28 * scale
    draw.rounded_rectangle(
        [pad, pad, canvas_size - pad, canvas_size - pad],
        radius=radius,
        fill=bg_color,
        outline=border_color,
        width=int(4.5 * scale)
    )
    
    # Center datum dashed line (y = canvas_size / 2)
    cy = canvas_size / 2
    dash_len = 8 * scale
    gap_len = 6 * scale
    x = 18 * scale
    x_end = canvas_size - (18 * scale)
    while x < x_end:
        draw.line([(x, cy), (min(x + dash_len, x_end), cy)], fill=line_dim, width=int(2 * scale))
        x += dash_len + gap_len
        
    # Telemetry pulse waveform points (normalized to 128, scaled by `scale`)
    raw_points = [
        (18, 64),
        (34, 64),
        (48, 30),
        (64, 96),
        (80, 42),
        (94, 64),
        (110, 64)
    ]
    scaled_points = [(p[0] * scale, p[1] * scale) for p in raw_points]
    
    # Draw waveform path
    for i in range(len(scaled_points) - 1):
        draw.line([scaled_points[i], scaled_points[i+1]], fill=wave_color, width=int(6 * scale))
        
    # Draw connected nodes
    nodes = [
        (scaled_points[2], 8.5 * scale, node1_color),  # Peak 1
        (scaled_points[3], 8.5 * scale, node2_color),  # Trough
        (scaled_points[4], 7.0 * scale, node3_color),  # Peak 2
    ]
    
    for (nx, ny), r, col in nodes:
        draw.ellipse([nx - r, ny - r, nx + r, ny + r], fill=col, outline=node_border, width=int(3 * scale))
        
    # Downsample with Lanczos filter for perfectly smooth antialiasing
    final_img = img.resize((size, size), Image.Resampling.LANCZOS)
    final_img.save(output_path, "PNG")
    print(f"Generated {output_path} ({size}x{size})")

def generate_logo_svg(output_path: str):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    svg_content = """<svg width="36" height="36" viewBox="0 0 36 36" fill="none" xmlns="http://www.w3.org/2000/svg">
  <rect width="36" height="36" rx="9" fill="#0D2E32" stroke="#14B8A6" stroke-width="1.5"/>
  <line x1="5" y1="18" x2="31" y2="18" stroke="#134E4A" stroke-width="1.2" stroke-dasharray="2 2"/>
  <polyline points="6,18 10,18 14,9 18.5,27 23,12 26.5,18 30,18" fill="none" stroke="#2DD4BF" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>
  <circle cx="14" cy="9" r="2.4" fill="#14B8A6" stroke="#0B1F24" stroke-width="1.4"/>
  <circle cx="18.5" cy="27" r="2.4" fill="#10B981" stroke="#0B1F24" stroke-width="1.4"/>
  <circle cx="23" cy="12" r="2" fill="#34D399" stroke="#0B1F24" stroke-width="1.2"/>
</svg>"""
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg_content.strip())
    print(f"Generated {output_path}")

def generate_pulse_png(output_path: str, size: int = 48):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    scale = 4
    canvas_size = size * scale
    img = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    teal = (20, 184, 166, 255) # #14B8A6
    
    # Waveform points (polyline points='22 12 18 12 15 21 9 3 6 12 2 12' scaled to 48x48)
    norm_pts = [
        (4, 24),
        (12, 24),
        (18, 6),
        (30, 42),
        (36, 24),
        (44, 24)
    ]
    scaled_pts = [(p[0] * scale, p[1] * scale) for p in norm_pts]
    for i in range(len(scaled_pts) - 1):
        draw.line([scaled_pts[i], scaled_pts[i+1]], fill=teal, width=int(4 * scale))
        
    final_img = img.resize((size, size), Image.Resampling.LANCZOS)
    final_img.save(output_path, "PNG")
    print(f"Generated {output_path} ({size}x{size})")

if __name__ == "__main__":
    base_dir = os.path.dirname(__file__)
    generate_logo_png(os.path.join(base_dir, "assets", "logo.png"), 128)
    generate_logo_svg(os.path.join(base_dir, "assets", "logo.svg"))
    generate_pulse_png(os.path.join(base_dir, "assets", "pulse.png"), 48)
