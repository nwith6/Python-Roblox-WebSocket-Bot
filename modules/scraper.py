import os
import json
import aiohttp as request

with open(f"{os.getcwd()}/config.json") as r:
    __cookie = json.load(r)["roblox"]["cookie"]

    cookies = {".ROBLOSECURITY": __cookie}
    cookie_header = f".ROBLOSECURITY={__cookie}; path=/; domain=.roblox.com"


class Scraper:

    def __init__(self, placeid: str):
        self.placeid = placeid

        self.__headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36",
            "Content-Type": "application/json",
            "Referer": "https://www.roblox.com/games/",
            "Origin": "https://www.roblox.com/",
            "Accept": "application/json",
            "Cookie": cookie_header
        }
        self.__gamejoin_headers = {
            "User-Agent": "Roblox/WinInet",
            "Referer": "https://www.roblox.com/games/",
            "Origin": "https://www.roblox.com/",
            "Cookie": cookie_header
        }

    def __update_instance_placeid(self, placeid):
        self.placeid = placeid

        self.__headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36",
            "Content-Type": "application/json",
            "Referer": "https://www.roblox.com/games/",
            "Origin": "https://www.roblox.com/",
            "Accept": "application/json",
            "Cookie": cookie_header
        }
        self.__gamejoin_headers = {
            "User-Agent": "Roblox/WinInet",
            "Referer": "https://www.roblox.com/games/",
            "Origin": "https://www.roblox.com/",
            "Cookie": cookie_header
        }

    
    async def __get(self, url: str) -> dict:
        async with request.ClientSession(cookies=cookies) as session:
            async with session.get(url, headers=self.__headers) as response:
                return await response.json()


    async def __post(self, url: str, payload: dict = dict()) -> dict:
        async with request.ClientSession(cookies=cookies) as session:
            async with session.post(url, headers=self.__headers, data=payload) as response:
                return await response.json()


    async def __post_gamejoin(self, url: str, payload: dict) -> dict:
        async with request.ClientSession(cookies=cookies) as session:
            async with session.post(url, headers=self.__gamejoin_headers, data=payload) as response:
                return await response.json()

    
    async def __servers(self):
        return await self.__get(f"https://games.roblox.com/v1/games/{self.placeid}/servers/Public?sortOrder=Desc&excludeFullGames=true&limit=25")


    async def __place_details(self) -> dict:
        return await self.__get(f"https://games.roblox.com/v1/games/multiget-place-details?placeids={self.placeid}")


    async def __game_instance(self, gameid: str) -> dict:
        return await self.__post_gamejoin("https://gamejoin.roblox.com/v1/join-game-instance", {
            "placeId": self.placeid,
            "isTeleport": False,
            "gameId": gameid,
            "gameJoinAttemptId": gameid
        })


    async def __userdata(self, username: str) -> dict:
        return await self.__post("https://users.roblox.com/v1/usernames/users", {
            "usernames": [ username ]
        })


    async def __userpresence(self, userid: str) -> dict:
        return await self.__post("https://presence.roblox.com/v1/presence/users", {
            "userIds": [ userid ]
        })


    async def __universe(self, universeid: str) -> dict:
        return await self.__get(f"https://games.roblox.com/v1/games?universeIds={universeid}")


    async def __roblox_imageurl(self, type: str, arg: str):
        if type == "headshot":
            return await self.__get(f"https://thumbnails.roblox.com/v1/users/avatar-headshot?userIds={arg}&size=48x48&format=Png&isCircular=true")
        else: # elif type == "icon":
            return await self.__get(f"https://thumbnails.roblox.com/v1/places/gameicons?placeIds={arg}&returnPolicy=0&size=50x50&format=Png&isCircular=true")


    async def __serversdata(self, servers: dict) -> dict:
        place_details = await self.__place_details()
        game_icon = await self.__roblox_imageurl("icon", place_details[0]["placeId"])

        pack = {
            "data": [],
            "maxPlayers": servers["data"][0]["maxPlayers"],
            "name": place_details[0]["name"],
            "url": place_details[0]["url"],
            "gameIconUrl": game_icon["data"][0]["imageUrl"]
        }

        for _,server in enumerate(servers["data"]):
            pack["data"].append({
                "gameId": server["id"],
                "playing": server["playing"],
                "ping": server["ping"]
            })

        return pack


    async def fetch_servers(self) -> dict:
        servers = await self.__servers()
        if not "data" in servers or not len(servers["data"]) > 0:
            return {
                "error": "Failed to fetch any servers from the given place."
            }

        return await self.__serversdata(servers)


    async def fetch_player_server(self, username: str) -> dict:
        userdata = await self.__userdata(username)
        if not len(userdata["data"]) > 0:
            return {
                "error": "Failed to fetch any userdata from the given user."
            }

        userpresence = await self.__userpresence(userdata["data"][0]["id"])
        if userpresence["userPresences"][0]["gameId"] == None or userpresence["userPresences"][0]["placeId"] == None:
            return {
                "error": "Failed to fetch the given user's server. This could be becuase the user is currently offline, has their joins off, or an unexpected error has occurred."
            }

        universe = await self.__universe(userpresence["userPresences"][0]["universeId"])
        player_headshot = await self.__roblox_imageurl("headshot", userdata["data"][0]["id"])
        self.__update_instance_placeid(userpresence["userPresences"][0]["placeId"])

        return {
            "user": {
                "name": userdata["data"][0]["name"],
                "display": userdata["data"][0]["displayName"],
                "url": f"https://www.roblox.com/users/{userdata['data'][0]['id']}/profile",
                "playerHeadshot": player_headshot["data"][0]["imageUrl"]
            },
            "gameId": userpresence,
            "maxPlayers": universe
        }


    async def fetch_server_socket(self, gameid: str) -> dict:
        game_instance = await self.__game_instance(gameid)

        if not game_instance["jobId"] or not game_instance["joinScript"] or game_instance["joinScript"]["MachineAddress"].startswith("10."):
            return {
                "error": "Protected websocket"
            }
        return {
            "ip": game_instance["joinScript"]["MachineAddress"],
            "port": game_instance["joinScript"]["ServerPort"]
        }