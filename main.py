import os
import json

from events import on_ready
from nextcord.ext import commands
from commands import getplayer, getservers

# Bot Init
bot = commands.Bot()

# Command Registration
bot.add_cog(getplayer.Getplayer(bot))
bot.add_cog(getservers.Getservers(bot))

# Event Registration
bot.add_cog(on_ready.On_ready(bot))

if __name__ == "__main__":
    with open(f"{os.getcwd()}/config.json", "r") as r:
        bot.run(json.load(r)["discord"]["token"])
