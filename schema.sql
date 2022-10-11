CREATE TABLE IF NOT EXISTS users
(
    id          BIGINT             NOT NULL
        CONSTRAINT points_pk
            PRIMARY KEY,
    points      SMALLINT DEFAULT 0 NOT NULL,
    sudoku_time interval DEFAULT '1 day'::interval
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
    cooldown TIMESTAMP WITH TIME ZONE DEFAULT (CURRENT_TIMESTAMP + '7 days'::interval) NOT NULL,
    approved boolean                  DEFAULT FALSE                                    NOT NULL
);
