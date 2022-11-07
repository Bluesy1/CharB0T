# SPDX-FileCopyrightText: 2021 Bluesy1 <68259537+Bluesy1@users.noreply.github.com>
#
# SPDX-License-Identifier: MIT

### Error messages for the bot to respond with


missing-program-role = You are missing at least one of the required roles: { $roles } - you must be at least level 1 to use this command/button.
wrong-channel = This command can only be run in the channel <#{ $channel-id }> .
no-pool-found = { $pool } pool not found. Please choose one from the autocomplete.
missing-any-role = { $user }, you don't have any of the required role(s) to use { $command }.
check-failed = { $user }, you can't use { $command }.
bad-code = { $user }, an error occurred while executing { $command }, Bluesy has been notified.
command-on-cooldown = { $user }, this command is on cooldown for { $retry_after } seconds you can retry after { $unix-timestamp }.
