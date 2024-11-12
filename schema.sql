CREATE TABLE Users
(
    id          SERIAL PRIMARY KEY,
    username    TEXT,
    password    TEXT
)

CREATE TABLE Posts
(
    id          SERIAL PRIMARY KEY,
    user_id     INTEGER REFERENCES Users(id),
    title       TEXT,
    content     TEXT,
    sent_at     DATE
)

CREATE TABLE Comments
(
    id          SERIAL PRIMARY KEY,
    post_id     INTEGER REFERENCES Posts(id),
    user_id     INTEGER REFERENCES Users(id),
    content     TEXT,
    sent_at     DATE
)

Create TABLE PrivateMessages
(
    id          SERIAL PRIMARY KEY,
    sender_id   INTEGER REFERENCES Users(id),
    receiver_id INTEGER REFERENCES Users(id),
    content     TEXT,
    sent_at     DATE
)