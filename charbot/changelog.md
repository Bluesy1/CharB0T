## CharB0T Changelog
Base version: commit [`975c554d`](https://github.com/Bluesy1/CharB0T/commit/975c554d52ecabb299ea66e7f8fba5f0fbd16cae)

Notes:
------

 - Text that looks like `this` is normally a link to the relevant file.

Important changes as of this commit:
-----------------------------------------------------

 - Added a dynamic [`calendar`](/charbot/gcal.py) that links to Charlie's Google calendar.
 - Added 3 games that generate reputation, [`tictactoe`](/charbot/tictactoe.py), [`shrugman`](/charbot/shrugman.py), and [`sudoku`](/charbot/sudoku.py).
 - Added a daily reputation generator command, [`rollcall`](/charbot/giveaway.py).
 - Added a reputation queryier command, [`reputation`](/charbot/giveaway.py).
 - Added a giveaway system, [`giveaway`](/charbot/giveaway.py).
 - Added initial code for a [`pool`](/charbot/pools.py) system.
 - Added media for the pool system, [`pools`](/charbot/media/pools).
 - Added medial for [`tictactoe`](/charbot/media/tictactoe).
 - Added a mod support system, [`mod`](/charbot/mod_support.py).
 - Fixed a possible [`race condition`](https://en.wikipedia.org/wiki/Race_condition) that could cause undesireable behavior in bidding in [`giveaways`](/charbot/giveaway.py).
 - Added a command that links to this [`changelog`](/charbot/query.py#L95)
 - Added this changelog.
