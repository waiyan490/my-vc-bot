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
# CHECK SETTINGS
# =========================================================

if not API_ID:
    raise ValueError("API_ID is missing")

if not API_HASH:
    raise ValueError("API_HASH is missing")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is missing")


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
        "🎵 Telegram VC Music Bot အဆင်သင့်ဖြစ်ပါပြီ။\n\n"
        "အသုံးပြုရန်👇\n"
        "/play သီချင်းနာမည်\n"
        "/pause\n"
        "/resume\n"
        "/stop"
    )


# =========================================================
# PLAY
# =========================================================

@app.on_message(filters.command("play"))
async def play(c, m):

    if len(m.command) < 2:
        await m.reply_text(
            "❌ သီချင်းနာမည် ထည့်ပေးပါ။\n\n"
            "ဥပမာ:\n"
            "/play Shape of You"
        )
        return

    chat_id = m.chat.id
    q = " ".join(m.command[1:])

    s = await m.reply_text(
        "⏳ သီချင်းရှာဖွေနေပါတယ်...\n"
        "🎵 Voice Chat ကို ချိတ်ဆက်နေပါတယ်..."
    )

    try:

        os.makedirs("downloads", exist_ok=True)

        opts = {
            "format": "bestaudio/best",
            "outtmpl": "downloads/%(id)s.%(ext)s",
            "noplaylist": True,
            "quiet": True,
            "no_warnings": True,
        }

        with yt_dlp.YoutubeDL(opts) as ydl:

            if q.startswith("http"):
                info = ydl.extract_info(q, download=True)
            else:
                info = ydl.extract_info(
                    f"ytsearch1:{q}",
                    download=True
                )

                if "entries" in info:
                    info = info["entries"][0]

        file_path = None

        video_id = info.get("id")

        if video_id:
            for filename in os.listdir("downloads"):
                if filename.startswith(video_id + "."):
                    file_path = os.path.join(
                        "downloads",
                        filename
                    )
                    break

        if not file_path:
            raise FileNotFoundError(
                "Downloaded audio file not found"
            )

        # =================================================
        # JOIN VOICE CHAT
        # =================================================

        await call_py.join_group_call(
            chat_id,
            AudioPiped(file_path)
        )

        title = info.get(
            "title",
            "Unknown"
        )

        username = (
            m.from_user.mention
            if m.from_user
            else "Unknown"
        )

        await s.edit_text(
            f"▶️ **Now Playing**\n\n"
            f"🎵 {title}\n"
            f"👤 Requested By: {username}"
        )

        # Command ကို 30 စက္ကန့်နောက် ဖျက်
        await asyncio.sleep(30)

        try:
            await m.delete()
        except Exception:
            pass

    except Exception as e:

        await s.edit_text(
            f"❌ **အမှားဖြစ်နေပါတယ်**\n\n"
            f"`{str(e)}`"
        )


# =========================================================
# PAUSE
# =========================================================

@app.on_message(filters.command("pause"))
async def pause(c, m):

    try:

        await call_py.pause_group_call(
            m.chat.id
        )

        msg = await m.reply_text(
            "⏸ သီချင်း ခဏရပ်ထားပါပြီ။"
        )

        await asyncio.sleep(30)

        try:
            await m.delete()
        except Exception:
            pass

        try:
            await msg.delete()
        except Exception:
            pass

    except Exception as e:

        await m.reply_text(
            f"❌ Error: {e}"
        )


# =========================================================
# RESUME
# =========================================================

@app.on_message(filters.command("resume"))
async def resume(c, m):

    try:

        await call_py.resume_group_call(
            m.chat.id
        )

        msg = await m.reply_text(
            "▶️ သီချင်း ပြန်ဖွင့်နေပါပြီ။"
        )

        await asyncio.sleep(30)

        try:
            await m.delete()
        except Exception:
            pass

        try:
            await msg.delete()
        except Exception:
            pass

    except Exception as e:

        await m.reply_text(
            f"❌ Error: {e}"
        )


# =========================================================
# STOP
# =========================================================

@app.on_message(filters.command("stop"))
async def stop(c, m):

    try:

        await call_py.leave_group_call(
            m.chat.id
        )

        msg = await m.reply_text(
            "⏹ Voice Chat မှ ထွက်လိုက်ပါပြီ။"
        )

        await asyncio.sleep(30)

        try:
            await m.delete()
        except Exception:
            pass

        try:
            await msg.delete()
        except Exception:
            pass

    except Exception as e:

        await m.reply_text(
            f"❌ Error: {e}"
        )


# =========================================================
# MAIN
# =========================================================

async def main():

    print("🚀 Starting Telegram Bot...")

    await app.start()

    print("✅ Pyrogram started")

    await call_py.start()

    print("✅ PyTgCalls started")

    print("🎵 Bot Started Successfully!")

    await idle()

    await call_py.stop()
    await app.stop()


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":
    asyncio.run(main())
