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
        if name.lower() == hero.localized_name.lower():
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

def get_player_winrate_on_hero(dota_player_id, hero):
    stats = get_player_stats(dota_player_id)
    name = get_player_name(dota_player_id)
    name = name if (name is not None) else 'Somebody'

    if stats is not None:
        for stat in stats:
            if int(stat.hero_id) == hero.id:
                if (stat.games) != 0:
                    return f'{name}\'s winrate on {hero.localized_name}: {stat.win / stat.games * 100:.2f}%, games {stat.games}'
                else:
                    return f'{name} has no games on {hero.localized_name}'

def get_player_wl_stats(dota_player_id):
    try:
        wl_stats = player_api.players_account_id_wl_get(int(dota_player_id))
        return wl_stats
    except Exception as e:
        print("Exception when calling PlayersApi->players_account_id_wl_get: %s\n" % e)
        return None


def register_dota_player(discord_id, dota_id):
    players_db_ref.update({ discord_id: dota_id })

def get_last_match(dota_player_id):
    try:
        last_matches = player_api.players_account_id_recent_matches_get(int(dota_player_id), _check_return_type=False)
        return last_matches[0]
    except Exception as e:
        print("Exception when calling PlayersApi->players_account_id_recent_matches_get: %s\n" % e)
        return None

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

    if (result is None):
        return

    if (hero is None):
        await ctx.reply(f'Хз, что за герой такой: {hero_name}')
        return

    first_player_id = get_dota_id(ctx.message.author.id)
    second_player_id = get_dota_id(result.group(1))

    if (first_player_id is None):
        await ctx.reply(f'Так мы не знакомы c тобой, напиши !register', mention_author=True)

    if (second_player_id is None):
        await ctx.reply(f'Не могу найти дотера {user_ref}')
        return

    await ctx.reply(f'{get_player_winrate_on_hero(first_player_id, hero)}\n{get_player_winrate_on_hero(second_player_id, hero)}')

@bot.command()
async def register(ctx, dota_player_id):
    name = get_player_name(dota_player_id)
    if (get_dota_id(ctx.message.author.id) is not None):
        await ctx.reply(f"За такое надо платить")
        return
    if name != None:
        await ctx.reply(f"Привет, дотер {name}")
        register_dota_player(ctx.message.author.id, dota_player_id)
    else:
        await ctx.reply(f"Кажется кто-то пиздун или закрыл аккаунт")

@bot.command()
async def winrate(ctx):
    dota_player_id = get_dota_id(ctx.message.author.id)

    if (dota_player_id is None):
        await ctx.reply(f"Ты кто такой, чтоб это делать?")
        return

    wl_stats = get_player_wl_stats(dota_player_id)
    winrate_in_percents = wl_stats.win / (wl_stats.win + wl_stats.lose) * 100

    await ctx.reply(
        f"Побед: {wl_stats.win}\n"
        f"Поражений: {wl_stats.lose}\n"
        f"Винрейт: {winrate_in_percents:.2f}%\n"
        f"{':muscle: cильный' if (winrate_in_percents >= 50) else ':chicken: cлабый'}, получается"
    )

@bot.command()
async def last(ctx):
    dota_player_id = get_dota_id(ctx.message.author.id)

    if (dota_player_id is None):
        await ctx.reply(f"Ты кто такой, чтоб это делать?")
        return
    last_match = get_last_match(dota_player_id)
    is_radiant = last_match.player_slot < 128
    is_win = (last_match.radiant_win and is_radiant) or (not last_match.radiant_win and not is_radiant)
    for hero in all_heroes:
        if int(last_match.hero_id) == int(hero.id):
            hero_name = hero.localized_name
    await ctx.reply(f"Твоя последняя игра на {hero_name} закончилась {'Победой' if is_win else 'Проигрышем'} \nИгра длилась {int(last_match.duration / 60)} минут \nТвои показатели KDA: {last_match.kills}:muscle:{last_match.deaths}:skull:{last_match.assists}:handshake:")


@bot.listen('on_message')
async def listen_message(message):
    hero = get_hero(message.content)
    if hero != None:
        dota_player_id = get_dota_id(message.author.id)
        if dota_player_id is not None:
            await message.channel.send(get_player_winrate_on_hero(dota_player_id, hero))




token = os.getenv('TOKEN', None)
if token != None:
    bot.run(token)
else:
    print('Cant find Token in .env')
