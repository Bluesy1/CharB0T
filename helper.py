import json

import hikari
import lightbulb
from hikari import Permissions, PermissionOverwrite, PermissionOverwriteType


def _punished(context: lightbulb.Context):
    """Checks if command user is punished"""
    for role in context.member.role_ids:
        print(role)
        if role in [684936661745795088, 676250179929636886]:
            print(False)
            raise lightbulb.errors.CheckFailure
    return True


punished = lightbulb.Check(_punished)

MOD_SENSITIVE = PermissionOverwrite(
    id=338173415527677954,
    type=PermissionOverwriteType.ROLE,
    allow=Permissions.NONE,
    deny=(Permissions.VIEW_CHANNEL | Permissions.SEND_MESSAGES)
)

MOD_GENERAL = PermissionOverwrite(
    id=338173415527677954,
    type=PermissionOverwriteType.ROLE,
    allow=(Permissions.VIEW_CHANNEL | Permissions.SEND_MESSAGES),
)

EVERYONE_MODMAIL = PermissionOverwrite(
    id=225345178955808768,
    type=PermissionOverwriteType.ROLE,
    deny=(Permissions.VIEW_CHANNEL | Permissions.SEND_MESSAGES),
)


def user_perms(user_id: hikari.Snowflakeish):
    """Creates a permission overwrite for a user with the given ID"""
    return PermissionOverwrite(
        id=user_id,
        type=PermissionOverwriteType.MEMBER,
        allow=(Permissions.VIEW_CHANNEL | Permissions.SEND_MESSAGES),
    )


def make_modmail_buttons(plugin: lightbulb.Plugin):
    """Creates a button row"""
    return [
        (plugin.bot.rest.build_action_row().add_button(hikari.ButtonStyle.DANGER, "Emergency Header")
         .set_label("EMERGENCY").set_emoji("‼").set_is_disabled(True).add_to_container()
         .add_button(hikari.ButtonStyle.PRIMARY, "Emergency_Sensitive")
         .set_label("Sensitive").set_emoji("❗").add_to_container()
         .add_button(hikari.ButtonStyle.SUCCESS, "Emergency_General")
         .set_label("General").set_emoji("⁉").add_to_container()),
        (plugin.bot.rest.build_action_row().add_button(hikari.ButtonStyle.DANGER, "Important Header")
         .set_label("IMPORTANT").set_emoji("⚠").set_is_disabled(True).add_to_container()
         .add_button(hikari.ButtonStyle.PRIMARY, "Important_Sensitive")
         .set_label("Sensitive").set_emoji("❗").add_to_container()
         .add_button(hikari.ButtonStyle.SUCCESS, "Important_General")
         .set_label("General").set_emoji("⁉").add_to_container()),
        (plugin.bot.rest.build_action_row().add_button(hikari.ButtonStyle.DANGER, "Question Header")
         .set_label("QUESTION").set_emoji("❓").set_is_disabled(True).add_to_container()
         .add_button(hikari.ButtonStyle.PRIMARY, "Question_Sensitive")
         .set_label("Sensitive").set_emoji("❗").add_to_container()
         .add_button(hikari.ButtonStyle.SUCCESS, "Question_General")
         .set_label("General").set_emoji("⁉").add_to_container()),
        (plugin.bot.rest.build_action_row().add_button(hikari.ButtonStyle.DANGER, "Other Header")
         .set_label("OTHER").set_emoji("❔").set_is_disabled(True).add_to_container()
         .add_button(hikari.ButtonStyle.PRIMARY, "Other_Sensitive")
         .set_label("Sensitive").set_emoji("❗").add_to_container()
         .add_button(hikari.ButtonStyle.SUCCESS, "Other_General")
         .set_label("General").set_emoji("⁉").add_to_container())]


def blacklist_user(user_id: hikari.Snowflakeish) -> bool:
    """Adds a user to the blacklist"""
    with open("modmail_blacklist.json", "r", encoding="utf8") as file:
        modmail_blacklist = json.load(file)
    if user_id not in modmail_blacklist["blacklisted"]:
        modmail_blacklist["blacklisted"].append(user_id)
        with open("modmail_blacklist.json", "w", encoding="utf8") as file:
            json.dump(modmail_blacklist, file)
        return True
    return False


def un_blacklist_user(user_id: hikari.Snowflakeish) -> bool:
    """Removes a user from the blacklist"""
    with open("modmail_blacklist.json", "r", encoding="utf8") as file:
        modmail_blacklist = json.load(file)
    if user_id in modmail_blacklist["blacklisted"]:
        modmail_blacklist["blacklisted"].remove(user_id)
        with open("modmail_blacklist.json", "w", encoding="utf8") as file:
            json.dump(modmail_blacklist, file)
        return True
    return False


def get_blacklist() -> list[hikari.Snowflakeish]:
    """Returns the User Blacklist"""
    with open("modmail_blacklist.json", "r", encoding="utf8") as file:
        return json.load(file)["blacklisted"]


def check_not_modmail_blacklisted(user_id: hikari.Snowflakeish) -> bool:
    """
    Checks if a user is in the blacklist
    Returns True if a user is allowed to use modmail buttons, False if not.
    """
    with open("modmail_blacklist.json", "r", encoding="utf8") as file:
        modmail_blacklist = json.load(file)
    return user_id not in modmail_blacklist["blacklisted"]
