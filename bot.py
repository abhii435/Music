import os
from flask import Flask
from threading import Thread
from pyrogram import Client, filters, idle
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from pytgcalls import PyTgCalls
from pytgcalls.types.input_stream import AudioPiped
from youtube_search import YoutubeSearch
import yt_dlp
import asyncio

# --- FLASK SERVER FOR KOYEB ---
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
SESSION = os.environ.get("SESSION") 
CHANNEL_1 = "LighZYagami"
CHANNEL_2 = "antishu72"

# Clients
app = Client("musicbot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
assistant = Client("assistant", api_id=API_ID, api_hash=API_HASH, session_string=SESSION)
vc = PyTgCalls(assistant)

@app.on_message(filters.command("start"))
async def start(client, message):
    user_id = message.from_user.id
    try:
        await client.get_chat_member(CHANNEL_1, user_id)
        await client.get_chat_member(CHANNEL_2, user_id)
    except:
        buttons = [[
            InlineKeyboardButton("🔔 Join Channel 1", url=f"https://t.me/{CHANNEL_1}"),
            InlineKeyboardButton("🔔 Join Channel 2", url=f"https://t.me/{CHANNEL_2}")
        ]]
        return await message.reply_photo(photo="music.jpg", caption="⚠️ Join both channels to use this bot.", reply_markup=InlineKeyboardMarkup(buttons))

    buttons = [[InlineKeyboardButton("➕ Add Bot To Your Group", url="https://t.me/LulzZec_Bot?startchannel=true")]]
    await message.reply_photo(photo="music.jpg", caption="🎧 **Welcome to Music Bot**\n\n▶️ Play music using /play", reply_markup=InlineKeyboardMarkup(buttons))

@app.on_message(filters.command("play") & filters.group)
async def play(client, message):
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
            await vc.join_group_call(message.chat.id, AudioPiped("song.mp3"))
        await m.edit(f"▶️ **Playing:** {results[0]['title']}")
    except Exception as e:
        await m.edit(f"❌ Error: {e}")

@app.on_message(filters.command("stop") & filters.group)
async def stop(client, message):
    try:
        await vc.leave_group_call(message.chat.id)
        await message.reply("⏹ Music stopped.")
    except:
        await message.reply("❌ No active call.")

# --- STARTING LOGIC ---
async def start_bot():
    print("Starting Bot & Assistant...")
    await app.start()
    await assistant.start()
    await vc.start()
    print("Bot is Online!")
    await idle()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(start_bot())
