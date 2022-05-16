---
layout: default
title: Changelog
permalink: /changes
---
## CharB0T Changelog
Base version: commit [975c554d](https://github.com/Bluesy1/CharB0T/commit/975c554d52ecabb299ea66e7f8fba5f0fbd16cae)

Important changes as of commit [975c554d](https://github.com/Bluesy1/CharB0T/commit/975c554d52ecabb299ea66e7f8fba5f0fbd16cae):
-----------------------------------------------------

 - Added a dynamic [calendar](https://github.com/Bluesy1/CharB0T/blob/main/charbot/gcal.py) that links to Charlie's Google calendar.
 - Added 3 games that generate reputation, [tictactoe](https://github.com/Bluesy1/CharB0T/blob/main/charbot/tictactoe.py), [shrugman](https://github.com/Bluesy1/CharB0T/blob/main/charbot/shrugman.py), and [sudoku](https://github.com/Bluesy1/CharB0T/blob/main/charbot/sudoku.py).
 - Added a daily reputation generator command, [rollcall](https://github.com/Bluesy1/CharB0T/blob/main/charbot/giveaway.py).
 - Added a reputation queryier command, [reputation](https://github.com/Bluesy1/CharB0T/blob/main/charbot/giveaway.py).
 - Added a giveaway system, [giveaway](https://github.com/Bluesy1/CharB0T/blob/main/charbot/giveaway.py).
 - Added initial code for a [pool](https://github.com/Bluesy1/CharB0T/blob/main/charbot/pools.py) system.
 - Added media for the pool system, [pools](https://github.com/Bluesy1/CharB0T/blob/main/charbot/media/pools).
 - Added media for [tictactoe](https://github.com/Bluesy1/CharB0T/blob/main/charbot/media/tictactoe).
 - Added a mod support system, [mod](https://github.com/Bluesy1/CharB0T/blob/main/charbot/mod_support.py).
 - Fixed a possible [race condition](https://en.wikipedia.org/wiki/Race_condition) that could cause undesireable behavior in bidding in [giveaways](https://github.com/Bluesy1/CharB0T/blob/main/charbot/giveaway.py).
 - Added a command that links to this [changelog](https://github.com/Bluesy1/CharB0T/blob/main/charbot/query.py#L95)
 - Added this changelog.

Monday, May 9th 2022
-------------------

 - Added [administration](https://github.com/Bluesy1/CharB0T/blob/main/charbot/reputation_admin.py) commands for the pools and reputation system.
 - Updated [giveaway](https://github.com/Bluesy1/CharB0T/blob/main/charbot/giveaway.py) system to reload games list csv every day instead of every time the cog is loaded.
 - Updated images for [pools](https://github.com/Bluesy1/CharB0T/blob/main/charbot/media/pools).
 - Updated masking for [cards](https://github.com/Bluesy1/CharB0T/blob/main/charbot/card.py) to better suit the new images.
 - Change title [font](https://github.com/Bluesy1/CharB0T/blob/main/charbot/media/pools/font2.ttf) to [batman](https://freefontsvault.com/batman-font-free-download/#more-7850).
 - Change text [color](https://github.com/Bluesy1/CharB0T/blob/main/charbot/card.py) to white.

Tuesday, May 10th 2022
---------------------

 - Made the [pool](https://github.com/Bluesy1/CharB0T/blob/main/charbot/pools.py) system user commands public.
