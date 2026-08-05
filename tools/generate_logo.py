import os
from PIL import Image, ImageDraw, ImageFont

def generate_branding_assets():
    # Colors matching the request and app theme
    text_color = (255, 255, 255, 255)     # White
    stroke_color = (40, 27, 21, 255)      # #281B15 (Dark Brown outline)
    transparent = (0, 0, 0, 0)

    # Use a large temp canvas to render text/graphics
    temp_size = 1500
    temp_img = Image.new("RGBA", (temp_size, temp_size), transparent)
    draw = ImageDraw.Draw(temp_img)

    # Draw 5x7 Pixel Art letter P
    pixel_matrix_p = [
        [1, 1, 1, 1, 0],
        [1, 0, 0, 0, 1],
        [1, 0, 0, 0, 1],
        [1, 1, 1, 1, 0],
        [1, 0, 0, 0, 0],
        [1, 0, 0, 0, 0],
        [1, 0, 0, 0, 0],
    ]
    
    px_size = 140
    gap = 20
    start_x = (temp_size - (5 * (px_size + gap))) // 2
    start_y = (temp_size - (7 * (px_size + gap))) // 2

    for r, row in enumerate(pixel_matrix_p):
        for c, val in enumerate(row):
            if val == 1:
                x0 = start_x + c * (px_size + gap)
                y0 = start_y + r * (px_size + gap)
                x1 = x0 + px_size
                y1 = y0 + px_size
                draw.rectangle([x0, y0, x1, y1], fill=(240, 240, 245, 255))


    # Auto-crop the bounding box of non-transparent content to maximize scale
    bbox = temp_img.getbbox()
    if bbox:
        cropped = temp_img.crop(bbox)
        w, h = cropped.size
        
        # Scale to fit inside render_size (1024) with a tiny safety margin (4%)
        render_size = 1024
        target_content_size = int(render_size * 0.96) # 96% fill factor (minimal padding)
        
        scale = target_content_size / max(w, h)
        new_w = int(w * scale)
        new_h = int(h * scale)
        
        resized = cropped.resize((new_w, new_h), Image.Resampling.LANCZOS)
        
        # Create final high-res square canvas
        img = Image.new("RGBA", (render_size, render_size), transparent)
        # Center the resized graphic
        x = (render_size - new_w) // 2
        y = (render_size - new_h) // 2
        img.paste(resized, (x, y), resized)
        print("Successfully auto-cropped and maximized the letter scale.")
    else:
        img = temp_img.resize((1024, 1024), Image.Resampling.LANCZOS)

    # Downsample using LANCZOS filter for smooth anti-aliased edges
    output_size = 256
    logo_png = img.resize((output_size, output_size), Image.Resampling.LANCZOS)

    # Make sure output directories exist
    assets_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")
    os.makedirs(assets_dir, exist_ok=True)
    
    # Save the application icon PNG
    png_path = os.path.join(assets_dir, "p.png")
    logo_png.save(png_path, "PNG")
    print(f"Successfully generated transparent PNG at: {png_path}")

    # Generate multi-size ICO file for Windows binary
    ico_sizes = [16, 32, 48, 64, 128, 256]
    ico_images = []
    for size in ico_sizes:
        ico_images.append(img.resize((size, size), Image.Resampling.LANCZOS))
    
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ico_path = os.path.join(project_root, "icon.ico")
    ico_images[0].save(
        ico_path,
        format="ICO",
        sizes=[(size, size) for size in ico_sizes],
        append_images=ico_images[1:]
    )
    print(f"Successfully generated multi-size ICO at: {ico_path}")

if __name__ == "__main__":
    generate_branding_assets()
