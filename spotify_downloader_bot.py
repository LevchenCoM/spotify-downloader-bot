import logging
import re
import tempfile
import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import filters, ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, CallbackContext

import subprocess


# Load environment variables from .env file
load_dotenv()

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Telegram Bot Token
TOKEN = os.getenv("TOKEN")
# Spotify Credentials
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

# Allowed users list
users_list = os.getenv("ALLOWED_USERS_IDS")
ALLOWED_USERS_IDS = users_list.split(",") if users_list else []


def validate_song_url(song_url):
    expression = r"https:\/\/open\.spotify\.com\/track\/[^?]+"
    if not re.match(expression, song_url):
        raise ValueError("Invalid song url.")


def validate(update: Update, song_url: str):
    user_id = update.effective_user.id
    # User validation
    if ALLOWED_USERS_IDS and str(user_id) not in ALLOWED_USERS_IDS:
        raise ValueError("Permission denied")
    
    validate_song_url(song_url)


async def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    await update.message.reply_text('Hi! Send me a Spotify song link and I will download it for you.')


async def download_song(update: Update, context: CallbackContext) -> None:
    """Download a song from Spotify and send it back to the user."""
    song_url = update.message.text
    try:
        validate(update, song_url)

        await update.message.reply_text("Downloading has been started, please wait")
        logger.info("Start downloading")
        # Get the song URL from the user's message
        song_url = update.message.text
        
        # Download the song
        temp_dir = tempfile.mkdtemp()
        logger.info(f"Created temp dir: {temp_dir}")
        process = subprocess.Popen(
            [
                "spotdl",
                "--client-id", SPOTIFY_CLIENT_ID,
                "--client-secret", SPOTIFY_CLIENT_SECRET,
                "--format", "flac",
                "--bitrate", "320k",
                song_url
            ],
            cwd=temp_dir
        )

        process.wait()
        file_path = os.path.join(temp_dir, os.listdir(temp_dir)[0])
        logger.info(f"Downloaded song: {file_path}")

        # Send the downloaded song file to the user
        await update.message.reply_document(document=open(file_path, 'rb'))

        # Remove temp files and dir
        os.remove(file_path)
        os.rmdir(temp_dir)
        logger.info(f"Temp dir removed")
    
    except Exception as e:
        await update.message.reply_text(f"An error occurred: {str(e)}")


def main() -> None:
    """Start the bot."""
    app = ApplicationBuilder().token(TOKEN).build()

    # Register command handlers
    app.add_handler(CommandHandler("start", start))

    # Register a message handler
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_song))

    # Start the Bot
    app.run_polling()


if __name__ == '__main__':
    main()
