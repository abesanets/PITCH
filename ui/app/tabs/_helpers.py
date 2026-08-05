"""Shared helper functions for dashboard tabs."""

def update_hotkey_badge(d) -> None:
    """Update the hotkey badge label on the Overview tab."""
    h1 = d.config.get("hotkey_1", "ctrl+windows").upper()
    if hasattr(d, "hotkey_badge") and d.hotkey_badge:
        d.hotkey_badge.setText(h1)
