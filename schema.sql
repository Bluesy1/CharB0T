-- SPDX-FileCopyrightText: 2022 Bluesy1 <68259537+Bluesy1@users.noreply.github.com>
--
-- SPDX-License-Identifier: MIT

--create types
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'benefit') THEN
        CREATE TYPE benefit AS ENUM
            (
                'control',
                'control_consumable',
                'defense',
                'defense_consumable',
                'offense',
                'offense_consumable',
                'other',
                'other_consumable'
            );
    END IF;
    --more types here...
END$$;

CREATE TABLE IF NOT EXISTS users
(
    id          BIGINT             NOT NULL
        CONSTRAINT points_pk
            PRIMARY KEY,
    points      SMALLINT DEFAULT 0 NOT NULL
);

CREATE TABLE IF NOT EXISTS daily_points
(
    id               BIGINT                   NOT NULL
        CONSTRAINT daily_points_pk
            PRIMARY KEY
        CONSTRAINT daily_user_id_fk
            REFERENCES users
            ON UPDATE CASCADE ON DELETE CASCADE,
    last_claim       TIMESTAMP WITH TIME ZONE NOT NULL,
    last_particip_dt TIMESTAMP WITH TIME ZONE NOT NULL,
    particip         SMALLINT DEFAULT 0       NOT NULL,
    won              SMALLINT DEFAULT 0       NOT NULL
);

CREATE TABLE IF NOT EXISTS bids
(
    id  BIGINT   NOT NULL
        CONSTRAINT bids_pk
            PRIMARY KEY
        CONSTRAINT bids_user_id_fk
            REFERENCES users
            ON UPDATE CASCADE ON DELETE CASCADE,
    bid SMALLINT NOT NULL
);

CREATE TABLE IF NOT EXISTS winners
(
    id   BIGSERIAL
        CONSTRAINT winners_pk
            PRIMARY KEY
        CONSTRAINT winners_users_id_fk
            REFERENCES users
            ON UPDATE CASCADE ON DELETE CASCADE,
    wins SMALLINT DEFAULT 0
);

CREATE TABLE IF NOT EXISTS pools
(
    pool           VARCHAR                                           NOT NULL
        CONSTRAINT pools_pk
            PRIMARY KEY,
    cap            INTEGER                                           NOT NULL,
    current        INTEGER  DEFAULT 0                                NOT NULL,
    reward         VARCHAR                                           NOT NULL,
    level          INTEGER  DEFAULT 1                                NOT NULL,
    start          INTEGER  DEFAULT 0                                NOT NULL,
    required_roles BIGINT[] DEFAULT '{225345178955808768}'::BIGINT[] NOT NULL
);

CREATE TABLE IF NOT EXISTS xp_users
(
    id            BIGINT             NOT NULL
        CONSTRAINT xp_users_pk
            PRIMARY KEY,
    username      VARCHAR(32)        NOT NULL,
    discriminator VARCHAR(4),
    xp            BIGINT   DEFAULT 0 NOT NULL,
    detailed_xp   BIGINT[] DEFAULT '{0,100,0}'::BIGINT[],
    level         INTEGER  DEFAULT 0 NOT NULL,
    messages      BIGINT   DEFAULT 0 NOT NULL,
    avatar        VARCHAR,
    prestige      SMALLINT DEFAULT 0
);

CREATE TABLE IF NOT EXISTS no_xp
(
    guild    BIGINT                          NOT NULL
        CONSTRAINT no_xp_pk
            PRIMARY KEY,
    channels BIGINT[] DEFAULT '{}'::BIGINT[] NOT NULL,
    roles    BIGINT[] DEFAULT '{}'::BIGINT[] NOT NULL
);

CREATE TABLE IF NOT EXISTS deal_no_deal
(
    user_id BIGINT                   NOT NULL
        CONSTRAINT deal_pk
            PRIMARY KEY,
    role_id BIGINT                   NOT NULL,
    until   TIMESTAMP WITH TIME ZONE NOT NULL
);

CREATE INDEX IF NOT EXISTS until_idx on deal_no_deal (until);

CREATE TABLE IF NOT EXISTS banners
(
    user_id  BIGINT                                                                    NOT NULL
        CONSTRAINT banners_pk
            PRIMARY KEY
        CONSTRAINT banners_users_fk
            REFERENCES users(id)
            ON UPDATE CASCADE ON DELETE CASCADE,
    quote    VARCHAR(100)                                                              NOT NULL,
    color    CHAR(8),
    gradient BOOLEAN                                                                   NOT NULL,
    cooldown TIMESTAMP WITH TIME ZONE DEFAULT (CURRENT_TIMESTAMP + '7 days'::interval) NOT NULL,
    approved boolean                  DEFAULT FALSE                                    NOT NULL
);

CREATE TABLE IF NOT EXISTS gangs
(
    name        VARCHAR(32) NOT NULL
        CONSTRAINT gangs_pk
            PRIMARY KEY,
    color       INTEGER     NOT NULL,
    leader      BIGINT      NOT NULL,
    role        BIGINT      NOT NULL,
    channel     BIGINT      NOT NULL,
    control     INTEGER     NOT NULL,
    join_base   SMALLINT    NOT NULL,
    join_slope  NUMERIC(5, 2) NOT NULL,
    upkeep_base SMALLINT    NOT NULL,
    upkeep_slope NUMERIC(5, 2) NOT NULL,
    all_paid    BOOLEAN    NOT NULL
);

CREATE TABLE IF NOT EXISTS territories
(
    id      SERIAL
        CONSTRAINT territories_pk
            PRIMARY KEY,
    name    VARCHAR(32) NOT NULL,
    gang    varchar(32) NOT NULL
        CONSTRAINT territories_gang_fk
            REFERENCES gangs(name)
            ON UPDATE CASCADE ON DELETE CASCADE,
    control SMALLINT     NOT NULL,
    benefit SMALLINT     NOT NULL, -- TODO: Make this reference something meaningful
    raid_end TIMESTAMP WITH TIME ZONE DEFAULT NULL,
    raider varchar(32)
        CONSTRAINT territories_raider_fk
            REFERENCES gangs(name)
            ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS _gang_members
(
    user_id    BIGINT                NOT NULL
        CONSTRAINT gang_members_pk
            PRIMARY KEY
        CONSTRAINT users_fk
            REFERENCES users
            ON UPDATE CASCADE ON DELETE CASCADE,
    gang       VARCHAR(10)           NOT NULL
        CONSTRAINT gangs_fk
            REFERENCES gangs
            ON UPDATE CASCADE ON DELETE CASCADE,
    leadership BOOLEAN DEFAULT FALSE NOT NULL ,
    paid       BOOLEAN DEFAULT TRUE  NOT NULL,
    raiding    BIGINT
        CONSTRAINT _gang_members_territories_null_fk
            REFERENCES territories
            ON UPDATE CASCADE ON DELETE SET NULL
);

CREATE OR REPLACE VIEW gang_members(user_id, gang, leadership, paid, raiding, leader) as
SELECT _gang_members.user_id,
       _gang_members.gang,
       _gang_members.leadership,
       _gang_members.paid,
       _gang_members.raiding,
       CASE
           WHEN (SELECT TRUE AS bool
                 FROM gangs
                 WHERE _gang_members.user_id = gangs.leader) THEN TRUE
           ELSE FALSE
           END AS leader
FROM _gang_members
WITH CASCADED CHECK OPTION;

-- noinspection SqlResolve
CREATE TABLE IF NOT EXISTS benefits
(
    id      SERIAL
        CONSTRAINT benefits_pk
            PRIMARY KEY,
    name    VARCHAR(32) UNIQUE NOT NULL,
    benefit BENEFIT            NOT NULL,
    value  SMALLINT            NOT NULL
);

-- noinspection SqlResolve
CREATE TABLE IF NOT EXISTS user_items
(
    id      SERIAL
        CONSTRAINT user_items_pk
            PRIMARY KEY,
    name    VARCHAR(32)                   NOT NULL,
    benefit BENEFIT                       NOT NULL,
    description VARCHAR(100)   DEFAULT '' NOT NULL,
    value  SMALLINT                       NOT NULL
);

CREATE TABLE IF NOT EXISTS user_inventory
(
    user_id BIGINT                   NOT NULL
        CONSTRAINT user_inventory_users_fk
            REFERENCES users(id)
            ON UPDATE CASCADE ON DELETE CASCADE,
    item   INTEGER                   NOT NULL
        CONSTRAINT user_inventory_items_fk
            REFERENCES user_items(id)
            ON UPDATE CASCADE ON DELETE CASCADE,
    quantity smallint NOT NULL,
    CONSTRAINT pk_user_inventory PRIMARY KEY (user_id, item)
);

-- noinspection SqlResolve
CREATE TABLE IF NOT EXISTS gang_items
(
    id      SERIAL
        CONSTRAINT gang_items_pk
            PRIMARY KEY,
    name    VARCHAR(32)                   NOT NULL,
    benefit BENEFIT                       NOT NULL,
    description VARCHAR(100)   DEFAULT '' NOT NULL,
    value  SMALLINT                       NOT NULL
);

CREATE TABLE IF NOT EXISTS gang_inventory
(
    gang VARCHAR(32)                NOT NULL
        CONSTRAINT user_inventory_users_fk
            REFERENCES gangs(name)
            ON UPDATE CASCADE ON DELETE CASCADE,
    item   INTEGER                  NOT NULL
    CONSTRAINT gang_inventory_items_fk
            REFERENCES gang_items(id)
            ON UPDATE CASCADE ON DELETE CASCADE,
    quantity SMALLINT NOT NULL,
    CONSTRAINT pk_gang_inventory PRIMARY KEY (gang, item)
);
