import discord
from discord.ext import commands
import os

intents = discord.Intents.default()
intents.guilds = True
intents.members = True

bot = discord.Bot(intents=intents)

# ========= Settings =========
GUILD_ID = 1265009261679739034
LOG_CHANNEL_ID = 1436831464619507713
TICKET_CATEGORY_ID = 1439275840432247017

STAFF_ROLE_IDS = [
1265012541214429216,
1265013755427946516,
1440322627561590875,
]
# ==========================


class ApplyModal(discord.ui.Modal, title="Clan Application"):

    ign = discord.ui.TextInput(
        label="What is your in-game name (IGN)?",
        required=True
    )

    rank = discord.ui.TextInput(
        label="What is your current rank?",
        required=True
    )

    axe_count = discord.ui.TextInput(
        label="How many axes do you have?",
        required=True
    )

    hours = discord.ui.TextInput(
        label="How many hours can you play on daily basis?",
        required=True
    )

    reason = discord.ui.TextInput(
        label="Why do you want to join our clan?",
        style=discord.TextStyle.paragraph,
        required=True
    )

    async def on_submit(self, interaction: discord.Interaction):
        guild = interaction.guild

        category = discord.utils.get(guild.categories, id=TICKET_CATEGORY_ID)

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }

        for role_id in STAFF_ROLE_IDS:
            role = guild.get_role(role_id)
            if role:
                overwrites[role] = discord.PermissionOverwrite(read_messages=True)

        channel = await guild.create_text_channel(
            name=f"apply-{interaction.user.name}",
            category=category,
            overwrites=overwrites
        )

        embed = discord.Embed(
            title="📥 New Clan Application",
            color=discord.Color.green()
        )
        embed.add_field(name="IGN", value=self.ign.value, inline=False)
        embed.add_field(name="Rank", value=self.rank.value, inline=False)
        embed.add_field(name="Axe Count", value=self.axe_count.value, inline=False)
        embed.add_field(name="Daily Playtime", value=self.hours.value, inline=False)
        embed.add_field(name="Reason", value=self.reason.value, inline=False)

        view = CloseTicketView()

        await channel.send(
            content=" ".join(f"<@&{r}>" for r in STAFF_ROLE_IDS),
            embed=embed,
            view=view
        )

        await channel.send(
            f"""
👋 Welcome {interaction.user.mention}!

Thanks for applying to our clan.
Our staff will review your application shortly.

📌 Please do not spam or ping staff.
🔒 Use the **Close Ticket** button when finished.
"""
        )

        log_channel = guild.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            await log_channel.send(embed=embed)

        await interaction.response.send_message(
            f"✅ Your application has been submitted!\nTicket: {channel.mention}",
            ephemeral=True
        )


class CloseTicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Close Ticket", style=discord.ButtonStyle.danger)
    async def close(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.channel.delete()


@bot.slash_command(
    name="apply",
    description="Open clan application panel",
    guild_ids=[GUILD_ID]
)
@commands.has_permissions(administrator=True)
async def apply(interaction: discord.Interaction):
    await interaction.response.send_modal(ApplyModal())


@bot.event
async def on_ready():
    print(f"Bot online: {bot.user}")


bot.run(os.getenv("DISCORD_TOKEN"))
