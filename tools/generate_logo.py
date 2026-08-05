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

    # Load cursive font
    font_path = r"C:\Windows\Fonts\segoescb.ttf"  # Segoe Script Bold
    if not os.path.exists(font_path):
        font_path = r"C:\Windows\Fonts\segoesc.ttf"
    
    if os.path.exists(font_path):
        font_size = 1000
        font = ImageFont.truetype(font_path, font_size)
        
        # Render P on temp canvas
        draw.text(
            (250, 250), 
            "P", 
            fill=text_color, 
            font=font, 
            stroke_width=32, 
            stroke_fill=stroke_color
        )
    else:
        # Fallback if cursive font is missing
        print("Warning: Cursive font not found. Using custom curves fallback.")
        # Drawing a geometric white "P" with dark brown stroke
        draw.ellipse([300, 220, 720, 560], fill=stroke_color)
        draw.ellipse([340, 260, 680, 520], fill=text_color)
        draw.ellipse([420, 320, 600, 460], fill=stroke_color)
        draw.ellipse([460, 360, 560, 420], fill=transparent)
        draw.rounded_rect([300, 220, 420, 800], radius=30, fill=stroke_color)
        draw.rounded_rect([330, 250, 390, 770], radius=15, fill=text_color)

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
