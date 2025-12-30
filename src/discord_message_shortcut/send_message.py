import json
from http.client import HTTPSConnection
from typing import NoReturn

import keyboard
from rich import print as pprint
from rich.panel import Panel


def send_discord_message(
    message: str,
    discord_token: str,
    discord_user_id: str,
    server_id: str,
    channel_id: str,
) -> None:
    """
    Sends a message to a specified Discord channel using the Discord API.
    Args:
        message (str): The message content to send.
        discord_token (str): The Discord authorization token.
        discord_user_id (str): The Discord user ID.
        server_id (str): The ID of the Discord server (guild).
        channel_id (str): The ID of the Discord channel.
    """
    conn = HTTPSConnection("discordapp.com", 443)

    headers = {
        "content-type": "application/json",
        "authorization": discord_token,
        "user-id": discord_user_id,
        "host": "discordapp.com",
        "referrer": f"https://discord.com/channels/{server_id}/{channel_id}",
    }

    payload = json.dumps({"content": message})

    conn.request(
        "POST",
        f"/api/v6/channels/{channel_id}/messages",
        payload,
        headers,
    )

    conn.getresponse()
    conn.close()


# ==============================================================
# Example usage
# This script listens for a specific key press and sends a Discord 
# message when triggered.
# ==============================================================

def main(
    message: str,
    discord_token: str,
    discord_user_id: str,
    server_id: str,
    channel_id: str,
    trigger_key: str = "ç",
) -> NoReturn:
    """
    Main application loop. Waits for a key press and sends a Discord message.
    Args:
        message (str): The message content to send.
        discord_token (str): The Discord authorization token.
        discord_user_id (str): The Discord user ID.
        server_id (str): The ID of the Discord server (guild).
        channel_id (str): The ID of the Discord channel.
    """
    panel = Panel.fit(
        f"[bold green]Discord Auto Message[/bold green]\n\n"
        f"[white]Press '{trigger_key}' to send the message:[/white]\n\n"
        f"[bold yellow]{message}[/bold yellow]",
        title="Discord Auto Message",
        border_style="bright_blue",
    )

    pprint(panel)

    try:
        while True:
            keyboard.wait(trigger_key)
            send_discord_message(
                message=message,
                discord_token=discord_token,
                discord_user_id=discord_user_id,
                server_id=server_id,
                channel_id=channel_id,
            )
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main(
        message="Hello! Im a Test Message :D",
        discord_token="YOUR_DISCORD_TOKEN",
        discord_user_id="YOUR_USER_ID",
        server_id="YOUR_SERVER_ID",
        channel_id="YOUR_CHANNEL_ID",
        trigger_key="ç",
    )