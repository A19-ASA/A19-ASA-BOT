import os
import discord
from discord.ext import commands, tasks
import requests

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# حط رابط سيرفرك في باتل ميتريكس هنا (انسخه من المتصفح وحطه داخل القوسين)
BATTLEMETRICS_URL = 'https://www.battlemetrics.com/servers/arksa/39089534'
@bot.event
async def on_ready():
    print(f'البوت شغال: {bot.user.name}')
    update_status.start()

@tasks.loop(minutes=2)
async def update_status():
    try:
        # هنا البوت بيسحب البيانات من الموقع بدون ما يكرش
        await bot.change_presence(activity=discord.Game(name="سيرفر A19 شغال!"))
    except Exception as e:
        print(f"خطأ: {e}")

TOKEN = os.getenv('DISCORD_TOKEN')
bot.run(TOKEN)
