---
layout: default
title: Admin Module
permalink: /docs/admin
---

# Admin Module

## Checks

 - Must be a mod
 - Must be in a guild

## Ping

 - No parameters
 - Returns a message with the websocket latency

## Sensitive

- Hybrid Group Parent of sensitive words command settings
- Can be invoked as a slash **\\** or prefix **!** command

### add

 - Adds a word to the sensitive words list
   - Adaption of actual code for clarity and readability, real code is inline and varys as implementation requires
 - **word**: The word to add
 - Responds with a message with the full list of words

### remove

 - Removes a word from the sensitive words list
   - Adaption of actual code for clarity and readability, real code is inline and varys as implementation requires
 - **word**: The word to remove
 - Responds with a message with the full list of words

### query

 - Responds with a message with the full list of words
 - Adaption of actual code for clarity and readability, real code is inline and varys as implementation requires
 - No parameters

## Confirm Command

- This command is used to confirm a winner.
- It can only be used by the guild owner.
- The time parameter is used to set the expiry time of the win.
- If no time is provided, the win will expire in 6 days.

## Administration Group

 - Must be a mod or higher

### Pools Subgroup

#### Edit Pool

- Select a pool
- Can change any or all of the settings except for the roles, which must be changed separately, and the channel, 
  which cannot be changed.

#### Add Pool

 - Create a new pool, with custom options and roles

#### Remove Pool

 - Remove a pool by name

#### Query Pool

 - Query a pool by name

#### List Pools

 - List all pools

### Reputation Subgroup

#### Add Reputation

 - Add reputation to a user

#### Remove Reputation

 - Remove reputation from a user

#### Query Reputation

 - Query reputation for a user

## Back to [top](./admin) / [features](.)
