---
layout: default
title: Changelog
permalink: /changes
---

{% assign github = site.data.links["github"].url %}
## CharB0T Changelog
Base version: commit [975c554d](https://github.com/Bluesy1/CharB0T/commit/975c554d52ecabb299ea66e7f8fba5f0fbd16cae)

Tuesday, October 25th 2022
-------------------------
- Switch to a proper [semver](https://semver.org/) system for versioning charbot, and release [charbot 1.0.0.post0](https://github.com/Bluesy1/CharB0T/releases/tag/v1.0.0)
- Add a rust portion of the bot, [charbot_rust]({{github}}/charbot_rust), to handle parts of the bot that better work in compiled languages, or frameworks better developed outside the python ecosystem.
- Future releases and changelogs will happen along version bumps to the bot, which can be tracked [here](https://github.com/Bluesy1/CharB0T/releases). This allows a proper commit diff to be viewed for changes from relese to release, in case things are left out of the changelog. Further, a release will generally mark new code being pushed to the live running instance, outside of security issues, which need to be patched and running before announced, or extenuating circumstances like rapid development requiring code be tested on live.

Thursday, June 9th 2022
----------------------

 - Added a leveling system, [levels]({{github}}/charbot/levels.py).
 - Fixed a bug in the hard mode of [tictactoe]({{github}}/charbot/programs).
 - Fixed an issue with [tictactoe]({{github}}/charbot/programs) where the image wouldn't appear in an embed properly.

Wednesday, May 25th 2022
--------------------

- Split out the programs into sub modules [sudoku]({{github}}/charbot/programs),
  [tictactoe]({{github}}/charbot/programs), and [shrugman]({{github}}/charbot/programs).
- Added them to a single group cog for ease of ux, [programs]({{github}}/charbot/programs).
- Added Feature Requests and Bug Report Issue templates.
- Added [greetings]({{github}}/.github/workflows/greetings.yml) GHA.
- Subclasses the default discord.py command tree and moved the subclassed bot class to their own file,
  [bot]({{github}}/charbot/bot.py).
- Updated ping [(admin)]({{github}}/charbot/admin.py) command to include Rest Ping, Typing Latency, and
  Database Latency on top of Websocket Latency.
- Updated [card]({{github}}/charbot/card.py) generation system to credits the author of disrank for the code I modified 
  and made it so the code auto generated the color circle.
  - License was already MIT so it was able to be used in my code.
- Depreciated the markdown [changelog]({{github}}/charbot/changelog.md) file, will be removed shortly in
  favor of this page.
- Custom Errors for the new error handlers i've added
- Reroute all non error event handling to a single events extension file, [events]({{github}}/charbot/events.py).
- Centralized the giveaway and reputation constants to bot variables.
- Added a factory method to recreate a giveaway object from a [message]({{github}}/charbot/giveaway) object.
- Updated the giveaway [draw]({{github}}/charbot/giveaway) to list names+discriminators for winners on top of pings
  to fix client caching issue.
  - Require two extra API requests to get the backup winners member objects from the discord API.
- Moved rollcall and reputation commands to [programs]({{github}}/charbot/programs) from
  [giveaway]({{github}}/charbot/giveaway)
  to avoid the issue described in this [postmortem](/CharB0T{% post_url 2022-05-22-giveaway-error-postmortem %}).
- Made sure people can't trigger [pool]({{github}}/charbot/pools.py) completion once a pool is complete,
- limiting it to one announcement per pool being full.
- Moved all the programs commands to the [programs]({{github}}/charbot/programs) group to combine it into one group.
- Updated [query]({{github}}/charbot/query.py) to have correct responses and removed one temporary joke command.

Tuesday, May 10th 2022
---------------------

 - Made the [pool]({{github}}/charbot/pools.py) system user commands public.

Monday, May 9th 2022
-------------------

 - Added [administration]({{github}}/charbot/reputation_admin.py) commands for the pools and reputation system.
 - Updated [giveaway]({{github}}/charbot/giveaway) system to reload games list csv every day instead of every time the cog is loaded.
 - Updated images for [pools]({{github}}/charbot/media/pools).
 - Updated masking for [cards]({{github}}/charbot/card.py) to better suit the new images.
 - Change title [font]({{github}}/charbot/media/pools/font2.ttf) to [batman](https://freefontsvault.com/batman-font-free-download/#more-7850).
 - Change text [color]({{github}}/charbot/card.py) to white.

Important changes as of commit [975c554d](https://github.com/Bluesy1/CharB0T/commit/975c554d52ecabb299ea66e7f8fba5f0fbd16cae):
-----------------------------------------------------

 - Added a dynamic [calendar]({{github}}/charbot/gcal.py) that links to Charlie's Google calendar.
 - Added 3 games that generate reputation, [tictactoe]({{github}}/charbot/programs), 
  [shrugman]({{github}}/charbot/programs), and [sudoku]({{github}}/charbot/programs).
 - Added a daily reputation generator command, [rollcall]({{github}}/charbot/giveaway).
 - Added a reputation query command, [reputation]({{github}}/charbot/giveaway).
 - Added a giveaway system, [giveaway]({{github}}/charbot/giveaway.py).
 - Added initial code for a [pool]({{github}}/charbot/pools.py) system.
 - Added media for the pool system, [pools]({{github}}/charbot/media/pools).
 - Added media for [tictactoe]({{github}}/charbot/media/tictactoe).
 - Added a mod support system, [mod]({{github}}/charbot/mod_support.py).
 - Fixed a possible [race condition](https://en.wikipedia.org/wiki/Race_condition) that could cause undesirable behavior
  in bidding in [giveaways]({{github}}/charbot/giveaway).
 - Added a command that links to this [changelog]({{github}}/charbot/query.py)
 - Added this changelog.
