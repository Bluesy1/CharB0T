---
layout: default
title: Mod Support Module
permalink: /docs/tickets
---

# Support Tickets

## Checks

```python
async def edit_check(interaction: Interaction) -> bool:
    user = interaction.user
    assert isinstance(user, discord.Member)
    return any(
        role.id in (0, 1, 2, 3)
        for role in user.roles
    )
```

- Used to restrict the blacklisting commands to moderators only.

```python
async def interaction_check(self, interaction: Interaction) -> bool:
    with open(self.filename, "r", encoding="utf8") as file:
        return interaction.user.id not in json.load(file)["blacklisted"]
```

- Used to restrict who can open a ticket.

## Commands

- All are restricted under the first check above.

### Query

```python
async def query(self, interaction):
	# Check if the user is a mod (check 1 above)
	with open("blacklist.json", "r", encoding="utf8") as file:
	    blacklisted = [
	        f"<@{item}>" for item in json.load(file)["blacklisted"]
	    ]
	await interaction.response.send_message(
	    embed=Embed(
	        title="Blacklisted users", description="\n".join(blacklisted)
	    ),
	    ephemeral=True,
	)
```

- Sends a list of blacklisted users.
- The list is dynamic and depends on who is blacklisted at the time the command is run

### Edit

```python
async def edit(self, interaction, add: bool, user):
	 # Check if the user is a mod (check 1 above)
	 if add:
	    successful = False
	    with open("blacklist.json", "r", encoding="utf8") as file:
	        modmail_blacklist = json.load(file)
	    if user.id not in modmail_blacklist["blacklisted"]:
	        modmail_blacklist["blacklisted"].append(user.id)
	        with open("blacklist.json", "w", encoding="utf8") as file:
	            json.dump(modmail_blacklist, file)
	        successful = True
	else:
	    successful = False
	    with open("blacklist.json", "r", encoding="utf8") as file:
	        modmail_blacklist = json.load(file)
	    if user.id in modmail_blacklist["blacklisted"]:
	        modmail_blacklist["blacklisted"].remove(user.id)
	        with open("blacklist.json", "w", encoding="utf8") as file:
	            json.dump(modmail_blacklist, file)
	        successful = True
	await interaction.response.send_message(
		"Depends on success and blacklisting/unblacklisting",
	)
```

 - Adds or removes a user from the blacklist.
 - The list is dynamic and depends on who is blacklisted at the time the command is run

## Ticket System

- All buttons under the ticket system are restricted by the second check above.

### Standard callback

```python
async def standard_callback(self, button, interaction):
    user = interaction.user
    assert isinstance(user, discord.Member)
    await interaction.response.send_modal(
        ModSupportModal(
            {
                self.mod_role: PermissionOverwrite(
                    view_channel=True, read_messages=True
                ),
                self.everyone: PermissionOverwrite(
                    view_channel=False, read_messages=False
                ),
                user: PermissionOverwrite(
                    view_channel=True, read_messages=True
                ),
            },
            f"{button.label}-{user.name}-mod-support",
        )
    )
```

- Used to open a `General`, `Important`, or `Emergency` ticket.

### Private callback

```python
    )
async def private(self, interaction: Interaction, select: discord.ui.Select):
    user = interaction.user
    assert isinstance(user, discord.Member)
    perms = {
        self.mod_role: PermissionOverwrite(
            view_channel=False, read_messages=False
        ),
        self.everyone: PermissionOverwrite(
            view_channel=False, read_messages=False
        ),
        user: PermissionOverwrite(
            view_channel=True, read_messages=True
        ),
    }
    for uid in select.values:
        perms.update(
            {self.mods[uid]: PermissionOverwrite(
                view_channel=True, read_messages=True
            )}
        )
    await interaction.response.send_modal(
        ModSupportModal(perms, f"Private-{user.name}-mod-support")
        )
```

 - Used to open a private ticket, with limited access for moderators.

### Mod support Form

- Also has the second check above.

#### Fields

```python
short_description = ui.TextInput(
    label="Short Description of your problem/query",
    style=discord.TextStyle.short,
    placeholder="Short description here ...",
    required=True,
    custom_id="Short_Description",
    max_length=100,
)

full_description = ui.TextInput(
    label="Full description of problem/query.",
    style=discord.TextStyle.paragraph,
    placeholder="Put your full description here ...",
    required=False,
    custom_id="Long_Desription",
)
```

#### On submit

```python
async def on_submit(self, interaction: Interaction):
	category = await interaction.client.fetch_channel(0)
	guild = interaction.guild
	topic = self.short_description.value
	assert isinstance(_channel, discord.CategoryChannel)
	assert isinstance(_guild, discord.Guild)
	assert isinstance(topic, str)
	channel = await guild.create_text_channel(
		self.channel_name,
		category=category,
		overwrites=self.perm_overrides,
		topic=topic
	)
	long = "     They supplied a longer description: "
	await channel.send(
	    f"{interaction.user.mention} has a new issue/question/request:\n"
	    f"{self.short_description.value}."
	    f"{long if self.full_description.value else ''}",
	    allowed_mentions=discord.AllowedMentions(users=True),
	)
	if self.full_description.value:
	    await channel.send(self.full_description.value)
	await interaction.response.send_message(
		f"Channel Created: {channel.mention}", ephemeral=True
	)
```

 - Used to create a new channel for the ticket.
 - The channel is created with the short description as the topic.
 - Sends a message to the channel with the long description as the content.

## Back to [top](./tickets) / [features](.)
