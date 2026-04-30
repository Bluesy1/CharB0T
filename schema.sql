-- cspell: ignore particip

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


CREATE TABLE IF NOT EXISTS giveaway
(
    channel     BIGINT                          NOT NULL
        CONSTRAINT giveaway_pk
            PRIMARY KEY,
    end_dt      TIMESTAMP WITH TIME ZONE        NOT NULL,
    winners     SMALLINT CHECK(winners > 0)     NOT NULL,
    game        VARCHAR(255)                    NOT NULL,
    distributor BIGINT                          NOT NULL,
    complete    BOOLEAN     DEFAULT FALSE       NOT NULL,
    min_level   SMALLINT    DEFAULT 0           NOT NULL,
    random_num  BOOLEAN     DEFAULT FALSE       NOT NULL
);

CREATE TABLE IF NOT EXISTS xcom_character_request
(
    requestor       BIGINT                          NOT NULL
        CONSTRAINT xcom_character_request_pk
            PRIMARY KEY,
    req_dt          TIMESTAMP WITH TIME ZONE        NOT NULL
                                DEFAULT CURRENT_TIMESTAMP   ,
    first_name      VARCHAR(25)                     NOT NULL,
    last_name       VARCHAR(25)                     NOT NULL,
    nickname        VARCHAR(25)                     NOT NULL,
    country         VARCHAR(50)                     NOT NULL,
    gender          VARCHAR(6)                      NOT NULL
        CHECK(gender IN ('male', 'female'))                 ,
    race            VARCHAR(9)                      NOT NULL
        CHECK(race IN ('Caucasian', 'African', 'Asian', 'Hispanic')),
    details         VARCHAR(500)                    NOT NULL,
    biography       VARCHAR(2000)                   NOT NULL,
    fulfiller       BIGINT      DEFAULT NULL                ,
    fulfill_thread  BIGINT      DEFAULT NULL
);

CREATE TABLE IF NOT EXISTS xcom_character_submission
(
    submitter   BIGINT                           NOT NULL
        CONSTRAINT xcom_character_submission_pk
            PRIMARY KEY,
    message_id      BIGINT                       NOT NULL,
    preferred_class VARCHAR(13)                  NOT NULL
);
