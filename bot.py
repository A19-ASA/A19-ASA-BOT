import discord
import os
import requests
from discord.ext import commands, tasks

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# هنا حط رقم سيرفرك من رابط BattleMetrics
SERVER_ID = '19258802' 
URL = f"https://api.battlemetrics.com/servers/{39089534}"

@bot.event
async def on_ready():
    print('البوت متصل وجاهز لتحديث الحالة!')
    update_status.start()

@tasks.loop(minutes=2)
async def update_status():
    try:
        response = requests.get(URL)
        data = response.json()
        players = data['data']['attributes']['players']
        max_players = data['data']['attributes']['maxPlayers']
        await bot.change_presence(activity=discord.Game(name=f"{players}/{max_players} لاعب"))
    except Exception as e:
        print(f"تحديث الحالة معلق حالياً: {e}")

bot.run(os.getenv('DISCORD_TOKEN'))
