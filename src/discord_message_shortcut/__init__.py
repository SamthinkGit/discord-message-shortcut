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
