import python_opendota
from python_opendota.api import players_api, heroes_api

dota_client = python_opendota.ApiClient(python_opendota.Configuration(host = "http://api.opendota.com/api"))
players_api = players_api.PlayersApi(dota_client)
heroes_api = heroes_api.HeroesApi(dota_client)

HERO_NAMES = [
    "Ancient Apparition",
    "Abaddon",
    "Alchemist",
    "Anti-Mage",
    "Arc Warden",
    "Axe",
    "Bane",
    "Batrider",
    "Beastmaster",
    "Bloodseeker",
    "Bounty Hunter",
    "Brewmaster",
    "Bristleback",
    "Broodmother",
    "Centaur Warrunner",
    "Chaos Knight",
    "Chen",
    "Clinkz",
    "Clockwerk",
    "Crystal Maiden",
    "Dark Seer",
    "Dark Willow",
    "Dawnbreaker",
    "Dazzle",
    "Death Prophet",
    "Disruptor",
    "Doom",
    "Dragon Knight",
    "Drow Ranger",
    "Earth Spirit",
    "Earthshaker",
    "Elder Titan",
    "Ember Spirit",
    "Enchantress",
    "Enigma",
    "Faceless Void",
    "Grimstroke",
    "Gyrocopter",
    "Hoodwink",
    "Huskar",
    "Invoker",
    "Io",
    "Jakiro",
    "Juggernaut",
    "Keeper of the Light",
    "Kunkka",
    "Legion Commander",
    "Leshrac",
    "Lich",
    "Lifestealer",
    "Lina",
    "Lion",
    "Lone Druid",
    "Luna",
    "Lycan",
    "Magnus",
    "Marci",
    "Mars",
    "Medusa",
    "Meepo",
    "Mirana",
    "Monkey King",
    "Morphling",
    "Naga Siren",
    "Nature's Prophet",
    "Necrophos",
    "Night Stalker",
    "Nyx Assassin",
    "Ogre Magi",
    "Omniknight",
    "Oracle",
    "Outworld Devourer",
    "Pangolier",
    "Phantom Assassin",
    "Phantom Lancer",
    "Phoenix",
    "Primal Beast",
    "Puck",
    "Pudge",
    "Pugna",
    "Queen of Pain",
    "Razor",
    "Riki",
    "Rubick",
    "Sand King",
    "Shadow Demon",
    "Shadow Fiend",
    "Shadow Shaman",
    "Silencer",
    "Skywrath Mage",
    "Slardar",
    "Slark",
    "Snapfire",
    "Sniper",
    "Spectre",
    "Spirit Breaker",
    "Storm Spirit",
    "Sven",
    "Techies",
    "Templar Assassin",
    "Terrorblade",
    "Tidehunter",
    "Timbersaw",
    "Tinker",
    "Tiny",
    "Treant Protector",
    "Troll Warlord",
    "Tusk",
    "Underlord",
    "Undying",
    "Ursa",
    "Vengeful Spirit",
    "Venomancer",
    "Viper",
    "Visage",
    "Void Spirit",
    "Warlock",
    "Weaver",
    "Windranger",
    "Winter Wyvern",
    "Witch Doctor",
    "Wraith King",
    "Zeus"
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