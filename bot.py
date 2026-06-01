import os
import discord
from discord.ext import tasks
import requests

# جلب الإعدادات من متغيرات بيئة السيرفر في Railway
TOKEN = os.getenv('DISCORD_TOKEN')
SERVER_IP = os.getenv('SERVER_IP')
SERVER_PORT = os.getenv('SERVER_PORT')
CHANNEL_ID = os.getenv('CHANNEL_ID')

# التأكد من أن التوكن غير فارغ لمنع الكراش
if not TOKEN:
    raise ValueError("خطأ: لم يتم العثور على DISCORD_TOKEN في متغيرات Railway!")

intents = discord.Intents.default()
bot = discord.Client(intents=intents)
message_id = None

@bot.event
async def on_ready():
    print(f'تم تسجيل الدخول بنجاح باسم {bot.user.name}')
    update_server_status.start()

@tasks.loop(minutes=3)
async def update_server_status():
    global message_id
    if not CHANNEL_ID:
        print("خطأ: CHANNEL_ID غير محدد في المتغيرات.")
        return
        
    channel = bot.get_channel(int(CHANNEL_ID))
    if not channel:
        print("خطأ: لم يتم العثور على القناة المحددة بالديسكورد.")
        return

    # إنشاء الـ Embed الاحترافي المنسق
    embed = discord.Embed(
        title="A19 ASA Server Status",
        description="حالة السيرفر المباشرة وتفاصيل التشغيل",
        color=discord.Color.green()
    )

    # رابط استعلام يتخطى مشاكل الـ SSL والشهادات القديمة
    url = f"https://api.gamedig.org/query?type=arksa&host={SERVER_IP}&port={SERVER_PORT}"
    
    try:
        # verify=False تتخطى مشكلة الـ certificate verify failed بشكل نهائي ومضمون
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
            
        embed.set_footer(text="يتم التحديث تلقائياً كل 3 دقائق")

    except Exception as e:
        print(f"خطأ أثناء فحص السيرفر: {e}")
        embed.color = discord.Color.red()
        embed.add_field(name="🔹 حالة السيرفر", value="```🔴 السيرفر لا يستجيب حالياً```", inline=False)
        embed.set_footer(text="يتم التحديث تلقائياً كل 3 دقائق")

    # إرسال الرسالة أو تعديلها لمنع التكرار في الروم
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
        print(f"خطأ في التعامل مع رسائل الديسكورد: {ex}")

bot.run(TOKEN)

