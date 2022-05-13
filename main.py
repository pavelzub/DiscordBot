import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
import python_opendota
from pprint import pprint
from python_opendota.api import players_api
from python_opendota.api import heroes_api
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate("fireToken.json")
fireApp = firebase_admin.initialize_app(cred, {'databaseURL': 'https://botdis-7d015-default-rtdb.firebaseio.com'}) 
dotaPlayersRef = db.reference('/DotaPlayers')

def registerDotaPlayer(discordId, dotaId):
    dotaPlayersRef.update({discordId: dotaId})

load_dotenv()
bot = discord.Client(intents=discord.Intents.all())
dota_client = python_opendota.ApiClient(python_opendota.Configuration(host = "http://api.opendota.com/api"))
player_api = players_api.PlayersApi(dota_client)
heroes_api = heroes_api.HeroesApi(dota_client)

all_heroes = heroes_api.heroes_get()
stats = player_api.players_account_id_heroes_get(77315939)

def getHero(name):
    for hero in all_heroes:
        if hero.localized_name.lower() == name.lower():
            return hero
    return None

@bot.event
async def on_ready():
    guild_count = 0
    for guild in bot.guilds:
        print(f"- {guild.id} (name: {guild.name})")

        guild_count = guild_count + 1

    print("SampleDiscordBot is in " + str(guild_count) + " guilds.")

@bot.event
async def on_message(message):
    hero = getHero(message.content)
    if hero != None:
        for stat in stats:
            if int(stat.hero_id) == hero.id:
                await message.channel.send('Winrate on {} : {:.2f}%'.format(hero.localized_name, stat.win / stat.games * 100))

# pprint(response)

token = os.getenv('TOKEN', None)
if token != None:
    bot.run(token)
