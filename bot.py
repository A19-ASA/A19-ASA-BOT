import os
import discord
from discord.ext import tasks
import requests

# جلب المتغيرات بأمان تام
TOKEN = os.getenv('DISCORD_TOKEN')
SERVER_IP = os.getenv('SERVER_IP') or os.getenv('SERVER_ID')
SERVER_PORT = os.getenv('SERVER_PORT')
CHANNEL_ID = os.getenv('CHANNEL_ID')

intents = discord.Intents.default()
bot = discord.Client(intents=intents)
message_id = None

@bot.event
async def on_ready():
    print(f'🟢 البوت شغال ومستقر بالكامل باسم: {bot.user.name}')
    if not update_server_status.is_running():
        update_server_status.start()

@tasks.loop(minutes=3)
async def update_server_status():
    global message_id
    
    # حماية 1: منع الكراش لو المتغيرات ناقصة أو ما انحفظت في ريلواي
    if not TOKEN or not SERVER_IP or not SERVER_PORT or not CHANNEL_ID:
        print("⚠️ تنبيه: بعض المتغيرات ناقصة في لوحة Railway أو لم يتم حفظها بالأخضر!")
        return

    try:
        channel = bot.get_channel(int(CHANNEL_ID))
        if not channel:
            print("⚠️ تنبيه: لم يتم العثور على القناة بالديسكورد، تأكد من الـ ID.")
            return
    except Exception as e:
        print(f"⚠️ خطأ في قراءة الـ Channel ID: {e}")
        return

    embed = discord.Embed(
        title="A19 ASA Server Status",
        description="حالة السيرفر المباشرة وتفاصيل التشغيل",
        color=discord.Color.green()
    )

    # حماية 2: الفحص داخل try/except مخصص عشان لو الـ API علق البوت ما يكرش
    try:
        url = f"https://api.gamedig.org/query?type=arksa&host={SERVER_IP}&port={SERVER_PORT}"
        response = requests.get(url, verify=False, timeout=8).json()
        
        if response and 'error' not in response:
            players = len(response.get('players', []))
            max_players = response.get('maxplayers', 50)
            server_name = response.get('name', 'A19 ARK Server')
            
            embed.add_field(name="🔹 حالة السيرفر", value="```🟢 متصل```", inline=False)
            embed.add_field(name="👥 عدد اللاعبين", value=f"``` {players} / {max_players} ```", inline=False)
            embed.add_field(name="📍 اسم السيرفر", value=f"``` {server_name} ```", inline=False)
        else:
            embed.color = discord.Color.red()
            embed.add_field(name="🔹 حالة السيرفر", value="```🔴 مغلق أو تحت الصيانة```", inline=False)
    except Exception as api_error:
        print(f"📡 خطأ اتصال بالسيرفر (البوت مستمر ولن يكرش): {api_error}")
        embed.color = discord.Color.red()
        embed.add_field(name="🔹 status", value="```🔴 السيرفر لا يستجيب حالياً```", inline=False)

    embed.set_footer(text="يتم التحديث تلقائياً كل 3 دقائق")

    # حماية 3: إرسال وتعديل الرسالة بدون كراشات
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
    except Exception as discord_error:
        print(f"❌ خطأ ديسكورد (البوت مستمر ولن يكرش): {discord_error}")

# حماية 4: تشغيل البوت داخل محاولة عامة لمنع الكراش النهائي
try:
    bot.run(TOKEN)
except Exception as main_error:
    print(f"🚨 خطأ حرج في التوكن أو التشغيل: {main_error}")
