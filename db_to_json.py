import psycopg2
import orjson
from os import getenv
from typing import Callable

_: Callable[[str], str | None] = lambda x: getenv(f"{x.upper()}")


conn = psycopg2.connect(database=_("db"), user=_("db_user"), password=_("pass"), host=_("host"), port=_("port"))


def avatar(avatar_hash: str | None, user_id: int, discriminator: int) -> str:
    if avatar_hash is None:
        return f"https://cdn.discordapp.com/embed/avatars/{discriminator % 5}.png"
    return f"https://cdn.discordapp.com/avatars/{user_id}/{avatar_hash}.png"


def get_str(xp):
    if xp < 1000:
        return str(xp)
    if 1000 <= xp < 1000000:
        return str(round(xp / 1000, 1)) + "k"
    if xp > 1000000:
        return str(round(xp / 1000000, 1)) + "M"


with conn, conn.cursor() as cur:
    cur.execute("SELECT *, ROW_NUMBER() OVER(ORDER BY xp DESC) FROM xp_users ORDER BY xp DESC")
    with open("_data/users.json", "b") as r:
        old = r.read()
    with open("_data/users.json", "wb") as f:
        new = orjson.dumps(
                [
                    {
                        "id": str(user[0]),
                        "name": user[1],
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
                option=orjson.OPT_INDENT_2,
            )
        if old != new:
            f.write(new)
        with open(_("github_env"), "a") as envfile:
            envfile.write(f"DO_COMMIT={'true' if old != new else 'false'}")
