import os

# True pixel art SVG definitions (pixel grid paths using rects)
icons = {
    "overview": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="{color}">
<rect x="7" y="1" width="2" height="2"/>
<rect x="5" y="3" width="2" height="2"/>
<rect x="9" y="3" width="2" height="2"/>
<rect x="3" y="5" width="2" height="2"/>
<rect x="11" y="5" width="2" height="2"/>
<rect x="1" y="7" width="2" height="2"/>
<rect x="13" y="7" width="2" height="2"/>
<rect x="1" y="9" width="2" height="6"/>
<rect x="13" y="9" width="2" height="6"/>
<rect x="3" y="13" width="10" height="2"/>
<rect x="7" y="9" width="2" height="4"/>
</svg>""",
    "visualizer": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="{color}">
<rect x="1" y="7" width="2" height="2"/>
<rect x="3" y="5" width="2" height="6"/>
<rect x="5" y="1" width="2" height="14"/>
<rect x="7" y="7" width="2" height="2"/>
<rect x="9" y="3" width="2" height="10"/>
<rect x="11" y="6" width="2" height="4"/>
<rect x="13" y="7" width="2" height="2"/>
</svg>""",
    "history": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="{color}">
<rect x="2" y="2" width="12" height="2"/>
<rect x="2" y="12" width="12" height="2"/>
<rect x="2" y="4" width="2" height="8"/>
<rect x="12" y="4" width="2" height="8"/>
<rect x="7" y="4" width="2" height="5"/>
<rect x="9" y="7" width="3" height="2"/>
</svg>""",
    "settings": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="{color}">
<rect x="7" y="1" width="2" height="3"/>
<rect x="7" y="12" width="2" height="3"/>
<rect x="1" y="7" width="3" height="2"/>
<rect x="12" y="7" width="3" height="2"/>
<rect x="5" y="5" width="6" height="2"/>
<rect x="5" y="9" width="6" height="2"/>
<rect x="5" y="7" width="2" height="2"/>
<rect x="9" y="7" width="2" height="2"/>
</svg>"""
}

color_active = "#F0F0F5"

assets_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")

for name, template in icons.items():
    filename = f"nav_{name}_active.svg"
    filepath = os.path.join(assets_dir, filename)
    content = template.replace("{color}", color_active)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Generated {filename}")


