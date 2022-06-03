import psycopg2
import json
from os import getenv, environ


def _(env: str) -> str | None:
    return getenv(f"{env.upper()}")


conn = psycopg2.connect(database=_("db"), user=_("db_user"), password=_("pass"), host=_("host"), port=_("port"))


def avatar(avatar_hash: str | None, user_id: int, discrim: int) -> str:
    if avatar_hash is None:
        return f"https://cdn.discordapp.com/embed/avatars/{discrim % 5}.png"
    return f"https://cdn.discordapp.com/avatars/{user_id}/{avatar_hash}.png"


try:
    with conn, conn.cursor() as cur:
        cur.execute("SELECT * FROM xp_users ORDER BY xp DESC")
        LEADERBOARD_JSON = json.dumps(
            [
                {
                    "id": user[0],
                    "name": user[1],
                    "discrim": user[2],
                    "xp": user[3],
                    "detailed_xp": user[4],
                    "level": user[5],
                    "messages": user[6],
                    "avatar": avatar(user[7], user[0], int(user[2])),
                }
                for user in cur.fetchall()
            ],
        )
except Exception as e:
    with open("_data/users.json", "r") as f:
        LEADERBOARD_JSON = json.dumps(json.load(f))
finally:
    with open(getenv('GITHUB_ENV'), "a") as myfile:
        myfile.write(f"LEADERBOARD_JSON={LEADERBOARD_JSON}")