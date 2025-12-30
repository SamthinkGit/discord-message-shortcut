import sys
import os


def resource_path(relative_path: str) -> str:
    """
    Get absolute path to resource, works for dev and for PyInstaller exe.
    """
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


def main():
    from discord_message_shortcut.ui import DmsUI
    from discord_message_shortcut.dms_manager import DMS_Manager

    manager = DMS_Manager(app_name="DMS")
    ui = DmsUI(manager=manager, icon_path=resource_path("resources/dms_icon.png"))
    ui.run()


if __name__ == "__main__":
    # Careful: This code will add the application to Windows startup!
    # It is used here for installation convenience for the user.
    # If you want to use this application in development mode you can use
    #
    # >> uv run discord_message_shortcut
    from pathlib import Path
    import win32com.client  # pip install pywin32

    def add_to_startup(app_name: str) -> None:
        startup_dir = (
            Path(os.getenv("APPDATA"))
            / r"Microsoft\Windows\Start Menu\Programs\Startup"
        )
        exe_path = Path(sys.executable)

        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut_path = startup_dir / f"{app_name}.lnk"

        shortcut = shell.CreateShortcut(str(shortcut_path))
        shortcut.TargetPath = str(exe_path)
        shortcut.WorkingDirectory = str(exe_path.parent)
        shortcut.IconLocation = str(exe_path)
        shortcut.save()

    add_to_startup("Discord Messsage Shortcut (DMS)")
    main()
