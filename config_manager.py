import json
import os

CONFIG_FILE = "config.json"

def load_config():
    defaults = {
        "api_key": "", 
        "hotkey": "ctrl+windows",
        "text_model": "llama-3.3-70b-versatile",
        "theme": "dark",
        "run_on_startup": False,
        "visualizer_style": "wave",
        "visualizer_color_preset": "emerald",
        "visualizer_size": "medium",
        "visualizer_sensitivity": 1.0,
        "use_raw_whisper": False,
    }
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                config = json.load(f)
                config.pop("hotkey_command", None)
                if config.get("visualizer_style") in ("pulse", "dots", "ribbon"):
                    config["visualizer_style"] = "wave"
                for k, v in defaults.items():
                    if k not in config:
                        config[k] = v
                return config
        except Exception:
            pass
    return defaults

def save_config(config):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4)
