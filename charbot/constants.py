# Guilds
GUILD_ID = 225345178955808768
GUILD_IDS = [GUILD_ID]

# Channels
GAMES_FORUM_ID = 1019647326601609338
GAME_SUGGESTIONS_TAG_ID = 1019691620741959730
SPECIAL_CATEGORIES = frozenset(
    [
        360814817457733635,  # Information
        360818916861280256,  # Administration
        942578610336837632,  # Mod Support
        360819195904262144,  # VIP Channels
    ]
)
LINK_ALLOWED_CHANNELS = frozenset(
    [
        723653004301041745,  # Music Channel
        338894508894715904,  # gifs/memes Channel
        407185164200968203,  # Clips
    ]
)


# Roles
LEVEL_1_ID = 969626979353632790
LEVEL_2_ID = 969627321239760967
LEVEL_3_ID = 969628342733119518
LEVEL_4_ID = 969629632028614699
LEVEL_5_ID = 969629628249563166
LEVEL_6_ID = 969629622453039104
LEVEL_ROLE_IDS = frozenset([LEVEL_1_ID, LEVEL_2_ID, LEVEL_3_ID, LEVEL_4_ID, LEVEL_5_ID, LEVEL_6_ID])
MOD_ROLE_IDS = frozenset(
    [
        225413350874546176,  # Charlie
        253752685357039617,  # Admin
        725377514414932030,  # General Staff
        338173415527677954,  # Mod
    ]
)
LEGACY_ROLE_IDS = frozenset(
    [
        337743478190637077,  # Knight
        685331877057658888,  # Fedora
        406690402956083210,  # The Cuz
        387037912782471179,  # The Bro
        729368484211064944,  # IRL Friend
        1359917004932386826,  # Old Guard
    ]
)
SUPPORTER_ROLE_IDS = frozenset(
    [
        338870051853697033,  # Patrons
        733541021488513035,  # Youtube Members
        926150286098194522,  # Twitch Subscribers
        970819808784441435,  # Lifetime VIP (2)
        400445639210827786,  # Lifetime VIP (1)
    ]
)
LINK_ALLOWED_ROLES = MOD_ROLE_IDS | LEGACY_ROLE_IDS | SUPPORTER_ROLE_IDS | (LEVEL_ROLE_IDS - {LEVEL_1_ID})
