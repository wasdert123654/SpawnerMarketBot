import discord
from discord.ext import commands
from discord import app_commands
import os
import re

TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

igns = {}

# 🔹 Parse "5m", "2.5b", "3k"
def parse_number(value: str):
    value = value.lower().replace(",", "").strip()
    if value.endswith("k"):
        return float(value[:-1]) * 1_000
    if value.endswith("m"):
        return float(value[:-1]) * 1_000_000
    if value.endswith("b"):
        return float(value[:-1]) * 1_000_000_000
    return float(value)

# 🔹 Convert expression "5m+2k-3m"
def calculate_expression(expr: str):
    def repl(match):
        return str(parse_number(match.group(0)))
    expr = re.sub(r"\d+(\.\d+)?[kmbKMB]", repl, expr)
    return eval(expr)

# 🔹 Parse percent like "2% of 5m"
def calculate_percent(percent_str: str):
    match = re.match(r"(\d+(?:\.\d+)?)%\s*(?:of)?\s*(.+)", percent_str.replace(" ", ""), re.IGNORECASE)
    if not match:
        return None, None
    pct = float(match.group(1))
    base = calculate_expression(match.group(2))
    result = (pct / 100) * base
    return pct, result

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    try:
        synced = await tree.sync()
        print(f"Synced {len(synced)} slash commands.")
    except Exception as e:
        print("Slash command sync error:", e)

# --------------------------
# 🔥 SLASH COMMANDS
# --------------------------

@tree.command(name="help", description="Shows all commands")
async def help_cmd(interaction: discord.Interaction):
    embed = discord.Embed(title="Commands List", color=discord.Color.blue())
    embed.add_field(name="/calc <expression>", value="Calculate values like `5m+2k`", inline=False)
    embed.add_field(name="/percent <expression>", value="Calculate percentages like `2% of 500m`", inline=False)
    embed.add_field(name="/ign <username>", value="Set your IGN", inline=False)
    embed.add_field(name="/acalc <expression>", value="Calculate and format `/pay <IGN> <amount>`", inline=False)
    await interaction.response.send_message(embed=embed)

@tree.command(name="ign", description="Set your in-game name")
async def ign_cmd(interaction: discord.Interaction, name: str):
    igns[interaction.user.id] = name
    await interaction.response.send_message(f"IGN set to **{name}**")

@tree.command(name="calc", description="Calculate expressions like 5m+2k")
async def calc_cmd(interaction: discord.Interaction, expression: str):
    try:
        total = calculate_expression(expression)
        await interaction.response.send_message(f"**Result:** {total:,.0f}")
    except:
        await interaction.response.send_message("Invalid expression!", ephemeral=True)

@tree.command(name="acalc", description="Calculate /pay IGN amount")
async def acalc_cmd(interaction: discord.Interaction, expression: str):
    ign = igns.get(interaction.user.id)
    if not ign:
        await interaction.response.send_message("You must set your IGN first using `/ign <name>`.", ephemeral=True)
        return
    try:
        total = calculate_expression(expression)
    except:
        await interaction.response.send_message("Invalid expression!", ephemeral=True)
        return
    await interaction.response.send_message(f"/pay **{ign}** **{total:,.0f}**")

@tree.command(name="percent", description="Calculate percentages like 2% of 500m")
async def percent_cmd(interaction: discord.Interaction, query: str):
    pct, result = calculate_percent(query)
    if pct is None:
        await interaction.response.send_message("Invalid percent format! Example: `2% of 500m`", ephemeral=True)
        return
    await interaction.response.send_message(f"**{pct}%** of the amount is **{result:,.0f}**")

bot.run(TOKEN)
