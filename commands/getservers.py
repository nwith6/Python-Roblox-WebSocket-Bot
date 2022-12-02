import nextcord as discord

from modules import embed_replies
from nextcord.ext import commands
from modules.scraper import Scraper


class Getservers(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


    @discord.slash_command("getservers", "Get server data for the given game.")
    async def getservers(self, interaction: discord.Interaction, url: str = discord.SlashOption("url", "The url for the game.", True)):
        if not "/" in url or not url.split("/")[4] or not "https://www.roblox.com/games/" in url or not url.split("/")[4].isdigit():
            return await interaction.send("The provided url is invalid. Ensure it is formatted as 'https://www.roblox.com/games/placeId/placeName'", ephemeral=True)

        scraper = Scraper(url.split("/")[4])
        servers = await scraper.fetch_servers()

        if "error" in servers:
            return await interaction.send(servers["error"], ephemeral=True)

        embed = embed_replies.SERVER(servers["name"], servers["url"], servers["gameIconUrl"], "```ini\n[ Fetching server data ]\n```")
        message = await interaction.send(embeds=[embed])

        description = str()
        for i,server in enumerate(servers["data"]):
            socket_data = await scraper.fetch_server_socket(server["gameId"])
            server_number = str((i + 1)).zfill(2)
            ping = f"{server['ping']}ms"
            serverstring = str()

            if "error" in socket_data:
                serverstring = f"; Server {server_number} | ({str(server['playing']).zfill(2)}/{str(servers['maxPlayers']).zfill(2)}) | {(socket_data['error']).ljust(20, ' ')} | {ping.ljust(5, ' ')} ;\n"
            else:
                socket = f"{socket_data['ip']}:{socket_data['port']}"

                serverstring = f"[ Server {server_number} | ({str(server['playing']).zfill(2)}/{str(servers['maxPlayers']).zfill(2)}) | {socket.ljust(20, ' ')} | {ping.ljust(5, ' ')} ]\n"

            description += serverstring
            embed.description = f"```ini\n{description}\n```"

            await message.edit(embeds=[embed])