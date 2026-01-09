import os
import discord
from discord.ext import commands

TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="/", intents=intents)


# =========================================
#              ON READY
# =========================================
@bot.event
async def on_ready():
    print(f"Bot is online as {bot.user}")


# =========================================
#              HELP COMMAND
# =========================================
@bot.command(name="myhelp")
async def myhelp(ctx):
    embed = discord.Embed(
        title="Available Commands",
        description=(
            "**/pay <amount+fee>** - Calculates fee\n"
            "**/percent <percent> <amount>** - Calculate percent of an amount\n"
            "**/roleadd <role> <user>** - Adds a role\n"
            "**/roleremove <role> <user>** - Removes a role\n"
        ),
        color=0x00ff00
    )

    await ctx.reply(embed=embed, mention_author=True)


# =========================================
#          PAY CALCULATOR (5m+5)
# =========================================
@bot.command(name="pay")
async def pay(ctx, input_value: str):
    """
    Format example: 5m+5 or 10b+2
    """

    def convert(x):
        x = x.lower()
        if "m" in x:
            return float(x.replace("m", "")) * 1_000_000
        elif "b" in x:
            return float(x.replace("b", "")) * 1_000_000_000
        else:
            return float(x)

    try:
        base, percent = input_value.split("+")
        base_value = convert(base)
        percent_value = float(percent)

        total = base_value + (base_value * percent_value / 100)

        await ctx.reply(
            f"💰 **Payment Result**\n"
            f"Base: `{base_value:,.0f}`\n"
            f"Fee: `{percent_value}%`\n"
            f"Total: `{total:,.0f}`",
            mention_author=True
        )

    except:
        await ctx.reply("❌ Invalid format! Use: `/pay 5m+5`", mention_author=True)


# =========================================
#        PERCENT CALCULATOR (2% of 500m)
# =========================================
@bot.command(name="percent")
async def percent(ctx, percent_value: float, amount: str):
    def convert(x):
        x = x.lower()
        if "m" in x:
            return float(x.replace("m", "")) * 1_000_000
        elif "b" in x:
            return float(x.replace("b", "")) * 1_000_000_000
        else:
            return float(x)

    try:
        amount_value = convert(amount)
        result = amount_value * (percent_value / 100)

        await ctx.reply(
            f"📊 **Percent Calculation**\n"
            f"{percent_value}% of `{amount_value:,.0f}` = **{result:,.0f}**",
            mention_author=True
        )

    except:
        await ctx.reply("❌ Invalid amount format! Example: `/percent 2 500m`")


# =========================================
#             ROLE ADD
# =========================================
@bot.command(name="roleadd")
async def roleadd(ctx, role_name: str, member: discord.Member = None):
    if member is None:
        member = ctx.author

    role = discord.utils.get(ctx.guild.roles, name=role_name)
    if role is None:
        return await ctx.reply("❌ Role not found.", mention_author=True)

    await member.add_roles(role)
    await ctx.reply(f"✅ Added role **{role_name}** to {member.mention}", mention_author=True)


# =========================================
#             ROLE REMOVE
# =========================================
@bot.command(name="roleremove")
async def roleremove(ctx, role_name: str, member: discord.Member = None):
    if member is None:
        member = ctx.author

    role = discord.utils.get(ctx.guild.roles, name=role_name)
    if role is None:
        return await ctx.reply("❌ Role not found.", mention_author=True)

    await member.remove_roles(role)
    await ctx.reply(f"❌ Removed role **{role_name}** from {member.mention}", mention_author=True)


# =========================================
#              RUN BOT
# =========================================
if TOKEN is None:
    print("ERROR: TOKEN missing in Railway!")
else:
    bot.run(TOKEN)
