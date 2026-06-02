import os, discord, requests
from discord.ext import tasks

TOKEN, SERVER_IP, CHANNEL_ID = os.getenv('DISCORD_TOKEN'), os.getenv('SERVER_IP') or "31.214.216.41", os.getenv('CHANNEL_ID')
intents = discord.Intents.default()
bot = discord.Client(intents=intents)
message_id = None

@bot.event
async def on_ready():
    print("Bot is ready")
    if not update_server_status.is_running(): update_server_status.start()

@tasks.loop(minutes=3)
async def update_server_status():
    global message_id
    if not TOKEN or not CHANNEL_ID: return
    try:
        channel = bot.get_channel(int(CHANNEL_ID))
        if not channel: return
    except: return
    
    embed = discord.Embed(title="A19 ASA Server Status", description="Live server details", color=discord.Color.green())
    s_name, p, m_p = "A19 PRIMAL NEMESIS", 0, 20
    
    try:
        res = requests.get(f"https://api.battlemetrics.com/servers?filter[search]={SERVER_IP}&filter[game]=arksa", headers={"User-Agent": "Mozilla"}, timeout=8).json()
        if res and "data" in res and len(res["data"]) > 0:
            attr = res["data"][0]["attributes"]
            s_name, p, m_p = attr.get("name", s_name), attr.get("players", 0), attr.get("maxPlayers", 20)
    except: pass

    embed.add_field(name="Server Status", value="```\nONLINE\n```", inline=False)
    embed.add_field(name="Players Online", value=f"```\n {p} / {m_p} \n```", inline=False)
    embed.add_field(name="Server Name", value=f"```\n {s_name} \n```", inline=False)
    embed.set_footer(text="Updated every 3 minutes")

    try:
        if message_id is None:
            msg = await channel.send(embed=embed)
            message_id = msg.id
        else:
            try:
                msg = await channel.fetch_message(message_id)
                await msg.edit(embed=embed)
            except:
                msg = await channel.send(embed=embed)
                message_id = msg.id
    except: pass

try:
    bot.run(TOKEN)
except Exception as e:
    print(e)
