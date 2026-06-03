import os
import discord
from discord.ext import tasks
import requests

TOKEN = os.getenv('DISCORD_TOKEN')
SERVER_IP = os.getenv('SERVER_IP')
SERVER_PORT = os.getenv('SERVER_PORT')
CHANNEL_ID = os.getenv('CHANNEL_ID')

intents = discord.Intents.default()
bot = discord.Client(intents=intents)
message_id = None

@bot.event
async def on_ready():
    print(f'🟢 البوت متصل ومستقر عبر نظام الفحص العام باسم: {bot.user.name}')
    if not update_server_status.is_running():
        update_server_status.start()

@tasks.loop(minutes=3)
async def update_server_status():
    global message_id
    
    if not TOKEN or not SERVER_IP or not SERVER_PORT or not CHANNEL_ID:
        print("⚠️ تنبيه: بعض المتغيرات ناقصة في لوحة Railway!")
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
        # الفحص عبر الـ API المفتوح والمتوافق مع سيرفرات أرك اسندد ونترادو
        url = f"https://api.battlemetrics.com/servers?filter[search]={SERVER_IP}"
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10).json()
        
        server_found = False
        if response and 'data' in response and len(response['data']) > 0:
            for server in response['data']:
                attributes = server.get('attributes', {})
                # التأكد من مطابقة البورت لضمان جلب سيرفرك بالظبط
                if str(attributes.get('port')) == str(SERVER_PORT) or str(SERVER_PORT) in str(attributes.get('ip')):
                    server_name = attributes.get('name', 'A19 PRIMAL NEMESIS [Arab]')
                    players = attributes.get('players', 0)
                    max_players = attributes.get('maxPlayers', 20)
                    status = attributes.get('status', 'online')
                    
                    if status == 'online':
                        embed.add_field(name="🔹 حالة السيرفر", value="```🟢 متصل وجاهز للعب```", inline=False)
                        embed.add_field(name="👥 عدد اللاعبين", value=f"``` {players} / {max_players} ```", inline=False)
                        embed.add_field(name="📍 اسم السيرفر", value=f"``` {server_name} ```", inline=False)
                    else:
                        embed.color = discord.Color.red()
                        embed.add_field(name="🔹 حالة السيرفر", value="```🔴 مغلق أو تحت الصيانة```", inline=False)
                    
                    server_found = True
                    break

        if not server_found:
            # طريقة رديفة ثانية وسريعة عبر مسار الاستعلام العام
            url_backup = f"https://api.mcsrvstat.us/3/{SERVER_IP}:{SERVER_PORT}"
            res_b = requests.get(url_backup, timeout=10).json()
            if res_b and res_b.get('online') is True:
                embed.add_field(name="🔹 حالة السيرفر", value="```🟢 متصل وجاهز للعب```", inline=False)
                embed.add_field(name="👥 عدد اللاعبين", value=f"``` {res_b.get('players', {}).get('online', 0)} / {res_b.get('players', {}).get('max', 20)} ```", inline=False)
                embed.add_field(name="📍 اسم السيرفر", value="``` A19 PRIMAL NEMESIS [Arab] ```", inline=False)
            else:
                raise Exception("سيرفر أرك لم يظهر في القائمة العامة بعد")
                
    except Exception as e:
        print(f"📡 خطأ فحص: {e}")
        embed.color = discord.Color.red()
        embed.add_field(name="🔹 حالة السيرفر", value="```🔴 السيرفر لا يستجيب حالياً```", inline=False)
        embed.add_field(name="⚠️ تنبيه", value="```جاري جلب البيانات من قائمة السيرفرات...```", inline=False)

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
