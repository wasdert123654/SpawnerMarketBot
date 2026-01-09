import os
import discord
from discord.ext import commands

TOKEN = os.getenv("TOKEN")

CUSTOMER_ROLE_ID = 1446629248491327550
ADMIN_ROLE_IDS = [1446628032541491384, 1446628032541491384]

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Store IGN per user
user_igns = {}


@bot.event
async def on_ready():
    print(f"Bot is online as {bot.user}!")


def is_admin(ctx):
    return any(role.id in ADMIN_ROLE_IDS for role in ctx.author.roles)


# ----------------------------- IGN COMMAND -----------------------------

@bot.command()
async def ign(ctx, *, ign_name=None):
    if ign_name is None:
        return await ctx.reply("❌ Please provide your IGN. Example: `!ign MyName`")

    user_igns[ctx.author.id] = ign_name

    embed = discord.Embed(
        title="IGN Saved",
        description=f"Your IGN has been set to **{ign_name}**",
        color=discord.Color.green()
    )
    await ctx.reply(embed=embed)


# ----------------------------- CALC COMMAND -----------------------------

@bot.command()
async def calc(ctx, amount=None):
    if amount is None:
        return await ctx.reply("❌ Please provide an amount. Example: `!calc 2m`")

    embed = discord.Embed(
        title="Calculation",
        description=f"**Amount: {amount}**",
        color=discord.Color.blue()
    )
    await ctx.reply(embed=embed)


# ----------------------------- ACALC COMMAND -----------------------------

@bot.command()
async def acalc(ctx, amount=None):
    if amount is None:
        return await ctx.reply("❌ Please provide an amount. Example: `!acalc 2m`")

    if ctx.author.id not in user_igns:
        return await ctx.reply("❌ You must set your IGN first using: `!ign <name>`")

    ign_name = user_igns[ctx.author.id]

    embed = discord.Embed(
        title="Auto Calculation",
        description=f"/pay **{ign_name}** {amount}",
        color=discord.Color.gold()
    )
    await ctx.reply(embed=embed)


# ----------------------------- ROLE ADD COMMAND -----------------------------

@bot.command()
async def roleadd(ctx, role_name=None, member: discord.Member = None):
    if not is_admin(ctx):
        return await ctx.reply("❌ You do not have permission to use this command.")

    if role_name != "customer":
        return await ctx.reply("❌ Only the `customer` role can be added.")

    if member is None:
        return await ctx.reply("❌ Please mention a user. Example: `!roleadd customer @user`")

    role = ctx.guild.get_role(CUSTOMER_ROLE_ID)
    await member.add_roles(role)

    embed = discord.Embed(
        title="Role Added",
        description=f"Added **Customer** role to {member.mention}",
        color=discord.Color.green()
    )
    await ctx.reply(embed=embed)


# ----------------------------- ROLE REMOVE COMMAND -----------------------------

@bot.command()
async def roleremove(ctx, role_name=None, member: discord.Member = None):
    if not is_admin(ctx):
        return await ctx.reply("❌ You do not have permission to use this command.")

    if role_name != "customer":
        return await ctx.reply("❌ Only the `customer` role can be removed.")

    if member is None:
        return await ctx.reply("❌ Please mention a user. Example: `!roleremove customer @user`")

    role = ctx.guild.get_role(CUSTOMER_ROLE_ID)
    await member.remove_roles(role)

    embed = discord.Embed(
        title="Role Removed",
        description=f"Removed **Customer** role from {member.mention}",
        color=discord.Color.red()
    )
    await ctx.reply(embed=embed)


# ----------------------------- HELP COMMAND -----------------------------

@bot.command(name="help")
async def help_command(ctx):
    embed = discord.Embed(
        title="Spawner Market Bot Commands",
        color=discord.Color.blurple()
    )

    embed.add_field(name="!ign <name>", value="Set your IGN.", inline=False)
    embed.add_field(name="!calc <amount>", value="Shows an amount.", inline=False)
    embed.add_field(name="!acalc <amount>", value="Shows /pay with your saved IGN.", inline=False)
    embed.add_field(name="!roleadd customer @user", value="Admin only – adds Customer role.", inline=False)
    embed.add_field(name="!roleremove customer @user", value="Admin only – removes Customer role.", inline=False)

    await ctx.reply(embed=embed)


bot.run(TOKEN)
