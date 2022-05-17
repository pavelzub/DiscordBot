import os
from dotenv import load_dotenv
import interactions
import python_opendota
from python_opendota.api import players_api
from python_opendota.api import heroes_api
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

load_dotenv()

firebase_cred = credentials.Certificate("fireToken.json")
firebase_app = firebase_admin.initialize_app(firebase_cred, {'databaseURL': 'https://botdis-7d015-default-rtdb.firebaseio.com'}) 
players_db_ref = db.reference('/DotaPlayers')

token = os.getenv('TOKEN', None)
if token != None:
    bot = interactions.Client(token)
else:
    print('Cant find Token in .env')

dota_client = python_opendota.ApiClient(python_opendota.Configuration(host = "http://api.opendota.com/api"))
player_api = players_api.PlayersApi(dota_client)
heroes_api = heroes_api.HeroesApi(dota_client)

def pluralize(count: int, words: list[str]) -> str:
    cases = [2, 0, 1, 1, 1, 2]
    return f"{count} {words[2 if count % 100 > 4 and count % 100 < 20 else cases[min(count % 100, 5)]]}"

def get_dota_id(discord_id):
    return players_db_ref.get().get(str(discord_id), None)

def get_hero(name):
    all_heroes = heroes_api.heroes_get()
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
    name = name if (name is not None) else '[Имя неизвестно]'

    if stats is not None:
        for stat in stats:
            if int(stat.hero_id) == hero.id:
                if (stat.games) != 0:
                    return f"Винрейт игрока {name} на {hero.localized_name}: {stat.win / stat.games * 100:.2f}%, игр {stat.games}"
                else:
                    return f"{name} ни разу не играл на {hero.localized_name}"

def get_player_wl_stats(dota_player_id):
    try:
        wl_stats = player_api.players_account_id_wl_get(int(dota_player_id))
        return wl_stats
    except Exception as e:
        print("Exception when calling PlayersApi->players_account_id_wl_get: %s\n" % e)
        return None


def register_dota_player(discord_id: int, steam_id: int):
    players_db_ref.update({ discord_id: steam_id })

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

@bot.command(
    name="winrate",
    description="Показывает твой общий винрейт",
    scope=814468578349678653,
)
async def winrate(ctx: interactions.CommandContext):
    dota_player_id = get_dota_id(ctx.author.id)

    if (dota_player_id is None):
        await ctx.send(f"Ты кто такой, чтоб это делать?")
        return

    wl_stats = get_player_wl_stats(dota_player_id)
    winrate_in_percents = wl_stats.win / (wl_stats.win + wl_stats.lose) * 100

    await ctx.send(
        f"Побед: {wl_stats.win}\n"
        f"Поражений: {wl_stats.lose}\n"
        f"Винрейт: {winrate_in_percents:.2f}%\n"
        f"{':muscle: cильный' if (winrate_in_percents >= 50) else ':chicken: cлабый'}, получается"
    )

# SLON OTVETSTVENYI
@bot.command(
    name="compare",
    description="Помериться письками (винрейтом на герое) с другим дотером",
    scope=814468578349678653,
    options=[
        interactions.Option(
            type=interactions.OptionType.MENTIONABLE,
            name="doter",
            description="Имя дотера в Discord",
            required=True
        ),
        interactions.Option(
            type=interactions.OptionType.STRING,
            name="hero",
            description="Имя героя",
            required=True
        ),
    ]
)
async def compare(ctx: interactions.CommandContext, doter: interactions.api.models.member.Member, hero: str):
    hero_entity = get_hero(hero)

    if (hero_entity is None):
        await ctx.send(f'Ошибка: Хз, что за герой такой: {hero}.')
        return

    await ctx.send(f'Ща, подумаю и узнаем, кто лучше играет на {hero}…')

    first_player_id = get_dota_id(ctx.author.id)
    second_player_id = get_dota_id(doter.id)

    if (first_player_id is None):
        # Вова попросил
        await ctx.send(f"Ошибка: Ногу с клавиатуры убери, чёрт неизвестный")
        return

    if (second_player_id is None):
        await ctx.send(f'Ошибка: Не могу найти дотера {doter.name}')
        return

    await ctx.send(f"{get_player_winrate_on_hero(int(first_player_id), hero_entity)}\n{get_player_winrate_on_hero(int(second_player_id), hero_entity)}")


@bot.command(
    name="register",
    description="Регистрирует тебя между ног у бота",
    scope=814468578349678653,
    options=[interactions.Option(
        type=interactions.OptionType.NUMBER,
        name="steam_id",
        description="Твой Steam ID",
        required=True,
    )]
)
async def register(ctx: interactions.CommandContext, steam_id: int):
    name = get_player_name(steam_id)
    if (get_dota_id(ctx.author.id) is not None):
        await ctx.send(f"Ошибка: Ты уже в системе, ало.")
        return
    if name != None:
        await ctx.send(f"Привет, дотер {name}!")
        register_dota_player(int(ctx.author.id), steam_id)
    else:
        await ctx.send(f"Ошибка: Кажется кто-то пиздун или закрыл аккаунт.")


@bot.command(
    name="last",
    description="Показывает статистики твоей последней игры",
    scope=814468578349678653,
)
async def last(ctx: interactions.CommandContext):
    all_heroes = heroes_api.heroes_get()

    dota_player_id = get_dota_id(ctx.author.id)
    if (dota_player_id is None):
        await ctx.send(f"Ты кто такой, чтоб это делать?")
        return

    last_match = get_last_match(dota_player_id)
    is_radiant = last_match.player_slot < 128
    is_win = (last_match.radiant_win and is_radiant) or (not last_match.radiant_win and not is_radiant)

    for hero in all_heroes:
        if int(last_match.hero_id) == int(hero.id):
            hero_name = hero.localized_name
    await ctx.send(f"Твоя последняя игра на {hero_name} закончилась {'победой :yum:' if is_win else 'проигрышем :sob:'} \nИгра длилась {pluralize(int(last_match.duration / 60), ['минуту', 'минуты', 'минут'])}\nТвои показатели KDA: {last_match.kills}:crossed_swords: {last_match.deaths}:skull: {last_match.assists}:handshake:")

@bot.command(
    name="hero",
    description="Показывает винрейт на поределенном герое",
    scope=814468578349678653,
    options=[interactions.Option(
        type=interactions.OptionType.STRING,
        name="name",
        description="Имя героя",
        required=True,
    )]
)
async def hero_winrate(ctx: interactions.CommandContext, name: str):
    hero = get_hero(name)
    if hero is not None:
        dota_player_id = get_dota_id(ctx.author.id)
        if dota_player_id is not None:
            await ctx.send(get_player_winrate_on_hero(dota_player_id, hero))
        else:
            await ctx.send("Ало, а ты кто такой?")
    else:
        await ctx.send(f"Ошибка: В доте, вроде, нет героя {name}.")

bot.start()
