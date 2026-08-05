import sys
import os


def is_startup_enabled(app_name: str = "PITCHVoiceAssistant") -> bool:
    """Check if the application is currently registered in Windows Startup registry."""
    if sys.platform != "win32":
        return False
    import winreg
    key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_READ)
        _, _ = winreg.QueryValueEx(key, app_name)
        winreg.CloseKey(key)
        return True
    except Exception:
        return False


def sync_startup_config(config: dict) -> dict:
    """Synchronize the config's run_on_startup state with Windows Registry."""
    if sys.platform == "win32":
        config["run_on_startup"] = is_startup_enabled()
    return config


def update_startup_registry(enabled: bool, app_name: str = "PITCHVoiceAssistant") -> None:
    """
    Registers or deletes the application from the Windows startup registry.
    Only works on Windows; no-op on other platforms.
    """
    if sys.platform != "win32":
        return

    import winreg
    key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"

    # Determine executable path
    if getattr(sys, 'frozen', False):
        exe_path = f'"{sys.executable}"'
    else:
        script_path = os.path.abspath(sys.argv[0])
        exe_path = f'"{sys.executable}" "{script_path}"'

    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_ALL_ACCESS)
        if enabled:
            winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, exe_path)
            print(f"Registry: registered {app_name} at {exe_path} for startup")
        else:
            try:
                winreg.DeleteValue(key, app_name)
                print(f"Registry: unregistered {app_name} from startup")
            except FileNotFoundError:
                pass
        winreg.CloseKey(key)
    except Exception as e:
        print(f"Registry: error updating startup: {e}")
