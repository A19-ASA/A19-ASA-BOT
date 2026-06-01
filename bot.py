import os
import discord
from discord.ext import tasks
import valve.source.a2s

# جلب المتغيرات البيئية من Railway
TOKEN = os.getenv('DISCORD_TOKEN')
# هنا الكود يقرأ SERVER_IP أو SERVER_ID الاحتياطي عشان لو ما غيرت الاسم
SERVER_IP = os.getenv('SERVER_IP') or os.getenv('SERVER_ID')
SERVER_PORT = os.getenv('SERVER_PORT')
CHANNEL_ID = os.getenv('CHANNEL_ID')

if not TOKEN:
    raise ValueError("خطأ: لم يتم العثور على DISCORD_TOKEN")

intents = discord.Intents.default()
bot = discord.Client(intents=intents)
message_id = None

@bot.event
async def on_ready():
    print(f'تم تشغيل بوت {bot.user.name} بنجاح والاتصال مستقر!')
    update_server_status.start()

@tasks.loop(minutes=3)
async def update_server_status():
    global message_id
    if not CHANNEL_ID or not SERVER_IP or not SERVER_PORT:
        print("خطأ: بعض المتغيرات ناقصة في Railway")
        return
        
    channel = bot.get_channel(int(CHANNEL_ID))
    if not channel:
        print("لم يتم العثور على القناة المحددة")
        return

    # إنشاء الـ Embed المنسق والاحترافي لطلبك
    embed = discord.Embed(
        title="A19 ASA Server Status",
        description="حالة السيرفر المباشرة وتفاصيل التشغيل",
        color=discord.Color.green()
    )

    try:
        # الاتصال المباشر بالسيرفر عبر بروتوكول Steam الرسمي (A2S)
        # نقوم بتحويل البورت إلى رقم إجباري لمنع مشاكل النصوص
        server_address = (SERVER_IP, int(SERVER_PORT))
        
        with valve.source.a2s.ServerQuerier(server_address, timeout=10) as querier:
            info = querier.info()
            players = info["players"]
            max_players = info["max_players"]
            server_name = info["server_name"]
            
            embed.add_field(name="🔹 حالة السيرفر", value="```🟢 متصل```", inline=False)
            embed.add_field(name="👥 عدد اللاعبين", value=f"``` {players} / {max_players} ```", inline=False)
            embed.add_field(name="📍 اسم السيرفر", value=f"``` {server_name} ```", inline=False)
            
    except Exception as e:
        # في حال السيرفر طافي أو جاري التشغيل: الكود لن يكرش! بل سيعرض هذي الرسالة الحمراء
        print(f"السيرفر لم يستجب حالياً: {e}")
        embed.color = discord.Color.red()
        embed.add_field(name="🔹 حالة السيرفر", value="```🔴 مغلق أو تحت الصيانة```", inline=False)
        embed.add_field(name="⚠️ تنبيه", value="```لا يمكن الاتصال بخادم اللعبة حالياً```", inline=False)

    embed.set_footer(text="يتم التحديث تلقائياً كل 3 دقائق")

    # إرسال وتحديث الرسالة في الديسكورد
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
        print(f"خطأ في إرسال الرسالة إلى الديسكورد: {ex}")

bot.run(TOKEN)
