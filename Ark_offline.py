import os
import asyncio
from flask import Flask
from threading import Thread
import discord
from discord.ext import commands

# 🎛️ ======= KONFIGURATION =======
DISCORD_TOKEN = os.environ["DISCORD_TOKEN"]     # Dein Bot-Token
TRIGGER_TEXT = "triggered by"                    # Text, der den Bot auslöst
USER_IDS_TO_NOTIFY = [730067423935594530]       # Liste der User-IDs für DMs
NUMBER_OF_PINGS = 20                             # Anzahl Pings & DMs pro Person

PING_CHANNEL_ID = 1376343305830531082            # Channel-ID für Pings
VOICE_CHANNEL_ID_1 = 1293936068143612027         # Erster Sprachkanal (ein Ton)
VOICE_CHANNEL_ID_2 = 1376702476488671342         # Zweiter Sprachkanal (mehrere Töne)

MP3_FILENAME_1 = "alarm.mp3"                     # Erster Ton (einmal abspielen)
MP3_FILENAME_2 = "sound.mp3"                     # Zweiter Ton (mehrfach abspielen)
NUMBER_OF_REPEATS = 2                            # Wie oft zweiter Ton abgespielt wird
# 🎛️ =============================

app = Flask('')
@app.route('/')
def home():
    return "Bot läuft!"
def run():
    app.run(host='0.0.0.0', port=8080)
def keep_alive():
    t = Thread(target=run)
    t.start()

intents = discord.Intents.default()
intents.message_content = True
intents.messages = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

alarm_lock = asyncio.Lock()  # 🚨 Sperre für gleichzeitige Alarme

@bot.event
async def on_ready():
    print(f"✅ Bot ist online als {bot.user.name}")

async def play_sound(voice_client, filename, repeats=1):
    for i in range(repeats):
        audio_source = discord.FFmpegPCMAudio(filename)
        done = asyncio.Event()

        def after_playing(error):
            if error:
                print(f"❌ Fehler beim Abspielen: {error}")
            bot.loop.call_soon_threadsafe(done.set)

        voice_client.play(audio_source, after=after_playing)
        await done.wait()

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    if TRIGGER_TEXT and TRIGGER_TEXT.lower() not in message.content.lower():
        return

    # Prüfe, ob gerade ein Alarm läuft
    if alarm_lock.locked():
        print("⚠️ Alarm läuft bereits, neuer Trigger wird ignoriert.")
        return

    async with alarm_lock:  # 🔒 Sperre aktivieren
        print(f"📩 Nachricht erkannt: {message.content}")

        # Pings und DMs mehrfach senden
        channel = bot.get_channel(PING_CHANNEL_ID)
        mention_string = ' '.join(f"<@{uid}>" for uid in USER_IDS_TO_NOTIFY)

        for i in range(NUMBER_OF_PINGS):
            if channel:
                await channel.send(
                    f"{mention_string} ⚠️ Tek Sensor getriggert!!! ({i+1}/{NUMBER_OF_PINGS})\nid=2134784721848210427\n```{message.content}```"
                )
                print(f"🔔 Ping {i+1} gesendet")
            await asyncio.sleep(0.5)

        for user_id in USER_IDS_TO_NOTIFY:
            user = await bot.fetch_user(user_id)
            for i in range(NUMBER_OF_PINGS):
                try:
                    await user.send(
                        f"⚠️ Tek Sensor getriggert!!! ({i+1}/{NUMBER_OF_PINGS})\nid=2134784721848210427\n```{message.content}```"
                    )
                    print(f"📨 DM {i+1} an {user.name} gesendet")
                except Exception as e:
                    print(f"❌ Fehler beim Senden an {user_id}: {e}")
                await asyncio.sleep(0.5)

        # Sprachkanal 1 joinen & Ton abspielen
        voice_channel_1 = bot.get_channel(VOICE_CHANNEL_ID_1)
        if voice_channel_1 and isinstance(voice_channel_1, discord.VoiceChannel):
            try:
                voice_client_1 = await voice_channel_1.connect()
                print(f"🔊 Bot ist im Sprachkanal 1")
                await play_sound(voice_client_1, MP3_FILENAME_1, repeats=1)
                await voice_client_1.disconnect()
                print("🚪 Bot hat Sprachkanal 1 verlassen")
            except Exception as e:
                print(f"❌ Fehler in Sprachkanal 1: {e}")

        # Sprachkanal 2 joinen & Ton mehrfach abspielen
        voice_channel_2 = bot.get_channel(VOICE_CHANNEL_ID_2)
        if voice_channel_2 and isinstance(voice_channel_2, discord.VoiceChannel):
            try:
                voice_client_2 = await voice_channel_2.connect()
                print(f"🔊 Bot ist im Sprachkanal 2")
                await play_sound(voice_client_2, MP3_FILENAME_2, repeats=NUMBER_OF_REPEATS)
                await voice_client_2.disconnect()
                print("🚪 Bot hat Sprachkanal 2 verlassen")
            except Exception as e:
                print(f"❌ Fehler in Sprachkanal 2: {e}")

keep_alive()
bot.run(DISCORD_TOKEN)

