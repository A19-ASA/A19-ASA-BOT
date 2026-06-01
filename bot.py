import osimport os
import discord
from discord.ext import tasks
import requests

# جلب الإعدادات من متغيرات Railway
TOKEN = os.getenv('DISCORD_TOKEN')
SERVER_IP = os.getenv('SERVER_IP') or os.getenv('SERVER_ID') # يقرأ الآيبي حتى لو كان الاسم القديم
SERVER_PORT = os.getenv('SERVER_PORT')
CHANNEL_ID = os.getenv('CHANNEL_ID')

if not TOKEN:
    raise ValueError("خطأ: لم يتم العثور على DISCORD_TOKEN")

intents = discord.Intents.default()
bot = discord.Client(intents=intents)
message_id = None

@bot.event
async def on_ready():
    print(f'تم تشغيل بوت {bot.user.name} بنجاح!')
    update_server_status.start()

@tasks.loop(minutes=3)
async def update_server_status():
    global message_id
    if not CHANNEL_ID:
        return
        
    channel = bot.get_channel(int(CHANNEL_ID))
    if not channel:
        print("لم يتم العثور على القناة")
        return

    embed = discord.Embed(
        title="A19 ASA Server Status",
        description="حالة السيرفر المباشرة وتفاصيل التشغيل",
        color=discord.Color.green()
    )

    # رابط الاستعلام المباشر
    url = f"https://api.gamedig.org/query?type=arksa&host={SERVER_IP}&port={SERVER_PORT}"
    
    try:
        # verify=False تحل مشكلة الـ certificate verify failed نهائياً وتمنع الكراش
        response = requests.get(url, verify=False, timeout=10).json()
        
        if 'error' not in response:
            players = len(response.get('players', []))
            max_players = response.get('maxplayers', 50)
            server_name = response.get('name', 'A19 ARK Server')
            
            embed.add_field(name="🔹 حالة السيرفر", value="```🟢 متصل```", inline=False)
            embed.add_field(name="👥 عدد اللاعبين", value=f"``` {players} / {max_players} ```", inline=False)
            embed.add_field(name="📍 اسم السيرفر", value=f"``` {server_name} ```", inline=False)
        else:
            embed.color = discord.Color.red()
            embed.add_field(name="🔹 حالة السيرفر", value="```🔴 مغلق أو تحت الصيانة```", inline=False)
            
    except Exception as e:
        embed.color = discord.Color.red()
        embed.add_field(name="🔹 حالة السيرفر", value="```🔴 السيرفر لا يستجيب حالياً```", inline=False)

    embed.set_footer(text="يتم التحديث تلقائياً كل 3 دقائق")

    try:
        if message_id is None:
            msg = await channel.send(embed=embed)
            message_id = msg.id
        else:
            try:
                msg = await channel.fetch_message(message_id)
                await msg.edit(embed=embed)
            except discord.NotFound:
                msg = await channel.send(embed=embed)
                message_id = msg.id
    except Exception as ex:
        print(f"خطأ في إرسال الرسالة: {ex}")

bot.run(TOKEN)

