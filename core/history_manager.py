import json
import os
import time

HISTORY_FILE = "history.json"
MAX_HISTORY_ENTRIES = 100

def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    filtered = [
                        entry for entry in data
                        if (entry.get("cleaned_text") or entry.get("text") or "").strip()
                    ]
                    if len(filtered) != len(data):
                        save_history(filtered)
                    return filtered
        except Exception:
            pass
    return []

def save_history(history):
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving history: {e}")

def add_history_entry(model: str, text: str, stt_latency: float, rtf: float = 0.0, audio_duration: float = 0.0):
    if not text or not text.strip():
        return None

    history = load_history()
    cleaned = text.strip()
    word_count = len(cleaned.split())
    char_count = len(cleaned)
    stt_lat = round(stt_latency, 2)

    entry = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "model": model,
        "raw_text": cleaned,
        "cleaned_text": cleaned,
        "stt_latency": stt_lat,
        "total_latency": stt_lat,
        "audio_duration": round(audio_duration, 2),
        "rtf": round(rtf, 3),
        "word_count": word_count,
        "char_count": char_count
    }

    history.insert(0, entry)
    history = history[:MAX_HISTORY_ENTRIES]
    save_history(history)
    return entry

def clear_history():
    if os.path.exists(HISTORY_FILE):
        try:
            os.remove(HISTORY_FILE)
        except Exception:
            pass

def get_statistics():
    history = load_history()
    total_dictations = len(history)

    if total_dictations == 0:
        return {
            "total_dictations": 0,
            "avg_stt_latency": 0.0,
            "avg_total_latency": 0.0,
            "avg_rtf": 0.05,
            "total_words": 0,
            "total_chars": 0
        }

    total_stt_lat = sum(e.get("stt_latency", e.get("whisper_latency", 0.0)) for e in history)
    total_total_lat = sum(e.get("total_latency", 0.0) for e in history)
    total_words = sum(e.get("word_count", 0) for e in history)
    total_chars = sum(e.get("char_count", 0) for e in history)

    valid_rtf_entries = [e.get("rtf") for e in history if e.get("rtf") is not None and e.get("rtf") > 0]
    avg_rtf = round(sum(valid_rtf_entries) / len(valid_rtf_entries), 2) if valid_rtf_entries else 0.05

    return {
        "total_dictations": total_dictations,
        "avg_stt_latency": round(total_stt_lat / total_dictations, 2),
        "avg_total_latency": round(total_total_lat / total_dictations, 2),
        "avg_rtf": avg_rtf,
        "total_words": total_words,
        "total_chars": total_chars
    }
