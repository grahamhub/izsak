CREATE TABLE IF NOT EXISTS media (
    id              SERIAL PRIMARY KEY,
    url             TEXT,
    author          TEXT,
    category        VARCHAR(30),
    nsfw            BOOLEAN,
    has_been_sent   BOOLEAN DEFAULT False,
    submitted_by    VARCHAR(100),
    submitted_on    TIMESTAMP DEFAULT current_timestamp
);

CREATE TABLE IF NOT EXISTS mediaV2 (
    id              SERIAL PRIMARY KEY,
    url             TEXT,
    author          TEXT,
    category        VARCHAR(30)[],
    nsfw            BOOLEAN,
    has_been_sent   BOOLEAN DEFAULT False,
    submitted_by    VARCHAR(100),
    submitted_on    TIMESTAMP DEFAULT current_timestamp
);

CREATE TABLE IF NOT EXISTS category (
    id              SERIAL PRIMARY KEY,
    name            VARCHAR(30),
    created_by      VARCHAR(100),
    created_on      TIMESTAMP DEFAULT current_timestamp
);
