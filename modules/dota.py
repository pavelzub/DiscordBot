import python_opendota
from python_opendota.api import players_api, heroes_api

dota_client = python_opendota.ApiClient(python_opendota.Configuration(host = "http://api.opendota.com/api"))
players_api = players_api.PlayersApi(dota_client)
heroes_api = heroes_api.HeroesApi(dota_client)

HERO_NAMES = [
    'Abaddon',
    'Alchemist',
    'Axe',
    'Beastmaster',
    'Brewmaster',
    'Bristleback',
    'Centaur Warrunner',
    'Chaos Knight',
    'Clockwerk',
    'Dawnbreaker',
    'Doom',
    'Dragon Knight',
    'Earth Spirit',
    'Earthshaker',
    'Elder Titan',
    'Huskar',
    'Io',
    'Kunkka',
    'Legion Commander',
    'Lifestealer',
    'Lycan',
    'Magnus',
    'Marci',
    'Mars',
    'Night Stalker',
    'Omniknight',
    'Phoenix',
    'Primal Beast',
    'Pudge',
    'Sand King',
    'Slardar',
    'Snapfire',
    'Spirit Breaker',
    'Sven',
    'Tidehunter',
    'Timbersaw',
    'Tiny',
    'Treant Protector',
    'Tusk',
    'Underlord',
    'Undying',
]

def get_player_name(steam_id: int) -> str | None:
    try:
        player_info = players_api.players_account_id_get(int(steam_id), _check_return_type=False)
        return player_info['profile']['personaname']
    except Exception as e:
        print("Exception when calling PlayersApi->players_account_id_get: %s\n" % e)
        return None

def get_player_stats(steam_id: int):
    try:
        player_stats = players_api.players_account_id_heroes_get(int(steam_id))
        return player_stats
    except Exception as e:
        print("Exception when calling PlayersApi->players_account_id_heroes_get: %s\n" % e)
        return None

def get_dota_hero_by_name(name: str):
    all_heroes = heroes_api.heroes_get()
    for hero in all_heroes:
        if name.lower() == hero.localized_name.lower():
            return hero
    return None

def get_dota_hero_by_id(id: int):
    all_heroes = heroes_api.heroes_get()
    for hero in all_heroes:
        if id == int(hero.id):
            return hero
    return None

def get_last_match(steam_id: int):
    try:
        last_matches = players_api.players_account_id_recent_matches_get(int(steam_id), _check_return_type=False)
        return last_matches[0]
    except Exception as e:
        print("Exception when calling PlayersApi->players_account_id_recent_matches_get: %s\n" % e)
        return None

def get_player_wl_stats(steam_id: int):
    try:
        wl_stats = players_api.players_account_id_wl_get(int(steam_id))
        return wl_stats
    except Exception as e:
        print("Exception when calling PlayersApi->players_account_id_wl_get: %s\n" % e)
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