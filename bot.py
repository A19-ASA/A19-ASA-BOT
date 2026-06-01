import os
import discord
from discord.ext import tasks, commands
import requests

# قراءة توكن الديسكورد بأمان
TOKEN = os.getenv('DISCORD_TOKEN')

# ضع الـ IP الخاص بسيرفرك هنا بين الفاصلتين
SERVER_IP = "31.214.216.41:5560"
# ضع بورت الاستعلام (Query Port) الخاص بالسيرفر هنا (يكون غالباً رقم مكون من 5 أرقام)
SERVER_PORT = "21" 

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'تم تشغيل بوت A19 ASA بنجاح!')
    update_status.start()

@tasks.loop(minutes=3) # يتأكد من حالة السيرفر كل 3 دقائق
async def update_status():
    # استخدام موقع خارجي مجاني ومفتوح لفحص سيرفرات ارك عن طريق الـ IP دون الحاجة لتوكن
    url = f"https://api.gamedig.github.io/v1/query?type=arksa&host={SERVER_IP}&port={SERVER_PORT}"
    
    try:
        response = requests.get(url).json()
        if 'error' not in response:
            players = len(response.get('players', []))
            max_players = response.get('maxplayers', 50)
            
            # تحديث حالة البوت الجانبية في الديسكورد باللاعبين
            await bot.change_presence(activity=discord.Game(name=f"اللاعبين: {players}/{max_players}"))
            print(f"السيرفر متصل | اللاعبين: {players}/{max_players}")
        else:
            await bot.change_presence(activity=discord.Game(name="السيرفر مغلق 🔴"))
    except Exception as e:
        print(f"خطأ أثناء فحص السيرفر: {e}")

bot.run(TOKEN)
