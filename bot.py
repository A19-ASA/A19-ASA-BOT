import os
import discord
from discord.ext import tasks
import requests

TOKEN = os.getenv('DISCORD_TOKEN')
SERVER_ID = os.getenv('SERVER_ID') or os.getenv('SERVER_IP') # بيقرأ رقم السيرفر من خانة الآيبي أو السيرفر آيدي
CHANNEL_ID = os.getenv('CHANNEL_ID')

intents = discord.Intents.default()
bot = discord.Client(intents=intents)
message_id = None

@bot.event
async def on_ready():
    print(f'🟢 البوت متصل ومستقر عبر نظام Nitrado API باسم: {bot.user.name}')
    if not update_server_status.is_running():
        update_server_status.start()

@tasks.loop(minutes=3)
async def update_server_status():
    global message_id
    
    if not TOKEN or not SERVER_ID or not CHANNEL_ID:
        print("⚠️ المتvariables ناقصة في Railway.")
        return

    try:
        channel = bot.get_channel(int(CHANNEL_ID))
        if not channel: return
    except: return

    embed = discord.Embed(
        title="A19 ASA Server Status",
        description="حالة السيرفر المباشرة وتفاصيل التشغيل",
        color=discord.Color.green()
    )

    try:
        # قراءة البيانات عبر الـ API العام لنترادو بدون تعقيد بورتات
        url = f"https://api.nitrado.net/gameserver/query_by_id/{SERVER_ID}"
        response = requests.get(url, timeout=10).json()
        
        if response and response.get('status') == 'success':
            data = response.get('data', {}).get('server', {})
            
            # التأكد من حالة السيرفر إذا كان أونلاين
            is_online = data.get('status') == 'started'
            server_name = data.get('name', 'A19 ARK Server')
            players = data.get('players_current', 0)
            max_players = data.get('players_max', 50)
            
            if is_online:
                embed.add_field(name="🔹 حالة السيرفر", value="```🟢 متصل```", inline=False)
                embed.add_field(name="👥 عدد اللاعبين", value=f"``` {players} / {max_players} ```", inline=False)
                embed.add_field(name="📍 اسم السيرفر", value=f"``` {server_name} ```", inline=False)
            else:
                embed.color = discord.Color.red()
                embed.add_field(name="🔹 حالة السيرفر", value="```🔴 مغلق أو تحت الصيانة```", inline=False)
        else:
            raise Exception("فشل قراءة الـ API")
            
    except Exception as e:
        print(f"📡 خطأ في جلب بيانات نترادو: {e}")
        embed.color = discord.Color.red()
        embed.add_field(name="🔹 حالة السيرفر", value="```🔴 السيرفر لا يستجيب حالياً```", inline=False)
        embed.add_field(name="⚠️ تنبيه", value="```تأكد من معرف السيرفر (SERVER_ID) في ريلواي```", inline=False)

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
        print(f"خطأ ديسكورد: {ex}")

try:
    bot.run(TOKEN)
except Exception as e:
    print(f"خطأ تشغيل: {e}")
