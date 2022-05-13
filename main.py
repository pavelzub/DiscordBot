import os
from dotenv import load_dotenv
import discord
import python_opendota
from pprint import pprint
from python_opendota.api import players_api
from python_opendota.api import heroes_api

load_dotenv()
bot = discord.Client()
dota_client = python_opendota.ApiClient(python_opendota.Configuration(host = "http://api.opendota.com/api"))
player_api = players_api.PlayersApi(dota_client)
heroes_api = heroes_api.HeroesApi(dota_client)

all_heroes = heroes_api.heroes_get()
stats = player_api.players_account_id_heroes_get(77315939)

def heroId(name):
    for hero in all_heroes:
        if hero.localized_name.lower() == name.lower():
            return hero.id
    return -1

@bot.event
async def on_ready():
    guild_count = 0
    for guild in bot.guilds:
        print(f"- {guild.id} (name: {guild.name})")

        guild_count = guild_count + 1

    print("SampleDiscordBot is in " + str(guild_count) + " guilds.")

@bot.event
async def on_message(message):
    id = heroId(message.content)
    if id > 0:
        for stat in stats:
            if stat.hero_id == id:
                await message.channel.send('Winrate on {} : {}%'.format(message.content, stat.win / stat.games * 100))

# pprint(response)

token = os.getenv('TOKEN', None)
if token != None:
    bot.run(token)
