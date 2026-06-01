import discord
import os
import requests
from discord.ext import commands, tasks

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# هنا حطينا رقم باتل ميتريكس فقط
SERVER_ID = '39089534' 
URL = f"https://api.battlemetrics.com/servers/{SERVER_ID}"

@bot.event
async def on_ready():
    print('Bot is online and ready!')
    update_status.start()

@tasks.loop(minutes=2)
async def update_status():
    try:
        response = requests.get(URL)
        data = response.json()
        # جلب البيانات من المسار الصحيح
        attrs = data['data']['attributes']
        players = attrs['players']
        max_players = attrs['maxPlayers']
        status_text = f"{players}/{max_players} لاعب"
        await bot.change_presence(activity=discord.Game(name=status_text))
    except Exception as e:
        print(f"Error updating status: {e}")

bot.run(os.getenv('DISCORD_TOKEN'))
