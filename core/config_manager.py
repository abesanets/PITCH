import json
import os

CONFIG_FILE = "config.json"

def load_config():
    defaults = {
        "stt_model": "gigaam-v3-e2e-rnnt",
        "corrections_path": "corrections.json",
        "hotkey_1": "ctrl+windows",
        "mode_1": "default",
        "hotkey_2_enabled": False,
        "hotkey_2": "shift+windows",
        "mode_2": "translate_en",
        "theme": "dark",
        "run_on_startup": False,
        "visualizer_style": "wave",
        "visualizer_color_preset": "emerald",
        "visualizer_size": "medium",
        "visualizer_sensitivity": 1.0,
        "min_recording_duration": 0.4,
    }
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                config = json.load(f)
                config.pop("hotkey_command", None)
                for legacy_key in ("api_key", "groq_base_url", "use_raw_whisper", "whisper_model", "text_model", "formatting_style", "custom_formatting_style", "hotkey"):
                    config.pop(legacy_key, None)
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
