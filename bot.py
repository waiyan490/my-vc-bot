import os
import asyncio

from pyrogram import Client, filters, idle
from pytgcalls import PyTgCalls
from pytgcalls.types import AudioPiped
import yt_dlp


# =========================================================
# SETTINGS
# =========================================================

API_ID = int(os.environ.get("API_ID", "0"))
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")


# =========================================================
# EVENT LOOP
# =========================================================

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)


# =========================================================
# TELEGRAM
# =========================================================

app = Client(
    "shwe_zin_music_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

call_py = PyTgCalls(app)


# =========================================================
# START
# =========================================================

@app.on_message(filters.command("start"))
async def start(c, m):
    await m.reply_text(
        "👋 မင်္ဂလာပါ!\n\n"
        "☁️ Cloud Server ပေါ်မှ Telegram VC Music Bot "
        "အဆင်သင့် ဖြစ်ပါပြီ။\n\n"
        "🎵 /play သီချင်းနာမည်\n"
        "⏸ /pause\n"
        "▶️ /resume\n"
        "⏹ /stop"
    )


# =========================================================
# PLAY
# =========================================================

@app.on_message(filters.command("play"))
async def play(c, m):

    if len(m.command) < 2:
        await m.reply_text(
            "ကျေးဇူးပြု၍ သီချင်းနာမည် ထည့်ပေးပါ။\n\n"
            "ဥပမာ - /play Shape of You"
        )
        return

    chat_id = m.chat.id
    q = " ".join(m.command[1:])

    s = await m.reply_text(
        "⏳ သီချင်းရှာဖွေပြီး Voice Chat သို့ "
        "ချိတ်ဆက်နေပါပြီ..."
    )

    try:
        os.makedirs("downloads", exist_ok=True)

        opts = {
            "format": "bestaudio/best",
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }
            ],
            "outtmpl": "downloads/%(id)s.%(ext)s",
            "noplaylist": True,
        }

        with yt_dlp.YoutubeDL(opts) as ydl:

            search_url = (
                f"ytsearch:{q}"
                if not q.startswith("http")
                else q
            )

            info = ydl.extract_info(
                search_url,
                download=True
            )

            if "entries" in info:
                info = info["entries"][0]

            file_path = f"downloads/{info['id']}.mp3"

        # Join Voice Chat
        await call_py.join_group_call(
            chat_id,
            AudioPiped(file_path)
        )

        username = (
            m.from_user.mention
            if m.from_user
            else "Unknown"
        )

        await s.edit_text(
            f"▶️ **Now Playing in VC:**\n"
            f"🎵 {info.get('title', 'Unknown')}\n\n"
            f"👤 **Requested By:** {username}"
        )

        # Delete command after 30 seconds
        await asyncio.sleep(30)

        try:
            await m.delete()
        except Exception:
            pass

    except Exception as e:

        await s.edit_text(
            f"❌ **အမှား:**\n`{str(e)}`"
        )


# =========================================================
# PAUSE
# =========================================================

@app.on_message(filters.command("pause"))
async def pause(c, m):

    try:
        await call_py.pause_group_call(m.chat.id)

        msg = await m.reply_text(
            "⏸ သီချင်း ခဏရပ်ထားပါသည်။"
        )

        await asyncio.sleep(30)

        try:
            await m.delete()
            await msg.delete()
        except Exception:
            pass

    except Exception as e:
        await m.reply_text(
            f"❌ Error: `{e}`"
        )


# =========================================================
# RESUME
# =========================================================

@app.on_message(filters.command("resume"))
async def resume(c, m):

    try:
        await call_py.resume_group_call(m.chat.id)

        msg = await m.reply_text(
            "▶️ သီချင်း ဆက်လက်ဖွင့်နေပါပြီ။"
        )

        await asyncio.sleep(30)

        try:
            await m.delete()
            await msg.delete()
        except Exception:
            pass

    except Exception as e:
        await m.reply_text(
            f"❌ Error: `{e}`"
        )


# =========================================================
# STOP
# =========================================================

@app.on_message(filters.command("stop"))
async def stop(c, m):

    try:
        await call_py.leave_group_call(m.chat.id)

        msg = await m.reply_text(
            "⏹ Voice Chat မှ ထွက်လိုက်ပါပြီ။"
        )

        await asyncio.sleep(30)

        try:
            await m.delete()
            await msg.delete()
        except Exception:
            pass

    except Exception as e:
        await m.reply_text(
            f"❌ Error: `{e}`"
        )


# =========================================================
# MAIN
# =========================================================

async def main():

    await app.start()
    await call_py.start()

    print("Bot Started Successfully!")

    await idle()


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":
    loop.run_until_complete(main())
