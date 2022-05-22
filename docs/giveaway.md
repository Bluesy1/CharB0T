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

#### Used [SQL][SQL]

```sql
SELECT expiry FROM winners WHERE id = your_id;

DELETE FROM winners WHERE id = your_id;
````

1. This SQL query is used to check if the user has an unexpired win.
2. This SQL query is used to delete the user's win if it has expired.

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
    # Check if the user has enough rep to bid
    points: int | None = await conn.fetchval(
      "SELECT points FROM users WHERE id = $1", interaction.user.id
    )
    if points is None or points == 0:
      await send("You either have never gained reputation or have 0.")
      return self.stop()
    if points < bid_int:
      await send("You do not have enough reputation.")
      return self.stop()
    bid_int = min(bid_int, points)
    current_bid = await conn.fetchval(
      "SELECT bid FROM bids WHERE id = $1", interaction.user.id
    ) or 0
    # Check if the bot + any previous bids on the giveaway are above the limit
    if current_bid + bid_int > 32768:
        bid_int = 32768 - current_bid
    points: int | None = await conn.fetchval(
      "UPDATE users SET points = points - $1 WHERE id = $2 RETURNING points",
      bid_int,
      interaction.user.id
    )
    if points is None:
      points = 0
      await conn.execute(
          "UPDATE users SET points = 0 WHERE id = $1", interaction.user.id
      )
    new_bid: int | None = await conn.fetchval(
      "UPDATE bids SET bid = bid + $1 WHERE id = $2 RETURNING bid",
       bid_int,
       interaction.user.id
    )
    if new_bid is None:
      await conn.execute(
        "INSERT INTO bids (bid,id) values ($1, $2)"
        " ON CONFLICT DO UPDATE SET bid = $1",
        bid_int,
        interaction.user.id,
      )
    await send("Bid info")
```

- `bid_lock` is a lock that is used to prevent multiple users from bidding at the same time, to prevent race conditions.
  - See [asyncio.Lock](https://docs.python.org/3/library/asyncio-sync.html#asyncio.Lock)
  - In rare circumstances, it was possible for 2 bids to be processed out of order causing them to be lost, so a Lock
  is used to prevent this.
- First the input is validated, and if it is not valid, the user is notified.
- The user's reputation is checked, and if they do not have enough, they are notified.
- The user's current bid is checked, and if the user's bid is above the limit, the user's bid is set to the limit.
- The user's bid is updated in the database.
- The user's reputation is updated in the database.
- The user's bid is returned to the user.

#### Used [SQL][SQL]

```sql
SELECT points FROM users WHERE id = your_id;

SELECT bid FROM bids WHERE id = your_id;

UPDATE users SET points = points - your_bid WHERE id = your_id
    RETURNING points;

UPDATE users SET points = 0 WHERE id = your_id;

UPDATE bids SET bid = bid + your_bid WHERE id = your_id RETURNING bid;

INSERT INTO bids (bid,id) values (your_bid, your_id)
    ON CONFLICT DO UPDATE SET bid = your_bid;
```

1. Used to get how many points the user has.
2. Used to get the user's current bid.
3. Used to update the user's reputation after processing is done to make sure the bid isn't too high.
  Returns the user's new reputation. [RETURNING](https://www.postgresql.org/docs/current/dml-returning.html)
  is used to get the new reputation.
4. Used to update the user's reputation to 0 if they have no points.
5. Used to update the user's bid after processing is done to make sure the bid isn't too high.
6. Used to insert the user's bid if they don't have one. 
  `ON CONFLICT DO UPDATE` is used to update the user's bid if they already have one, and the query is somehow run, 
  to avoid a primary key violation error.

### Check Bid

```python
async def check(self, interaction, button):
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
            record = await conn.fetchval(
              "SELECT bid FROM bids WHERE id = $1", interaction.user.id
            )
    bid: int = record if record is not None else 0
    chance = bid * 100 / self.total_entries
    await interaction.response.send_message("Bid Info", ephemeral=True)
```

 - Checks if the user has an unexpired win.
 - If they do, they can't bid.
 - If they don't, they get their current bid.
 - If they have an expired win, it gets deleted.

#### Used [SQL][SQL]

```sql
SELECT expiry FROM winners WHERE id = your_id;

DELETE FROM winners WHERE id = your_id;

SELECT bid FROM bids WHERE id = your_id;
```

1. This SQL query is used to check if the user has an unexpired win.
2. This SQL query is used to delete the user's win if it has expired.
3. This SQL query is used to get the user's current bid.

### Toggle Alerts

```python
  async def toggle_alerts(self, interaction, button):
      await interaction.response.defer(ephemeral=True, thinking=True)
      user = interaction.user
      assert isinstance(user, discord.Member)
      role = discord.Object(id=972886729231044638)
      async with self.role_semaphore:
          if not any(role.id == 972886729231044638 for role in user.roles):
              await user.add_roles(role, reason="Toggled giveaway alerts.")
              await send("You will now receive giveaway alerts.")
          else:
              await user.remove_roles(role, reason="Toggled giveaway alerts.")
              await send("You will no longer receive giveaway alerts.")

```

 - Checks if the user has the giveaway alerts role.
 - If they do, they are removed.
 - If they don't, they are added.
 - The user is then notified of the success or failure of the operation.
 - The semaphore is used to prevent spamming the bot/API with requests and to prevent the bot from being overloaded,
  or getting rate-limited.

## Giveaway Task Loop

- End the previous giveaway and announce the winner and backups.
- Announce and start the next giveaway, after refreshing the game list on case of silent updates.

## Back to [top](./giveaway) / [features](.) / [SQL Structure][SQL]

[SQL]: ./database
