import os
from dotenv import load_dotenv
from pyparsing import empty
import discord
from discord.ext import commands
import python_opendota
from python_opendota.api import players_api
from python_opendota.api import heroes_api
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import re

load_dotenv()

firebase_cred = credentials.Certificate("fireToken.json")
firebase_app = firebase_admin.initialize_app(firebase_cred, {'databaseURL': 'https://botdis-7d015-default-rtdb.firebaseio.com'}) 
players_db_ref = db.reference('/DotaPlayers')

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

dota_client = python_opendota.ApiClient(python_opendota.Configuration(host = "http://api.opendota.com/api"))
player_api = players_api.PlayersApi(dota_client)
heroes_api = heroes_api.HeroesApi(dota_client)

all_heroes = heroes_api.heroes_get()

def get_dota_id(discord_id):
    return players_db_ref.get().get(str(discord_id), None)

def get_hero(name):
    for hero in all_heroes:
        if name.lower() in hero.localized_name.lower():
            return hero
    return None

def get_player_name(dota_player_id):
    try:
        player_info = player_api.players_account_id_get(int(dota_player_id), _check_return_type=False)
        return player_info['profile']['personaname']
    except Exception as e:
        print("Exception when calling BenchmarksApi->benchmarks_get: %s\n" % e)
        return None

def get_player_stats(dota_player_id):
    try:
        player_stats = player_api.players_account_id_heroes_get(int(dota_player_id))
        return player_stats
    except Exception as e:
        print("Exception when calling BenchmarksApi->benchmarks_get: %s\n" % e)
        return None

def register_dota_player(discord_id, dota_id):
    players_db_ref.update({ discord_id: dota_id })

@bot.event
async def on_ready():
    guild_count = 0
    for guild in bot.guilds:
        print(f"- {guild.id} (name: {guild.name})")

        guild_count = guild_count + 1

#SLON OTVETSTVENYI
@bot.command()
async def compare(ctx, user_ref, hero_name: str):
    result = re.match(r'<@(\d+)>', user_ref)
    hero = get_hero(hero_name)
    if result is None or hero is None:
        return

    dota_player_first = get_dota_id(ctx.message.author.id)
    dota_player_second = get_dota_id(result.group(1))

    if dota_player_first is None or dota_player_second is None:
        return

    stats_f = get_player_stats(dota_player_first)
    name_f = get_player_name(dota_player_first)

    stats_s = get_player_stats(dota_player_second)
    name_s = get_player_name(dota_player_second)

    if stats_f is None or name_f is None or stats_s is None or name_s is None:
        return

    result = ''
    for stat in stats_f:
        if int(stat.hero_id) == hero.id:
            result += f'{name_f} winrate on {hero.localized_name}: {stat.win / stat.games * 100:.2f}%, games {stat.games}'

    if result == '':
        result = f'{name_f} not played on {hero.localized_name}'
    result += "\n"

    for stat in stats_s:
        if int(stat.hero_id) == hero.id:
            result += f'{name_s} winrate on {hero.localized_name}: {stat.win / stat.games * 100:.2f}%, games {stat.games}'

    
    await ctx.reply(result)

@bot.command()
async def register(ctx, dota_player_id):
    name = get_player_name(dota_player_id)
    if get_dota_id(ctx.message.author.id) is not None:
        await ctx.reply(f"За такое надо платить")
        return
    if name != None:
        await ctx.reply(f"Привет дотер {name}")
        register_dota_player(ctx.message.author.id, dota_player_id)
    else:
        await ctx.reply(f"Кажется кто-то пиздун или закрыл аккаунт")

@bot.listen('on_message')
async def listen_message(message):
    hero = get_hero(message.content)
    if hero != None:
        dota_player_id = get_dota_id(message.author.id)
        if dota_player_id is not None:
            stats = get_player_stats(dota_player_id)
            name = get_player_name(dota_player_id)
            name = name if (name is not None) else 'Чей-то'
            if stats is not None:
                for stat in stats:
                    if int(stat.hero_id) == hero.id:
                        await message.channel.send(f'{name} winrate on {hero.localized_name}: {stat.win / stat.games * 100:.2f}%, games {stat.games}')


token = os.getenv('TOKEN', None)
if token != None:
    bot.run(token)
