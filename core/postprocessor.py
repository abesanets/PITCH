import json
import os
from rapidfuzz import process, utils


class TermPostprocessor:
    def __init__(self, corrections_path="corrections.json", match_cutoff=85.0):
        self.match_cutoff = match_cutoff
        self.corrections_path = corrections_path
        self.corrections = {}
        self.reload()

    def reload(self):
        if os.path.exists(self.corrections_path):
            try:
                with open(self.corrections_path, "r", encoding="utf-8") as f:
                    self.corrections = json.load(f)
            except Exception as e:
                print(f"[Postprocessor] Error loading corrections.json: {e}")
                self.corrections = {}
        else:
            self.corrections = {}

    def process_text(self, text: str) -> str:
        if not text or not self.corrections:
            return text

        words = text.split()
        processed_words = []

        for word in words:
            clean_word = word.strip(",.?!;:\"'()[]{}")
            punct_suffix = word[len(clean_word.rstrip()) :] if clean_word else ""
            punct_prefix = word[: len(word) - len(word.lstrip(",.?!;:\"'()[]{}"))]

            key = clean_word.lower()
            if key in self.corrections:
                replacement = self.corrections[key]
                processed_words.append(punct_prefix + replacement + punct_suffix)
            elif len(key) >= 4:
                match = process.extractOne(
                    key,
                    self.corrections.keys(),
                    processor=utils.default_process,
                    score_cutoff=self.match_cutoff,
                )
                if match:
                    matched_key = match[0]
                    replacement = self.corrections[matched_key]
                    processed_words.append(punct_prefix + replacement + punct_suffix)
                else:
                    processed_words.append(word)
            else:
                processed_words.append(word)

        return " ".join(processed_words)
