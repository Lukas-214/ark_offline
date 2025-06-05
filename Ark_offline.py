import os
from flask import Flask
from threading import Thread
import discord
from discord.ext import commands
import asyncio

# 🎛️ ======= KONFIGURATION =======
DISCORD_TOKEN = os.environ["DISCORD_TOKEN"]     # Dein Bot-Token
TRIGGER_TEXT = "triggered by"                   # Text, der den Bot auslöst
USER_IDS_TO_NOTIFY = [730067423935594530]       # Liste der User-IDs, die per DM benachrichtigt werden sollen
NUMBER_OF_PINGS = 2                              # Anzahl Pings & DMs pro Person
PING_CHANNEL_ID = 1376343305830531082            # Channel-ID für Pings
# 🎛️ =============================

if (user && user.id) {
  console.log(user.id);
} else {
  console.log("User nicht gefunden!");
}
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

@bot.event
async def on_ready():
    print(f"✅ Bot ist online als {bot.user.name}")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if TRIGGER_TEXT and TRIGGER_TEXT.lower() not in message.content.lower():
        return

    print(f"📩 Nachricht erkannt: {message.content}")

    # Pings im Channel
    channel = bot.get_channel(PING_CHANNEL_ID)
    mention_string = ' '.join(f"<@{uid}>" for uid in USER_IDS_TO_NOTIFY)

    for i in range(NUMBER_OF_PINGS):
        if channel:
            await channel.send(
                f"{mention_string} ⚠️ Tek Sensor getriggert!!! ({i+1}/{NUMBER_OF_PINGS})\nid=2134784721848210427\n```{message.content}```"
            )
            print(f"🔔 Ping {i+1} gesendet")
        await asyncio.sleep(0.5)

    # DMs an User mehrfach
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

keep_alive()
bot.run(DISCORD_TOKEN)
