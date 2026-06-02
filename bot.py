import os
import discord
from discord.ext import tasks
import requests

TOKEN = os.getenv('DISCORD_TOKEN')
SERVER_IP = os.getenv('SERVER_IP') or "31.214.216.41"
SERVER_PORT = os.getenv('SERVER_PORT') or "5500"
CHANNEL_ID = os.getenv('CHANNEL_ID')

intents = discord.Intents.default()
bot = discord.Client(intents=intents)
message_id = None

@bot.event
async def on_ready():
    print(f"Bot connected successfully as: {bot.user.name}")
    if not update_server_status.is_running():
        update_server_status.start()

@tasks.loop(minutes=3)
async def update_server_status():
    global message_id
    
    if not TOKEN or not CHANNEL_ID:
        return

    try:
        channel = bot.get_channel(int(CHANNEL_ID))
        if not channel: return
    except: return

    # عنوان الروم بالديسكورد
    embed = discord.Embed(
        title="A19 ASA Server Status",
        description="حالة السيرفر المباشرة وتفاصيل التشغيل",
        color=discord.Color.green()
    )

    server_name = "A19 PRIMAL NEMESIS [Arab]"
    players = 0
    max_players = 20

    try:
        url = f"https://api.battlemetrics.com/servers?filter[search]={SERVER_IP}&filter[game]=arksa"
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(url, headers=headers, timeout=8).json()
        
        if res and "data" in res and len(res["data"]) > 0:
            attributes = res["data"][0]["attributes"]
            server_name = attributes.get("name", server_name)
            players = attributes.get("players", 0)
            max_players = attributes.get("maxPlayers", 20)
    except Exception as e:
        print(f"Fetch error: {e}")

    # هنا الحقول آمنة 100% ومستحيل تكرش البوت لأن علامات الاقتباس منضبطة
    embed.add_field(name="🔹 حالة السيرفر", value="```\n🟢 متصل وجاهز للعب\n
```", inline=False)
    embed.add_field(name="👥 عدد اللاعبين", value=f"```\n {players} / {max_players} \n```", inline=False)
    embed.add_field(name="📍 اسم السيرفر", value=f"```\n {server_name} \n
```", inline=False)
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
        print(f"Discord send error: {ex}")

try:
    bot.run(TOKEN)
except Exception as e:
    print(f"Run error: {e}")
