import os
import discord
from discord.ext import tasks, commands
import requests

# قراءة البيانات السرية بأمان من بيئة تشغيل السيرفر
TOKEN = os.getenv('DISCORD_TOKEN')
NITRADO_API_TOKEN = os.getenv('NITRADO_API_TOKEN')
SERVER_ID = os.getenv('SERVER_ID')

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'تم تشغيل البوت بنجاح باسم {bot.user.name}')
    update_status.start()

@tasks.loop(minutes=5)
async def update_status():
    headers = {'Authorization': f'Bearer {NITRADO_API_TOKEN}'}
    url = f'https://api.nitrado.net/services/{SERVER_ID}/gameservers'

    try:
        response = requests.get(url, headers=headers).json()
        if response.get('status') == 'success':
            server_data = response['data']['gameserver']
            status = server_data['status']
            players = server_data['query']['player_current']
            max_players = server_data['query']['player_max']
            
            # تحديث حالة البوت الحالية في الديسكورد بالاعتماد على قيم نيترادو الوهمية حالياً
            await bot.change_presence(activity=discord.Game(name=f"Status: {status} | Players: {players}/{max_players}"))
            print(f"تم تحديث الحالة بنجاح | اللاعبين: {players}/{max_players}")
    except Exception as e:
        print(f"حدث خطأ أثناء الاتصال بـ Nitrado: {e}")

bot.run(TOKEN)
