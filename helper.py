# coding=utf-8

import hikari
from hikari import Permissions, PermissionOverwrite, PermissionOverwriteType

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
