import os
from dataclasses import dataclass
from typing import Optional, Dict

from dotenv import dotenv_values
from platformdirs import user_config_dir

from discord_message_shortcut.send_message import send_discord_message


@dataclass(frozen=True)
class DmsEnvKeys:
    discord_token: str = "DMS_DISCORD_TOKEN"
    discord_user_id: str = "DMS_DISCORD_USER_ID"
    latest_server_id: str = "DMS_LATEST_SERVER_ID"
    latest_channel_id: str = "DMS_LATEST_CHANNEL_ID"
    latest_shortcut: str = "DMS_LATEST_SHORTCUT"
    latest_message: str = "DMS_LATEST_MESSAGE"


class DMS_Manager:
    """
    Reads and writes a stable .env file from a per-user config directory.
    """

    def __init__(
        self,
        app_name: str = "DMS",
        env_filename: str = ".env",
        env_path: Optional[str] = None,
    ) -> None:
        self._keys = DmsEnvKeys()

        if env_path is None:
            config_dir = user_config_dir(appname=app_name, roaming=True)
            os.makedirs(config_dir, exist_ok=True)
            env_path = os.path.join(config_dir, env_filename)

        self.env_path = env_path
        self.reload_from_env()

    def reload_from_env(self) -> None:
        data = dotenv_values(self.env_path) if os.path.exists(self.env_path) else {}

        self.discord_token = str(data.get(self._keys.discord_token) or "").strip()
        self.discord_user_id = str(data.get(self._keys.discord_user_id) or "").strip()
        self.latest_server_id = str(data.get(self._keys.latest_server_id) or "").strip()
        self.latest_channel_id = str(data.get(self._keys.latest_channel_id) or "").strip()

        self.latest_shortcut = str(data.get(self._keys.latest_shortcut) or "º")
        self.latest_shortcut = self.latest_shortcut.strip() or "º"

        self.latest_message = str(data.get(self._keys.latest_message) or "Hello World from DMS!")
        self.latest_message = self.latest_message.strip() or "Hello World from DMS!"

    def send_message(self, message: str) -> None:
        send_discord_message(
            message=message,
            discord_token=self.discord_token,
            discord_user_id=self.discord_user_id,
            server_id=self.latest_server_id,
            channel_id=self.latest_channel_id,
        )

    def get_env_vars(self) -> Dict[str, str]:
        return {
            self._keys.discord_token: self.discord_token,
            self._keys.discord_user_id: self.discord_user_id,
            self._keys.latest_server_id: self.latest_server_id,
            self._keys.latest_channel_id: self.latest_channel_id,
            self._keys.latest_shortcut: self.latest_shortcut,
            self._keys.latest_message: self.latest_message,
        }

    def save_to_env(
        self,
        discord_token: Optional[str] = None,
        discord_user_id: Optional[str] = None,
        server_id: Optional[str] = None,
        channel_id: Optional[str] = None,
        latest_shortcut: Optional[str] = None,
        latest_message: Optional[str] = None,
    ) -> None:
        # Update in-memory first
        if discord_token is not None:
            self.discord_token = discord_token
        if discord_user_id is not None:
            self.discord_user_id = discord_user_id
        if server_id is not None:
            self.latest_server_id = server_id
        if channel_id is not None:
            self.latest_channel_id = channel_id
        if latest_shortcut is not None:
            self.latest_shortcut = latest_shortcut
        if latest_message is not None:
            self.latest_message = latest_message

        os.makedirs(os.path.dirname(self.env_path), exist_ok=True)

        # Persist
        env_vars = self.get_env_vars()
        with open(self.env_path, "w", encoding="utf-8") as f:
            for key, value in env_vars.items():
                escaped = (value or "").replace('"', '\\"')
                f.write(f'{key}="{escaped}"\n')

        # Reload from file to normalize and ensure consistency
        self.reload_from_env()
