import discord
from discord.ext import commands
from flask import Flask
from threading import Thread
import os

# ---- SETTINGS ----
TOKEN = os.getenv("TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID"))
ROLE_ID = int(os.getenv("ROLE_ID"))
MESSAGE_ID = int(os.getenv("MESSAGE_ID"))
EMOJI = "✅"
LIMIT = 300

# ---- FLASK KEEP-ALIVE ----
app = Flask('')

@app.route('/')
def home():
    return "Bot is alive!"

def run_web():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run_web)
    t.start()

# ---- DISCORD BOT ----
intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Bot is online as {bot.user}")

@bot.event
async def on_raw_reaction_add(payload):
    if payload.message_id != MESSAGE_ID or str(payload.emoji) != EMOJI or payload.user_id == bot.user.id:
        return

    guild = bot.get_guild(GUILD_ID)
    member = guild.get_member(payload.user_id)
    role = guild.get_role(ROLE_ID)

    # Stop assigning role if limit reached
    if len(role.members) >= LIMIT:
        channel = guild.get_channel(payload.channel_id)
        message = await channel.fetch_message(MESSAGE_ID)
        await message.remove_reaction(EMOJI, member)
        return

    await member.add_roles(role)

@bot.event
async def on_raw_reaction_remove(payload):
    if payload.message_id != MESSAGE_ID or str(payload.emoji) != EMOJI:
        return

    guild = bot.get_guild(GUILD_ID)
    member = guild.get_member(payload.user_id)
    role = guild.get_role(ROLE_ID)

    # Remove role when reaction is removed
    if member and role in member.roles:
        await member.remove_roles(role)

# ---- RUN EVERYTHING ----
keep_alive()
bot.run(TOKEN)
