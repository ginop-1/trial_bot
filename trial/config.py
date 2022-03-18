import json
from typing import Any, Dict, Optional, Tuple, Union


class Config:
    """
    Configurations class

    Attributes:
    ---
    TOKEN: [:class:`str`]
      Discord bot token
    PREFIX: [:class:`str`]
      Command prefix
    LAVA_CREDENTIALS: [:class:`dict`[:class:`str`, :class:`str`]]
      Lavalink credentials
    GENIUS_TOKEN: Optional[:class:`str`]
      Genius API token
    SPOTIFY_ID: Optional[:class:`str`]
      Spotify client ID
    SPOTIFY_SECRET: Optional[:class:`str`]
      Spotify client secret
    TEST_GUILD_IDS: Optional[:class:`tuple`]
      List of guild IDs to enable slash commands in
    """

    def __init__() -> None:
        pass

    @classmethod
    def load(cls):
        with open("configs/config.json", "r") as f:
            config = json.load(f)

        cls.CHARS_LIMIT = 2000

        # Required
        cls.TOKEN: str = config.get("DISCORD_TOKEN")
        cls.PREFIX: str = config.get("PREFIX")
        cls.LAVA_CREDENTIALS: Dict[str, str] = config.get("LAVALINK")

        # Optionals
        cls.GENIUS_TOKEN: str = config.get("GENIUS_TOKEN")
        cls.SPOTIFY_ID: str = config.get("SPOTIFY_CLIENT_ID")
        cls.SPOTIFY_SECRET: str = config.get("SPOTIFY_CLIENT_SECRET")
        cls.OWNER_ID: str = config.get("OWNER_ID")
        cls.TEST_GUILD_IDS: Tuple[str, ...] = Config._load_test_guild_ids(
            config.get("TEST_GUILD_IDS")
        )
        cls.INSULTS: Tuple[str, ...] = Config._load_insults()

    @classmethod
    def _load_test_guild_ids(cls, guild_ids: Union[Tuple[str], None]) -> tuple:
        try:
            return tuple(map(int, guild_ids))
        except TypeError:
            return tuple()

    @classmethod
    def _load_insults(cls) -> tuple:
        try:
            with open("configs/insults.txt", "r") as f:
                return f.read().splitlines()
        except FileNotFoundError:
            return []
