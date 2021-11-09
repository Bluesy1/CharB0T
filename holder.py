
def get_file(name):
    with open('{}.json'.format(name), 'r') as f:
        return json.load(f)


def is_admin(ctx):
    perms = ctx.author.guild_permissions
    return perms.administrator


@client.event
async def on_message(ctx):
    await client.process_commands(ctx)
    if ctx.author == client.user:
        return
    message_str = ctx.content
    url_obj = match_url(message_str)
    #logging.info(url_obj)
    if valid_url(url_obj[1]):
        if "discord.gift" in url_obj[1] or "media.discordapp.net/attachments" in url_obj[1] or 'cdn.discordapp.com/attachments' in url_obj[1] or 'discord.com/channels/225345178955808768' in url_obj[1] or 'youtube.com' in url_obj[1] or 'cpry.net' in url_obj[1] or 'twitter.com' in url_obj[1] or 'twitch.tv' in url_obj[1]:
            return
        match_url_precent = similarity_search(["discord", "nitro", "gift", "free", "giveaway"], url_obj[1], ".")
        match_percent = similarity_search(["nitro", "gift", "free", "giveaway"], message_str, " ")
        print(match_url_precent, match_percent)
        if match_url_precent >= 0.7 and match_percent >= 0.8:
            embed = to_embed(title="Likely Nitro Scam",
                                description="<@!{}> sent a message in <#{}> which has a {}% match".format(
                                    ctx.author.id, ctx.channel.id, int(max(match_percent, match_url_precent) * 100)),
                                field_name="Message",
                                field_value="{}".format(message_str))
            if max(match_percent, match_url_precent) > 0.85:
                bot_channel = get_file("info")
                try:
                    role_id = bot_channel[str(ctx.guild.id)]["role"]
                    role = ctx.guild.get_role(role_id)
                except KeyError:
                    role = None
                if role is not None:
                    await ctx.author.add_roles(role)
                    embed.add_field(name="Certain Match",
                                    value="<@!{}> was permanently muted".format(ctx.author.id))
                else:
                    embed.add_field(name="Certain Match",
                                    value="Unable to mute <@!{}>. No `Muted` Role Exists".format(ctx.author.id))
            record_channel = get_channel(ctx)
            if record_channel != ctx.channel:
                await record_channel.send(embed=embed)
            remove_embed = to_embed(title="Nitro Scam",
                                    description="Message removed for {}% match".format(int(match_percent*100)))
            await ctx.channel.send(embed=remove_embed)
            await ctx.delete()
        elif (match_url_precent >= 0.5 and match_percent >= 0.6) or match_url_precent >= 0.7:
            embed = to_embed(title="Possible Nitro Scam",
                                description="<@!{}> sent a message in <#{}> which has a {}% match".format(
                                    ctx.author.id, ctx.channel.id, int(max(match_percent, match_url_precent) * 100)),
                                field_name="Message",
                                field_value="{}\n\n `Not Deleted - 80% Match Required`".format(message_str))
            record_channel = get_channel(ctx)
            if record_channel != ctx.channel:
                await record_channel.send(embed=embed)



def to_embed(title=None, description=None, field_name=None, field_value=None):
    embed_var = discord.Embed(
        title=title, description=description, color=0xa5a5a5)
    if field_name is not None or field_value is not None:
        embed_var.add_field(name=field_name, value=field_value, inline=False)
    embed_var.set_footer(
        text="Nitro Scam Detection Coded by Bawnorton#0001")
    return embed_var


def get_channel(ctx):
    bot_channels = get_file('info')
    try:
        record_channel = client.get_channel(int(bot_channels[str(ctx.guild.id)]["channel"]))
    except KeyError:
        return ctx.channel
    return record_channel


def similarity_search(criteria, message_str, delimter) -> float:
    match_percent = 0.0
    match_count = 0
    words = message_str.replace("/", ".").split(delimter)
    for word in words:
        for matching in criteria:
            current_match = similarity(word.lower(), matching.lower())
            if current_match > 0.7:
                match_count += 1
            if current_match > match_percent:
                match_percent = current_match
    match_percent += match_percent * (match_count * 0.1)
    return min(match_percent, 1)


def similarity(a, b) -> float:
    return SequenceMatcher(None, a, b).ratio()


def match_url(message_str) -> (str):
    try:
        http_index = message_str.index("http")
    except ValueError:
        return False, ""
    link_extra = message_str[http_index:]
    try:
        space_index = link_extra.index(" ")
    except ValueError:
        return True, link_extra
    link = link_extra[:space_index]
    return True, link


def valid_url(url):
    response = validators.url(url)
    return response