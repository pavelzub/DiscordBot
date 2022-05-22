import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
from discord.commands import option
from modules import dota, firebase

load_dotenv()

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = discord.Bot()

token = os.getenv('TOKEN', None)
if token is None:
    print('Can\'t find bot token in .env')
    quit()

@bot.event
async def on_ready():
    guild_count = 0
    for guild in bot.guilds:
        print('Бот подключен на сервера:')
        print(f"- {guild.id} (name: {guild.name})")
        guild_count = guild_count + 1

@bot.slash_command(
    name="winrate",
    description="Показывает твой общий винрейт",
    scope=814468578349678653,
)
async def winrate(ctx: discord.ApplicationContext):
    dota_player_id = firebase.get_player_steam_id(ctx.author.id)
    await ctx.respond(':thinking: Думаю, подожди...')

    if (dota_player_id is None):
        await ctx.respond(f"Ты кто такой, чтоб это делать?")
        return

    wl_stats = dota.get_player_wl_stats(dota_player_id)
    winrate_in_percents = wl_stats.win / (wl_stats.win + wl_stats.lose) * 100

    await ctx.respond(
        f"Побед: {wl_stats.win}\n"
        f"Поражений: {wl_stats.lose}\n"
        f"Винрейт: {winrate_in_percents:.2f}%\n"
        f"{':muscle: cильный' if (winrate_in_percents >= 50) else ':chicken: cлабый'}, получается"
    )

# SLON OTVETSTVENYI
@bot.slash_command(
    name="compare",
    description="Помериться письками (винрейтом на герое) с другим дотером",
    scope=814468578349678653,
)
async def compare(ctx: discord.ApplicationContext, doter: discord.Member, hero: str):
    hero_entity = dota.get_dota_hero_by_name(hero)

    if (hero_entity is None):
        await ctx.respond(f'Ошибка: Хз, что за герой такой: {hero}.')
        return

    await ctx.respond(f':thinking: Ща, подумаю и узнаем, кто лучше играет на {hero}…')

    first_player_id = firebase.get_player_steam_id(ctx.author.id)
    second_player_id = firebase.get_player_steam_id(doter.id)

    if (first_player_id is None):
        # Вова попросил
        await ctx.respond(f"Ошибка: Ногу с клавиатуры убери, чёрт неизвестный")
        return

    if (second_player_id is None):
        await ctx.respond(f'Ошибка: Не могу найти дотера {doter.name}')
        return

    await ctx.respond(
        f"{dota.get_player_winrate_on_hero(int(first_player_id), hero_entity)}\n"
        f"{dota.get_player_winrate_on_hero(int(second_player_id), hero_entity)}"
    )

@bot.slash_command(
    name="register",
    description="Регистрирует тебя между ног у бота",
    scope=814468578349678653,
)
@option(
    name="steam_id",
    description="Твой Steam ID",
    required=True
)
async def register(ctx: discord.ApplicationContext, steam_id: int):
    await ctx.respond(':thinking: Думаю, подожди...')
    name = dota.get_player_name(steam_id)

    if (firebase.get_player_steam_id(ctx.author.id) is not None):
        await ctx.respond(f"Ошибка: Ты уже в системе, ало.")
        return

    if name != None:
        await ctx.respond(f"Привет, дотер {name}!")
        firebase.register_dota_player(int(ctx.author.id), steam_id)
    else:
        await ctx.respond(f"Ошибка: Кажется кто-то пиздун или закрыл аккаунт.")


@bot.slash_command(
    name="last",
    description="Показывает статистики твоей последней игры",
    scope=814468578349678653,
)
async def last(ctx: discord.ApplicationContext):
    await ctx.respond(':thinking: Думаю, подожди...')

    dota_player_id = firebase.get_player_steam_id(ctx.author.id)
    if (dota_player_id is None):
        await ctx.respond(f"Ты кто такой, чтоб это делать?")
        return

    last_match = dota.get_last_match(dota_player_id)
    hero = dota.get_dota_hero_by_id(last_match.hero_id)
    is_radiant = last_match.player_slot < 128
    is_win = (last_match.radiant_win and is_radiant) or (not last_match.radiant_win and not is_radiant)

    await ctx.respond(
        f"Твоя последняя игра на {hero.localized_name} закончилась {'победой :yum:' if is_win else 'проигрышем :sob:'}\n"
        f"Игра длилась {last_match.duration / 60:.0f} минут(ы)\n"
        f"Твои показатели KDA: {last_match.kills}:crossed_swords: {last_match.deaths}:skull: {last_match.assists}:handshake:"
    )

async def get_dota_heroes(ctx: discord.AutocompleteContext) -> str:
    return [hero_name for hero_name in dota.HERO_NAMES if hero_name.startswith(ctx.value.lower())]

@bot.slash_command(
    name="hero",
    description="Показывает винрейт на поределенном герое",
    scope=814468578349678653,
)
@option(
    name="name",
    description="Имя героя",
    autocomplete=discord.utils.basic_autocomplete(get_dota_heroes),
)
async def hero_winrate(ctx: discord.ApplicationContext, name: str):
    hero = dota.get_dota_hero_by_name(name)
    await ctx.respond(':thinking: Думаю, подожди...')
    if hero is not None:
        dota_player_id = firebase.get_player_steam_id(ctx.author.id)
        if dota_player_id is not None:
            await ctx.respond(dota.get_player_winrate_on_hero(dota_player_id, hero))
        else:
            await ctx.respond("Ало, а ты кто такой чтоб кнопки тут жать?")
    else:
        await ctx.respond(f"Ошибка: В доте, вроде, нет героя {name}.")

bot.run(token)
