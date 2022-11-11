# SPDX-FileCopyrightText: 2021 Bluesy1 <68259537+Bluesy1@users.noreply.github.com>
#
# SPDX-License-Identifier: MIT

### Messages for the minesweeper program to reply with

## Selects labels, descriptions, and placeholders

minesweeper-select-row-label = Row { $letter }
minesweeper-select-row-description = Change the row to { $letter }
minesweeper-select-row-placeholder = Select a row
minesweeper-select-col-label = Column { $letter }
minesweeper-select-col-description = Change the column to { $letter }
minesweeper-select-col-placeholder = Select a column

# Image alt text
minesweeper-image-alt-text = Minesweeper Board

## Button labels

minesweeper-reveal-label = Reveal
#Chord is not in the musical sense, but as the following move: http://www.minesweeper.info/wiki/Chord
minesweeper-chord-label = Chord
minesweeper-flag-label = Flag
minesweeper-quit-label = Quit
minesweeper-help-label = Help

## Lose messages

minesweeper-lose-title = You lost!
minesweeper-lose-description = You revealed a mine and lost the game. You gained { $awarded } points.
minesweeper-lose-hit-cap-description = You revealed a mine and lost the game. You gained { $awarded } points. (Hit daily cap)

## Win messages

minesweeper-win-title = You won!
minesweeper-win-description = You revealed all the safe tiles and won the game. You gained { $awarded } points.
minesweeper-win-hit-cap-description = You revealed all the safe tiles and won the game. You gained { $awarded } points. (Hit daily cap)

## Quit messages

minesweeper-quit-title = You quit!
minesweeper-quit-description = You quit the game without completing it

## Error messages

minesweeper-reveal-flag-fail = WARNING: you tried to reveal a flagged cell. Instead of revealing it, it was unflagged. If you meant to reveal it, press reveal again.
#Chord is not in the musical sense, but as the following move: http://www.minesweeper.info/wiki/Chord
minesweeper-chord-error = WARNING: you tried to chord a cell that was not revealed, not a number, or didn't have the appropriate number of surrounding tiles marked.
minesweeper-flag-error = WARNING: you tried to flag a revealed cell. This move was ignored.

## Help messages

minesweeper-help-title = Minesweeper
minesweeper-help-description = How to play minesweeper:
minesweeper-help-reveal-title = Reveal { "\u26cf" }
minesweeper-help-reveal-description = Reveal a covered tile.
#Chord is not in the musical sense, but as the following move: http://www.minesweeper.info/wiki/Chord
minesweeper-help-chord-title = Chord { "\u2692" }
#Chord is not in the musical sense, but as the following move: http://www.minesweeper.info/wiki/Chord
minesweeper-help-chord-description = Reveal all tiles around an exposed number that has the correct number of flagged tiles around it. This will explode mines.
minesweeper-help-flag-title = Flag { "\U01f6A9" }
minesweeper-help-flag-description = Flag a tile, or remove the flag from a flagged tile.
minesweeper-help-quit-title = Quit { "\u2620" }
minesweeper-help-quit-description = Quit the game.
minesweeper-help-help-title = Help { "\u2049" }
minesweeper-help-help-description = Show this help message.
minesweeper-help-image-alt-text = Example play-through of Minesweeper.
