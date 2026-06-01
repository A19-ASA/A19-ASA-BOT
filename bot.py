import os
import asyncio
import discord
from discord.ext import tasks
import a2s

# جلب المتغيرات من Railway
TOKEN = os.getenv('MTUxMDQ1NTU0ODc1NDI2NDE1NQ.GRX_1A.lwR7hXU1FRs9E93aGXpS0nAb10EfiCJTlZfMr0')
SERVER_IP = os.getenv('SERVER_IP') or os.getenv('19258802')
SERVER_PORT = os.getenv('21')
CHANNEL_ID = os.getenv('1506832226367701163')

if not TOKEN:
    raise ValueError("خطأ: لم يتم العثور على DISCORD_TOKEN في المتغيرات")

intents = discord.Intents.default()
bot = discord.Client(intents=intents)
message_id = None

@bot.event
async def on_ready():
    print(f'🟢 تم تشغيل بوت {bot.user.name} بنجاح والنظام مستقر!')
    if not update_server_status.is_running():
        update_server_status.start()

@tasks.loop(minutes=3)
async def update_server_status():
    global message_id
    
    # التأكد من وجود البيانات لمنع الكراش
    if not CHANNEL_ID or not SERVER_IP or not SERVER_PORT:
        print("⚠️ المتغيرات ناقصة في Railway، يرجى التأكد منها.")
        return
        
    channel = bot.get_channel(int(CHANNEL_ID))
    if not channel:
        print("⚠️ لم يتم العثور على القناة في الديسكورد.")
        return

    # تجهيز رسالة الـ Embed المنسقة
    embed = discord.Embed(
        title="A19 ASA Server Status",
        description="حالة السيرفر المباشرة وتفاصيل التشغيل",
        color=discord.Color.green()
    )

    try:
        # فحص السيرفر بشكل غير متزامن (Async) مستحيل يعلق البوت
        info = await a2s.ainfo((SERVER_IP, int(SERVER_PORT)), timeout=5)
        
        players = info.players
        max_players = info.max_players
        server_name = info.server_name

        embed.add_field(name="🔹 حالة السيرفر", value="```🟢 متصل```", inline=False)
        embed.add_field(name="👥 عدد اللاعبين", value=f"``` {players} / {max_players} ```", inline=False)
        embed.add_field(name="📍 اسم السيرفر", value=f"``` {server_name} ```", inline=False)
        
    except Exception as e:
        # نظام الحماية: لو السيرفر طافي أو ما رد، البوت يكمل شغل وما يكرش
        print(f"📡 السيرفر لا يستجيب حالياً (ربما طافي أو يعيد التشغيل): {e}")
        embed.color = discord.Color.red()
        embed.add_field(name="🔹 حالة السيرفر", value="```🔴 مغلق أو تحت الصيانة```", inline=False)
        embed.add_field(name="⚠️ تنبيه", value="```لا يمكن الاتصال بخادم اللعبة حالياً```", inline=False)

    embed.set_footer(text="يتم التحديث تلقائياً كل 3 دقائق")

    # إرسال أو تعديل الرسالة الثابتة لمنع التكرار
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
        print(f"❌ خطأ أثناء التعامل مع رسائل الديسكورد: {ex}")

bot.run(TOKEN)
