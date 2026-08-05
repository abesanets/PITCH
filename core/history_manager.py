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
                    # Filter out any entries with empty/whitespace-only cleaned_text
                    filtered = [entry for entry in data if entry.get("cleaned_text", "").strip()]
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

def add_history_entry(model, raw_text, cleaned_text, whisper_latency, llm_latency):
    if not cleaned_text or not cleaned_text.strip():
        return None

    history = load_history()
    
    # Calculate word and character count
    word_count = len(cleaned_text.split())
    char_count = len(cleaned_text)
    
    entry = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "model": model,
        "raw_text": raw_text.strip(),
        "cleaned_text": cleaned_text.strip(),
        "whisper_latency": round(whisper_latency, 2),
        "llm_latency": round(llm_latency, 2),
        "total_latency": round(whisper_latency + llm_latency, 2),
        "word_count": word_count,
        "char_count": char_count
    }
    
    history.insert(0, entry)  # Prepend new entry
    history = history[:MAX_HISTORY_ENTRIES]  # Cap size
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
            "avg_whisper_latency": 0.0,
            "avg_llm_latency": 0.0,
            "avg_total_latency": 0.0,
            "total_words": 0,
            "total_chars": 0
        }
        
    total_whisper_lat = sum(e.get("whisper_latency", 0.0) for e in history)
    total_llm_lat = sum(e.get("llm_latency", 0.0) for e in history)
    total_total_lat = sum(e.get("total_latency", 0.0) for e in history)
    total_words = sum(e.get("word_count", 0) for e in history)
    total_chars = sum(e.get("char_count", 0) for e in history)
    
    return {
        "total_dictations": total_dictations,
        "avg_whisper_latency": round(total_whisper_lat / total_dictations, 2),
        "avg_llm_latency": round(total_llm_lat / total_dictations, 2),
        "avg_total_latency": round(total_total_lat / total_dictations, 2),
        "total_words": total_words,
        "total_chars": total_chars
    }
