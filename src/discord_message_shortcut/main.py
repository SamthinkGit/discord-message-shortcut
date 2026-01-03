import sys
import os
import multiprocessing


def resource_path(relative_path: str) -> str:
    """
    Get absolute path to resource, works for dev and for PyInstaller exe.
    """
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


def app_entry(autostart: bool = False) -> None:
    from discord_message_shortcut.ui import DmsUI
    from discord_message_shortcut.dms_manager import DMS_Manager
    from discord_message_shortcut.main import resource_path

    manager = DMS_Manager(app_name="DMS")
    ui = DmsUI(manager=manager, icon_path=resource_path("resources/dms_icon.png"))
    if autostart:
        ui.toggle_active()
    ui.run()


def main():
    multiprocessing.set_start_method("spawn", force=True)
    keyboard_fix_request = False

    while True:
        print("Starting DMS application...")
        p = multiprocessing.Process(
            target=app_entry, kwargs={"autostart": keyboard_fix_request}
        )
        p.start()
        p.join()

        # Exit codes:
        # 0 = normal exit
        # 100 = restart requested
        if p.exitcode == 100:
            print("Restarting DMS application to fix keyboard hook...")
            keyboard_fix_request = True

        if p.exitcode != 100:
            break


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
