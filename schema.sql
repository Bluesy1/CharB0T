CREATE TABLE IF NOT EXISTS users
(
    id               BIGINT                   NOT NULL
        CONSTRAINT points_pk PRIMARY KEY              ,
    points           SMALLINT DEFAULT 0       NOT NULL,
    last_claim       TIMESTAMP WITH TIME ZONE NOT NULL
                        DEFAULT CURRENT_TIMESTAMP     ,
    last_particip_dt TIMESTAMP WITH TIME ZONE NOT NULL
                        DEFAULT CURRENT_TIMESTAMP     ,
    particip         SMALLINT DEFAULT 0       NOT NULL,
    won              SMALLINT DEFAULT 0       NOT NULL,
    wins             SMALLINT DEFAULT 0
);

CREATE TABLE IF NOT EXISTS levels
(
    id            BIGINT             NOT NULL
        CONSTRAINT levels_pk PRIMARY KEY,
    xp            BIGINT    DEFAULT 0 NOT NULL,
    last_message  TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS no_xp
(
    guild    BIGINT                          NOT NULL
        CONSTRAINT no_xp_pk
            PRIMARY KEY,
    channels BIGINT[] DEFAULT '{}'::BIGINT[] NOT NULL,
    roles    BIGINT[] DEFAULT '{}'::BIGINT[] NOT NULL
);

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
