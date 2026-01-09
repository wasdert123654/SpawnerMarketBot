import discord
from discord.ext import commands
import os
import re

# ===== CONFIG =====
COMMAND_PREFIX = "!"
CUSTOMER_ROLE_ID = 1446629248491327550
ADMIN_ROLE_IDS = [1446628032541491384, 1446628032541491384]

# Get token from environment
TOKEN = os.getenv("TOKEN")

# ===== BOT SETUP =====
intents = discord.Intents.default()
intents.members = True            # Needed for role commands
intents.message_content = True    # Needed for !commands to work

bot = commands.Bot(command_prefix=COMMAND_PREFIX, help_command=None, intents=intents)

# ===== USER DATA =====
igns = {}  # Stores user's IGN

# ===== UTILITIES =====
def parse_number(value: str):
    """Convert k/m/b shorthand to integer"""
    value = value.lower().replace(",", "").strip()
    if value.endswith("k"):
        return int(float(value[:-1]) * 1_000)
    elif value.endswith("m"):
        return int(float(value[:-1]) * 1_000_000)
    elif value.endswith("b"):
        return int(float(value[:-1]) * 1_000_000_000)
    else:
        return int(value)

def calculate_expression(expr: str):
    """Parse expression with k/m/b and calculate"""
    def replacer(match):
        return str(parse_number(match.group(0)))
    expr = re.sub(r"\d+(\.\d+)?[kKmMbB]", replacer, expr)
    return int(eval(expr))

# ===== EVENTS =====
@bot.event
async def on_ready():
    print(f"Bot is online as {bot.user}!")

# ===== COMMANDS =====

# Custom help
@bot.command()
async def help(ctx):
    embed = discord.Embed(
        title="Spawner Market Bot - Help",
        description="List of available commands:",
        color=discord.Color.blue()
    )
    embed.add_field(name="!calc <expression>", value="Calculates values like 1+1 or 5m+2k", inline=False)
    embed.add_field(name="!acalc <expression>", value="Calculates and outputs /pay <your_ign> <amount>", inline=False)
    embed.add_field(name="!ign <username>", value="Set your in-game name for acalc", inline=False)
    embed.add_field(name="!roleadd customer @user", value="Add Customer role (admin only)", inline=False)
    embed.add_field(name="!roleremove customer @user", value="Remove Customer role (admin only)", inline=False)
    await ctx.reply(embed=embed, mention_author=False)

# Set IGN
@bot.command()
async def ign(ctx, *, ign_name):
    igns[ctx.author.id] = ign_name
    embed = discord.Embed(
        title="IGN Set!",
        description=f"Your IGN is now: `{ign_name}`",
        color=discord.Color.green()
    )
    await ctx.reply(embed=embed, mention_author=False)

# !calc command
@bot.command()
async def calc(ctx, *, expression):
    try:
        total = calculate_expression(expression)
    except Exception:
        await ctx.reply("Invalid expression!", mention_author=False)
        return
    embed = discord.Embed(
        title="Calculation Result",
        description=f"{total:,}",
        color=discord.Color.green()
    )
    await ctx.reply(embed=embed, mention_author=False)

# !acalc command
@bot.command()
async def acalc(ctx, *, expression):
    user_ign = igns.get(ctx.author.id)
    if not user_ign:
        await ctx.reply("Set your IGN first with !ign <username>", mention_author=False)
        return
    try:
        total = calculate_expression(expression)
    except Exception:
        await ctx.reply("Invalid expression!", mention_author=False)
        return
    embed = discord.Embed(
        title="Calculation Result",
        description=f"/pay {user_ign} {total:,}",
        color=discord.Color.green()
    )
    await ctx.reply(embed=embed, mention_author=False)

# Add customer role
@bot.command(name="roleadd")
async def roleadd_customer(ctx, member: discord.Member = None):
    if ctx.author.id not in ADMIN_ROLE_IDS:
        await ctx.reply("You do not have permission to use this command.", mention_author=False)
        return
    if not member:
        await ctx.reply("Please mention a user.", mention_author=False)
        return
    role = ctx.guild.get_role(CUSTOMER_ROLE_ID)
    if not role:
        await ctx.reply("Customer role not found.", mention_author=False)
        return
    await member.add_roles(role)
    embed = discord.Embed(
        title="Role Added",
        description=f"Added `{role.name}` role to {member.display_name}",
        color=discord.Color.green()
    )
    await ctx.reply(embed=embed, mention_author=False)

# Remove customer role
@bot.command(name="roleremove")
async def roleremove_customer(ctx, member: discord.Member = None):
    if ctx.author.id not in ADMIN_ROLE_IDS:
        await ctx.reply("You do not have permission to use this command.", mention_author=False)
        return
    if not member:
        await ctx.reply("Please mention a user.", mention_author=False)
        return
    role = ctx.guild.get_role(CUSTOMER_ROLE_ID)
    if not role:
        await ctx.reply("Customer role not found.", mention_author=False)
        return
    await member.remove_roles(role)
    embed = discord.Embed(
        title="Role Removed",
        description=f"Removed `{role.name}` role from {member.display_name}",
        color=discord.Color.red()
    )
    await ctx.reply(embed=embed, mention_author=False)

# ===== RUN BOT =====
bot.run(TOKEN)
