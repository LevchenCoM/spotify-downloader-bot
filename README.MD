# Spotify Downloader Bot

Requirements:

- python3 (tested on 3.9, 3.10, 3.11)
- ffmpeg

## Installation
```shell
# Download the repo
git clone https://github.com/LevchenCoM/spotify-downloader-bot.git

# Go to project dir
cd spotify-downloader-bot

# Create virtualenv
python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt

# Set env variables > .env
vim .env # use .env.sample as an example, it contains all required variables

# Run bot
python spotify_downloader_bot.py
```