<h1 align="center"> Trial BOT </h1>

<h5 align="center">simple discord bot that plays music, scrapes wikipedia and other useless stuff</h5>
<p align="center">
<a href="https://nextcord.readthedocs.io/en/latest/index.html"> 
  <img src="https://img.shields.io/badge/BUILT%20USING-Nextcord-blue?style=for-the-badge" /></a>
<img src="https://img.shields.io/github/license/ginop-1/trial_bot?style=for-the-badge" />
<img src="https://img.shields.io/github/languages/top/ginop-1/trial_bot?style=for-the-badge" />
</p>

---

### Installation:

- Create a discord app
- Install dependencies: `pip install -r requirements.txt`
- Install lavalink 3.2 (3.1.x has a bug with encoding): `pip install https://github.com/Devoxin/Lavalink.py/archive/refs/heads/3.2.zip`
- Install Java 13
- Download and setup a [lavalink server](https://github.com/freyacodes/Lavalink/releases) \*
- Edit `application.yml` for lavalink server
- Edit `config.json.example` based on your needs and rename it to `config.json`
- Start the lavalink server and the bot

\* I personally host the bot on a Raspberry Pi (arm). If you're in the same situation you should use a [different lavalink build](https://github.com/Cog-Creators/Lavalink-Jars/releases)

### Features:

- Play Music from Youtube, Deezer, Spotify and SoundCloud
- Scrape articles from Wikipedia
- Shame people
