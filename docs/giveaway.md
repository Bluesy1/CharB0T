---
layout: default
title: Giveaway Module
permalink: /docs/giveaway
---

# Giveaway Module

## Giveaway

### Check

```python
async def interaction_check(self, interaction):
    user = interaction.user
    assert isinstance(user, discord.Member)
    if not any(role.id in self.bot.ALLOWED_ROLES for role in user.roles):
        raise errors.MissingProgramRole(self.bot.ALLOWED_ROLES)
    return True
```

### Bid

```python
async def bid(self, interaction, button):
    # Get an asyncpg connection from the connection pool
    async with self.bot.pool.aquuire() as conn:
        last_win = await conn.fetchval(
        "SELECT expiry FROM winners WHERE id = $1", interaction.user.id
        ) or self.bot.TIME() - datetime.timedelta(days=1)
        if last_win > self.bot.TIME():
            await respond(
                interaction, "You can't bid until your last win has expired."
            )
            return
        # check if they have an expired win
        if last_win != self.bot.TIME() - datetime.timedelta(days=1):
            await conn.execute(
                "DELETE FROM winners WHERE id = $1", interaction.user.id
            )
    modal = BidModal(self.bot, self)
    await interaction.response.send_modal(modal)
    await modal.wait()
    # do stuff to update the message
```

- The `BidModal` class is a subclass of `discord.ui.Modal`, code which opens a model which is documented below.
- Before a modal is opened, the interaction user is checked to see if the have a valid program role.
  - The interaction user is then checked to see if they have an unexpired win.
- The interaction user is then sent a modal which contains the form.

#### Used SQL:

```sql
SELECT expiry FROM winners WHERE id = your_id;

DELETE FROM winners WHERE id = your_id;
```

 - `winners` table is used to keep track of the last time a user won.
 - `expiry` is the day the user can start to bid again.
 - `id` is the user's id.
 - The dialect is `postgresql`

#### Bid Modal

Question Definition:
```python
    bid_str = ui.TextInput(
        label="How much to increase your bid by?",
        placeholder="Enter your bid (Must be an integer between 0 and 32768)",
        style=discord.TextStyle.short,
        min_length=1,
        max_length=5,
        required=True,
    )
```

Submit Processing:
```python
    async def submit(self, interaction):
    # Extract bid and verify it is an allowed integer between 0 and 32768
    # we get it as a string becaue discord only allows string inputs in modals
    try:
        val = self.bid_str.value
        assert isinstance(val, str)
        bid_int = int(val)
    except ValueError:
        await respond("Please enter a valid integer between 0 and 32768.")
        return self.stop()
    if 0 > bid_int < 32768:
        await respond("Please enter a valid integer between 0 and 32768.")
        return self.stop()
    await interaction.response.defer(ephemeral=True, thinking=True)
    # Get a locked asyncpg connection from the connection pool
    async with self.view.bid_lock, self.bot.pool.acquire() as conn, ...:
            points: int | None = await conn.fetchval(
              "SELECT points FROM users WHERE id = $1", interaction.user.id
            )
            if points is None or points == 0:
                await send("You either have never gained reputation or have 0.")
                return self.stop()
            if points < bid_int:
                await send(
                    f"You do not have enough reputation to bid {bid_int} more. You have {points} reputation."
                )
                return self.stop()
            bid_int = min(bid_int, points)
            current_bid = await conn.fetchval("SELECT bid FROM bids WHERE id = $1", interaction.user.id) or 0
            if current_bid + bid_int > 32768:
                bid_int = 32768 - current_bid
            points: int | None = await conn.fetchval(
                "UPDATE users SET points = points - $1 WHERE id = $2 RETURNING points", bid_int, interaction.user.id
            )
            if points is None:
                warnings.warn("Points should not be None at this code.", RuntimeWarning)
                points = 0
                await conn.execute("UPDATE users SET points = 0 WHERE id = $1", interaction.user.id)
            new_bid: int | None = await conn.fetchval(
                "UPDATE bids SET bid = bid + $1 WHERE id = $2 RETURNING bid", bid_int, interaction.user.id
            )
            if new_bid is None:
                warnings.warn("Bid should not be None at this code.", RuntimeWarning)
                new_bid = bid_int
                await conn.execute(
                    "INSERT INTO bids (bid,id) values ($1, $2) ON CONFLICT DO UPDATE SET bid = $1",
                    bid_int,
                    interaction.user.id,
                )
```

## Back to [top](./giveaway) / [features](.)