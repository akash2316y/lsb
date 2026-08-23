import os
from dotenv import load_dotenv
load_dotenv()
from os import environ
import logging
from logging.handlers import RotatingFileHandler

# Recommended
TG_BOT_TOKEN = os.environ.get("TG_BOT_TOKEN", "")
APP_ID = int(os.environ.get("APP_ID", ""))
API_HASH = os.environ.get("API_HASH", "")

# Channel where user links are stored
DATABASE_CHANNEL = int(os.environ.get("DATABASE_CHANNEL", ""))

# Main
OWNER_ID = int(os.environ.get("OWNER_ID", "")) #7889947993 7932127170
PORT = os.environ.get("PORT", "")
ADMINS = [7889947993]  

# Database
DB_URI = os.environ.get("DATABASE_URL", "")
DB_NAME = os.environ.get("DATABASE_NAME", "")

#Auto approve 
CHAT_ID = [int(app_chat_id) if id_pattern.search(app_chat_id) else app_chat_id for app_chat_id in environ.get('CHAT_ID', '').split()] # dont change anything 
TEXT = environ.get("APPROVED_WELCOME_TEXT", "<b>Hᴇʏ {mention},\n\nʏᴏᴜʀ ʀᴇǫᴜᴇsᴛ ᴛᴏ ᴊᴏɪɴ {title} ɪs ᴀᴘᴘʀᴏᴠᴇᴅ.</b>")
APPROVED = environ.get("APPROVED_WELCOME", "off").lower()

# Default
TG_BOT_WORKERS = int(os.environ.get("TG_BOT_WORKERS", "40"))
#--- ---- ---- --- --- --- - -- -  - - - - - - - - - - - --  - -
# Messages
START_MSG = os.environ.get("START_MESSAGE", "<b><blockquote>ʜᴇʟʟᴏ {mention} ×</blockquote><blockquote>ɪ'ᴍ ᴊᴜsᴛ ʟɪᴋᴇ ʏᴏᴜʀ ꜰʀɪᴇɴᴅʟʏ ɴᴇɪɢʜʙᴏʀʜᴏᴏᴅ ʟɪɴᴋ-sʜᴀʀɪɴɢ ʙᴏᴛ ! ᴍʏ ᴍᴀɪɴ ᴊᴏʙ ɪs sʜᴀʀɪɴɢ ᴄʜᴀɴɴᴇʟ ʟɪɴᴋs ᴛᴏ ᴋᴇᴇᴘ ᴀʟʟ ᴛʜᴇ ᴀᴅᴍɪɴ ᴄʜᴀɴɴᴇʟs sᴀꜰᴇ ᴀɴᴅ sᴏᴜɴᴅ ꜰʀᴏᴍ ᴄᴏᴘʏʀɪɢʜᴛ sᴛʀɪᴋᴇs.</blockquote><blockquote>— ʙᴜɪʟᴛ ꜰᴏʀ <a href='https://t.me/flawless_network'>ꜰʟᴀᴡʟᴇss ɴᴇᴛᴡᴏʀᴋ</a></b></blockquote>")
START_PIC = os.environ.get("START_PIC", "https://graph.org/file/2a3bdf158d2d876c474a1-8566a8ace3bc440d18.jpg")

#FORCE_PIC
FORCE_PIC = os.environ.get("FORCE_PIC", "https://graph.org/file/2a3bdf158d2d876c474a1-8566a8ace3bc440d18.jpg")
FORCE_MSG = """<b><blockquote>›› Hᴇʏ {mention} ×</blockquote>\n      ʏᴏᴜʀ ʟɪɴᴋ ɪs ʀᴇᴀᴅʏ ‼️ ʟᴏᴏᴋs ʟɪᴋᴇ ʏᴏᴜ ʜᴀᴠᴇɴ'ᴛ sᴜʙsᴄʀɪʙᴇᴅ ᴛᴏ ᴏᴜʀ ᴄʜᴀɴɴᴇʟs ʏᴇᴛ, sᴜʙsᴄʀɪʙᴇ ɴᴏᴡ ᴛᴏ ɢᴇᴛ ʏᴏᴜʀ ʟɪɴᴋ</b>"""

FSUB_LINK_EXPIRY = int(os.getenv("FSUB_LINK_EXPIRY", "300"))  # 0 means no expiry

HELP = os.environ.get("HELP_MESSAGE", "<b></b>")

ABOUT = os.environ.get("ABOUT_MESSAGE", "<b><blockquote expandable>This bot is developed to securely share Telegram channel links with temporary invite links, protecting your channels from copyright issues.</b>")


ABOUT_TXT = """<b><blockquote>›› ᴘʀᴏᴍᴏ : <a href='http://t.me/Kakuzoo0'>ᴏᴡɴᴇʀ</a></b></blockquote>"""

CHANNELS_TXT = """<b>›› ᴀɴɪᴍᴇ ᴄʜᴀɴɴᴇʟ</b> """

#--- ---- ---- --- --- --- - -- -  - - - - - - - - - - - --  - -
# Default
BOT_STATS_TEXT = "<b>BOT UPTIME</b>\n{uptime}"
USER_REPLY_TEXT = "⚠️ ғᴜᴄᴋ ʏᴏᴜ, ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴍʏ ᴍᴀsᴛᴇʀ. ɢᴏ ᴀᴡᴀʏ, ʙɪᴛᴄʜ 🙃!"

# Logging
LOG_FILE_NAME = "links-sharingbot.txt"

#--- ---- ---- --- --- --- - -- -  - - - - - - - - - - - --  - -


logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s - %(levelname)s] - %(name)s - %(message)s",
    datefmt='%d-%b-%y %H:%M:%S',
    handlers=[
        RotatingFileHandler(
            LOG_FILE_NAME,
            maxBytes=50000000,
            backupCount=10
        ),
        logging.StreamHandler()
    ]
)
logging.getLogger("pyrogram").setLevel(logging.WARNING)

def LOGGER(name: str) -> logging.Logger:
    return logging.getLogger(name)
    
