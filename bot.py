import os
from flask import Flask
from threading import Thread
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from pytgcalls import PyTgCalls
from pytgcalls.types.input_stream import AudioPiped
from youtube_search import YoutubeSearch
import yt_dlp

# --- RENDER PORT FIX ---
server = Flask('')
@server.route('/')
def home():
    return "Bot is Running"

def run():
    server.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))

Thread(target=run).start()

# --- CONFIGURATION ---
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")
SESSION = os.environ.get("SESSION") # Assistant User String Session
CHANNEL_1 = "LighZYagami"
CHANNEL_2 = "antishu72"

# Bot Client
app = Client("musicbot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Assistant Client (Zaroori for Voice Chat)
assistant = Client("assistant", api_id=API_ID, api_hash=API_HASH, session_string=SESSION)

vc = PyTgCalls(assistant)
queue = []

@app.on_message(filters.command("start"))
async def start(client: Client, message: Message):
    user_id = message.from_user.id
    try:
        member1 = await client.get_chat_member(CHANNEL_1, user_id)
        member2 = await client.get_chat_member(CHANNEL_2, user_id)
    except:
        member1 = member2 = None

    if not member1 or not member2:
        buttons = [[
            InlineKeyboardButton("🔔 Join Channel 1", url=f"https://t.me/{CHANNEL_1}"),
            InlineKeyboardButton("🔔 Join Channel 2", url=f"https://t.me/{CHANNEL_2}")
        ]]
        return await message.reply_photo(photo="music.jpg", caption="⚠️ Join both channels to use this bot.", reply_markup=InlineKeyboardMarkup(buttons))

    buttons = [[InlineKeyboardButton("➕ Add Bot To Your Group", url="https://t.me/LulzZec_Bot?startchannel=true")]]
    await message.reply_photo(photo="music.jpg", caption="🎧 **Welcome to Music Bot**\n\n▶️ Play music using /play", reply_markup=InlineKeyboardMarkup(buttons))

@app.on_message(filters.command("play"))
async def play(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply("❌ Usage: /play song name")

    m = await message.reply("🔎 Searching...")
    song_name = " ".join(message.command[1:])
    results = YoutubeSearch(song_name, max_results=1).to_dict()
    
    if not results:
        return await m.edit("❌ Song not found!")

    url = "https://www.youtube.com" + results[0]["url_suffix"]
    await m.edit("📥 Downloading...")

    ydl_opts = {'format': 'bestaudio/best', 'quiet': True, 'outtmpl': 'song.mp3', 'noplaylist': True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.extract_info(url, download=True)

    try:
        if not vc.is_connected:
            await assistant.start() # Start assistant if not started
            await vc.join_group_call(message.chat.id, AudioPiped("song.mp3"))
            await m.edit(f"▶️ **Playing:** {results[0]['title']}")
        else:
            await m.edit(f"✅ **Queued:** {results[0]['title']}")
    except Exception as e:
        await m.edit(f"❌ Error: {e}")

@app.on_message(filters.command("stop"))
async def stop(client: Client, message: Message):
    try:
        await vc.leave_group_call(message.chat.id)
        await message.reply("⏹ Music stopped.")
    except:
        await message.reply("❌ No active call.")

print("Bot & Assistant Starting...")
vc.start()
app.run()
