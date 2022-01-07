import json


class Config:
    """Database class"""

    with open("config.json", "r") as f:
        config = json.load(f)

    TOKEN = config.get("DISCORD_TOKEN")
    OWNER_ID = config.get("OWNER_ID")
    PREFIX = config.get("PREFIX")
    GENIUS_TOKEN = config.get("GENIUS_TOKEN")
    SPOTIFY_ID = config.get("SPOTIFY_CLIENT_ID")
    SPOTIFY_SECRET = config.get("SPOTIFY_CLIENT_SECRET")
    CHARS_LIMIT = 2000
    LAVA_CREDENTIALS = config.get("LAVALINK")
    TEST_GUILD_IDS = list(map(int, config.get("TEST_GUILD_IDS")))

    INSULTS: list = config["INSULTS"]

    def __init__(self) -> None:
        pass
