import os
import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'تم تشغيل البوت بنجاح باسم {bot.user.name}')
    # يخلي حالة البوت في الديسكورد شغال دايماً باسم سيرفرك
    await bot.change_presence(activity=discord.Game(name="A19 ASA"))

@bot.command()
async def status(ctx):
    await ctx.send("سيرفر A19 شغال وبأفضل حال! 🚀")

TOKEN = os.getenv('DISCORD_TOKEN')
if TOKEN:
    bot.run(TOKEN)
else:
    print("خطأ: لم يتم العثور على DISCORD_TOKEN!")
