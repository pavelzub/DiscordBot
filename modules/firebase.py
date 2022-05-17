import firebase_admin
from firebase_admin import credentials, db

firebase_cred = credentials.Certificate('fireToken.json')
firebase_app = firebase_admin.initialize_app(firebase_cred, {'databaseURL': 'https://botdis-7d015-default-rtdb.firebaseio.com'}) 
players_db_ref = db.reference('/DotaPlayers')

def get_player_steam_id(discord_id: int) -> int | None:
    return players_db_ref.get().get(str(discord_id), None)

def register_dota_player(discord_id: int, steam_id: int):
    players_db_ref.update({ discord_id: steam_id })