import json


class Config:
    """Database class"""

    with open("config.json", "r") as f:
        config = json.load(f)

    CHARS_LIMIT = 2000

    # Required
    TOKEN = config.get("DISCORD_TOKEN")
    PREFIX = config.get("PREFIX")
    LAVA_CREDENTIALS = config.get("LAVALINK")

    # Optionals
    GENIUS_TOKEN = config.get("GENIUS_TOKEN")
    SPOTIFY_ID = config.get("SPOTIFY_CLIENT_ID")
    SPOTIFY_SECRET = config.get("SPOTIFY_CLIENT_SECRET")
    try:
        TEST_GUILD_IDS = tuple(map(int, config.get("TEST_GUILD_IDS")))
    except TypeError as e:
        TEST_GUILD_IDS = ()
    OWNER_ID = config.get("OWNER_ID")
    INSULTS: tuple = tuple(config.get("INSULTS"))

    def __init__() -> None:
        pass
