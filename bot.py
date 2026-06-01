import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'البوت شغال كـ {bot.user.name}')
    await bot.change_presence(activity=discord.Game(name="سيرفر A19 بانتظار تحديثك!"))

@bot.command()
async def setstatus(ctx, *, status: str):
    # هذا الأمر يخليك تغير الحالة من الديسكورد
    # مثال: اكتب في الديسكورد !setstatus 5/20 لاعب
    await bot.change_presence(activity=discord.Game(name=status))
    await ctx.send(f"تم تحديث الحالة إلى: {status}")

import os
bot.run(os.getenv('DISCORD_TOKEN'))
