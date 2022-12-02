import nextcord as discord

from modules import embed_replies
from nextcord.ext import commands
from modules.scraper import Scraper


class Getplayer(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


    @discord.slash_command("getplayer", "Fetch the server data for a specific server based on a players username.")
    async def getplayer(self, interaction: discord.Interaction, username: str = discord.SlashOption("username", "The players username.", True)):
        scraper = Scraper("")
        server = await scraper.fetch_player_server(username)

        if "error" in server:
            return await interaction.send(server["error"], ephemeral=True)

        socket_data = await scraper.fetch_server_socket(server["gameId"])

        serverstring: str
        if "error" in socket_data:
            serverstring = f"; {socket_data['error']} ;"
        else:
            serverstring = f"[ User Server | (?/{server['maxPlayers']}) | {socket_data['ip']}:{socket_data['port']} | ?ms ]"

        embed = embed_replies.SERVER(f"{server['user']['display']} ({server['user']['name']})", server["user"]["url"], server["user"]["playerHeadshot"], f"```ini\n{serverstring}\n```")
        await interaction.send(embeds=[embed])