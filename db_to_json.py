import psycopg2
import json
from os import getenv, environ


def _(env: str) -> str | None:
    return getenv(f"{env.upper()}")


conn = psycopg2.connect(database=_("db"), user=_("db_user"), password=_("pass"), host=_("host"), port=_("port"))


def avatar(avatar_hash: str | None, user_id: int, discriminator: int) -> str:
    if avatar_hash is None:
        return f"https://cdn.discordapp.com/embed/avatars/{discriminator % 5}.png"
    return f"https://cdn.discordapp.com/avatars/{user_id}/{avatar_hash}.png"


with conn, conn.cursor() as cur:
    cur.execute("SELECT *, ROW_NUMBER() OVER(ORDER BY xp DESC) FROM xp_users ORDER BY xp DESC")
    with open("_data/users.json", "w") as f:
        json.dump(
            [
                {
                    "id": user[0],
                    "name": str(user[1]).encode("ascii", "ignore").decode(),
                    "discriminator": user[2],
                    "xp": user[3],
                    "detailed_xp": user[4],
                    "level": user[5],
                    "messages": user[6],
                    "avatar": avatar(user[7], user[0], int(user[2])),
                    "gang": user[8],
                    "prestige": user[9],
                    "rank": user[10],
                }
                for user in cur.fetchall()
            ],
            f
        )
