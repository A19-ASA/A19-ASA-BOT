import os
import discord
from discord.ext import tasks
import requests

TOKEN = os.getenv('DISCORD_TOKEN')
SERVER_ID = os.getenv('SERVER_ID')
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
        print("⚠️ المتغيرات ناقصة في Railway.")
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
        # استخدام رابط الـ API المباشر لمعلومات سيرفر اللعبة في نترادو
        url = f"https://api.nitrado.net/gameserver/gameserver/{SERVER_ID}"
        response = requests.get(url, timeout=10).json()
        
        if response and response.get('status') == 'success':
            data = response.get('data', {}).get('gameserver', {})
            
            # قراءة تفاصيل التشغيل واللاعبين بالملي
            status_text = data.get('status', '') # بدأ أو غيره
            server_name = data.get('settings', {}).get('config', {}).get('server-name', 'A19 ARK Server')
            
            # قراءة المتصلين
            players = data.get('query', {}).get('player_current', 0)
            max_players = data.get('query', {}).get('player_max', 20)
            
            if status_text == 'started':
                embed.add_field(name="🔹 حالة السيرفر", value="```🟢 متصل```", inline=False)
                embed.add_field(name="👥 عدد اللاعبين", value=f"``` {players} / {max_players} ```", inline=False)
                embed.add_field(name="📍 اسم السيرفر", value=f"``` {server_name} ```", inline=False)
            else:
                embed.color = discord.Color.red()
                embed.add_field(name="🔹 حالة السيرفر", value=f"```🔴 {status_text}```", inline=False)
        else:
            # إذا لم تكن تفاصيل السيرفر عامة، نقرأ من الـ وب هوك المباشر للوحة
            url_backup = f"https://api.nitrado.net/gameserver/query_by_id/{SERVER_ID}"
            res_b = requests.get(url_backup, timeout=10).json()
            if res_b and res_b.get('status') == 'success':
                d = res_b.get('data', {}).get('server', {})
                embed.add_field(name="🔹 حالة السيرفر", value="```🟢 متصل```", inline=False)
                embed.add_field(name="👥 عدد اللاعبين", value=f"``` {d.get('players_current', 0)} / {d.get('players_max', 20)} ```", inline=False)
                embed.add_field(name="📍 اسم السيرفر", value=f"``` {d.get('name', 'A19 ARK Server')} ```", inline=False)
            else:
                raise Exception("API Return error")
                
    except Exception as e:
        print(f"📡 خطأ في جلب بيانات نترادو: {e}")
        embed.color = discord.Color.red()
        embed.add_field(name="🔹 حالة السيرفر", value="```🔴 السيرفر لا يستجيب حالياً```", inline=False)
        embed.add_field(name="⚠️ تنبيه", value="```جاري تحديث الاتصال بلوحة التحكم...```", inline=False)

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
