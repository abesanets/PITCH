import os

icons = {
    "overview": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="square" stroke-linejoin="miter"><path d="M12 3 L3 10 V21 H21 V10 Z"/><rect x="9" y="14" width="6" height="7"/></svg>""",
    "visualizer": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="square" stroke-linejoin="miter"><path d="M2 12 H6 V5 H10 V19 H14 V9 H18 V15 H22"/></svg>""",
    "history": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="square" stroke-linejoin="miter"><rect x="3" y="3" width="18" height="18"/><path d="M12 7 V12 H16"/></svg>""",
    "settings": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="square" stroke-linejoin="miter"><rect x="7" y="7" width="10" height="10"/><rect x="10" y="2" width="4" height="5"/><rect x="10" y="17" width="4" height="5"/><rect x="2" y="10" width="5" height="4"/><rect x="17" y="10" width="5" height="4"/></svg>""",
    "predict": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="square" stroke-linejoin="miter"><rect x="8" y="3" width="8" height="11"/><path d="M5 10 V14 H19 V10 M12 14 V21 M8 21 H16"/></svg>"""
}

# Only active icons are used in the application layout
color_active = "#F0F0F5"

assets_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")

for name, template in icons.items():
    filename = f"nav_{name}_active.svg"
    filepath = os.path.join(assets_dir, filename)
    content = template.replace("{color}", color_active)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Generated {filename}")

