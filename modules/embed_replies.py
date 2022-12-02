import nextcord as discord


def SERVER(author_text: str, author_url: str, author_icon_url: str, description: str):
    embed = discord.Embed()
    embed.set_author(name=author_text, icon_url=author_icon_url, url=author_url)
    embed.description = description
    embed.color = 0x006fd5

    return embed