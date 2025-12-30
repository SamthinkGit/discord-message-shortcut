from discord_message_shortcut.send_message import send_discord_message
from dotenv import load_dotenv
from typing import Optional
import os


class DMS_Manager:

    def __init__(self):
        load_dotenv()
        self.discord_token = os.getenv("DMS_DISCORD_TOKEN")
        self.discord_user_id = os.getenv("DMS_DISCORD_USER_ID")
        self.latest_server_id = os.getenv("DMS_LATEST_SERVER_ID")
        self.latest_channel_id = os.getenv("DMS_LATEST_CHANNEL_ID")
        self.latest_shortcut = os.getenv("DMS_LATEST_SHORTCUT")
        self.latest_message = os.getenv("DMS_LATEST_MESSAGE")

    def send_message(self, message: str) -> None:
        send_discord_message(
            message=message,
            discord_token=self.discord_token,
            discord_user_id=self.discord_user_id,
            server_id=self.latest_server_id,
            channel_id=self.latest_channel_id,
        )

    def save_to_dotenv(
        self,
        discord_token: Optional[str] = None,
        discord_user_id: Optional[str] = None,
        server_id: Optional[str] = None,
        channel_id: Optional[str] = None,
        latest_shortcut: Optional[str] = None,
        latest_message: Optional[str] = None,
    ) -> None:
        if not discord_token:
            discord_token = self.discord_token
        if not discord_user_id:
            discord_user_id = self.discord_user_id
        if not server_id:
            server_id = self.latest_server_id
        if not channel_id:
            channel_id = self.latest_channel_id
        if not latest_shortcut:
            latest_shortcut = self.latest_shortcut
        if not latest_message:
            latest_message = self.latest_message

        env_vars = {
            "DMS_DISCORD_TOKEN": discord_token,
            "DMS_DISCORD_USER_ID": discord_user_id,
            "DMS_LATEST_SERVER_ID": server_id,
            "DMS_LATEST_CHANNEL_ID": channel_id,
            "DMS_LATEST_SHORTCUT": latest_shortcut,
            "DMS_LATEST_MESSAGE": latest_message,
        }

        with open(".env", "w") as f:
            for key, value in env_vars.items():
                f.write(f'{key}="{value}"\n')