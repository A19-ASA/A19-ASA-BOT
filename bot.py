import os
import discord
from discord.ext import tasks
import valve.source.a2s

# جلب المتغيرات من Railway
TOKEN = os.getenv('DISCORD_TOKEN')
SERVER_IP = os.getenv('SERVER_IP')
SERVER_PORT = int(os.getenv('SERVER_PORT'))  # البورت يجب أن يكون رقماً
CHANNEL_ID = int(os.getenv('CHANNEL_ID'))

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
    channel = bot.get_channel(CHANNEL_ID)
    if not channel:
        print("القناة غير موجودة، تأكد من CHANNEL_ID")
        return

    # إنشاء الـ Embed بالتنسيق الاحترافي مثل الصورة
    embed = discord.Embed(
        title="A19 ASA Server Status",
        description="حالة السيرفر المباشرة وتفاصيل التشغيل",
        color=discord.Color.green()
    )

    try:
        # الاتصال المباشر بالسيرفر عبر الآيبي والبورت لجلب البيانات
        with valve.source.a2s.ServerQuerier((SERVER_IP, SERVER_PORT)) as querier:
            info = querier.info()
            players = info["players"]
            max_players = info["max_players"]
            server_name = info["server_name"]

            embed.add_field(name="🔹 حالة السيرفر", value="```🟢 متصل```", inline=False)
            embed.add_field(name="👥 عدد اللاعبين", value=f"``` {players} / {max_players} ```", inline=False)
            embed.add_field(name="📍 اسم السيرفر", value=f"``` {server_name} ```", inline=False)
            embed.set_footer(text="يتم التحديث تلقائياً كل 3 دقائق")

    except Exception as e:
        # في حال كان السيرفر طافي أو لم يستجب
        print(f"السيرفر لم يستجب: {e}")
        embed.color = discord.Color.red()
        embed.add_field(name="🔹 حالة السيرفر", value="```🔴 مغلق أو تحت الصيانة```", inline=False)
        embed.set_footer(text="يتم التحديث تلقائياً كل 3 دقائق")

    # إرسال أو تعديل الرسالة لمنع التكرار
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
