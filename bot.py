import os
import asyncio
from pyrogram import Client, filters
from pytgcalls import PyTgCalls
from pytgcalls.types import AudioPiped
import yt_dlp

API_ID = 38991155
API_HASH = "6eb307ac1aba4d84679749b9bccc53d1"
BOT_TOKEN = "8784979169:AAEZJb6IEiKm1clqR5eoI6_eZ92yFuI7LJQ"

app = Client("shwe_zin_music_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
call_py = PyTgCalls(app)

@app.on_message(filters.command("start"))
async def start(c, m):
    await m.reply_text("👋 မင်္ဂလာပါ! Cloud Server ပေါ်မှ **Telegram VC Music Bot** အဆင်သင့် ဖြစ်ပါပြီ။\n\n- `/play သီချင်းနာမည်` (Voice Chat ထဲတွင် သီချင်းဖွင့်ရန်)\n- `/pause` (ရပ်ခဏထားရန်)\n- `/resume` (ပြန်ဖွင့်ရန်)\n- `/stop` (VC မှ ထွက်ရန်)")

@app.on_message(filters.command("play"))
async def play(c, m):
    if len(m.command) < 2:
        await m.reply_text("ကျေးဇူးပြု၍ သီချင်းနာမည် ထည့်ပေးပါ။ ဥပမာ: `/play Shape of You`")
        return

    chat_id = m.chat.id
    q = " ".join(m.command[1:])
    s = await m.reply_text("⏳ သီချင်းရှာဖွေပြီး Voice Chat သို့ ချိတ်ဆက်နေပါပြီ...")

    try:
        opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}],
            'outtmpl': 'downloads/%(id)s.%(ext)s',
            'noplaylist': True,
        }
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(f"ytsearch:{q}" if not q.startswith("http") else q, download=True)
            if 'entries' in info: info = info['entries'][0]
            f = f"downloads/{info['id']}.mp3"

        # Voice Chat ထဲသို့ ဝင်ရောက်ပြီး သီချင်းစတင်ဖွင့်မည်
        await call_py.join_group_call(
            chat_id,
            AudioPiped(f)
        )
        
        await s.edit_text(f"▶️ **Now Playing in VC:** {info.get('title')}\n👤 **Requested By:** {m.from_user.mention}")

        # စက္ကန့် ၃၀ ပြည့်ပါက Command message များကို ဖျက်မည်
        await asyncio.sleep(30)
        try:
            await m.delete()
        except: pass

    except Exception as e:
        await s.edit_text(f"❌ အမှား: {str(e)}")

@app.on_message(filters.command("pause"))
async def pause(c, m):
    try:
        await call_py.pause_group_call(m.chat.id)
        msg = await m.reply_text("⏸ သီချင်း ခဏရပ်ထားပါသည်။")
        await asyncio.sleep(30)
        await m.delete()
        await msg.delete()
    except Exception as e:
        await m.reply_text(f"Error: {e}")

@app.on_message(filters.command("resume"))
async def resume(c, m):
    try:
        await call_py.resume_group_call(m.chat.id)
        msg = await m.reply_text("▶️ သီချင်း ဆက်လက်ဖွင့်နေပါပြီ။")
        await asyncio.sleep(30)
        await m.delete()
        await msg.delete()
    except Exception as e:
        await m.reply_text(f"Error: {e}")

@app.on_message(filters.command("stop"))
async def stop(c, m):
    try:
        await call_py.leave_group_call(m.chat.id)
        msg = await m.reply_text("⏹ Voice Chat မှ ထွက်လိုက်ပါပြီ။")
        await asyncio.sleep(30)
        await m.delete()
        await msg.delete()
    except Exception as e:
        await m.reply_text(f"Error: {e}")

async def main():
    await app.start()
    await call_py.start()
    print("Bot Started Successfully!")
    await idle()

if __name__ == "__main__":
    from pyrogram import idle
    app.loop.run_until_complete(main())
