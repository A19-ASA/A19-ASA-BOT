import os
import discord
from discord.ext import commands, tasks
import requests

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# هنا حط رقم سيرفرك الحقيقي اللي طلعته من نيترادو
SERVER_ID = '19258802' 

@bot.event
async def on_ready():
    print(f'البوت شغال كـ {bot.user.name}')
    update_status.start()

@tasks.loop(minutes=2) # يحدّث الحالة كل دقيقتين
async def update_status():
    try:
        # رابط عام لجلب بيانات سيرفرات نترادو
        url = f"https://api.nitrado.net/services/{SERVER_ID}/gameservers"
        response = requests.get(url)
        data = response.json()
        
        if data['status'] == 'success':
            players = data['data']['gameserver']['query']['player_current']
            max_players = data['data']['gameserver']['query']['player_max']
            status_text = f"{players}/{max_players} لاعب في السيرفر"
            await bot.change_presence(activity=discord.Game(name=status_text))
    except Exception as e:
        print(f"خطأ في التحديث: {e}")

TOKEN = os.getenv('DISCORD_TOKEN')
bot.run(TOKEN)
