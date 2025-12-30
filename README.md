> Note:
> For generating a distributable you can use:

```bash
uv run pyinstaller --onefile --windowed --name "DiscordMessageShortcut" --icon .\resources\dms_icon.png --add-data "resources;resources" .\src\discord_message_shortcut\main.py
```