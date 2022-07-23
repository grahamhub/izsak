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
