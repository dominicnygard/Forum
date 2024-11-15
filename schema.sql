CREATE TABLE Users
(
    id          SERIAL PRIMARY KEY,
    username    TEXT UNIQUE,
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

Create TABLE messages
(
    id              SERIAL PRIMARY KEY,
    chat_id         INTEGER REFERENCES chats(id),
    sender_id       INTEGER REFERENCES Users(id),
    receiver_id     INTEGER REFERENCES Users(id),
    content         TEXT,
    sent_at         DATE
)

CREATE TABLE chats
(
    id              SERIAL PRIMARY KEY,
    room_id         TEXT UNIQUE
)

CREATE TABLE Permissions
(
    id              SERIAL PRIMARY KEY,
    permission_name UNIQUE TEXT
)

CREATE TABLE UserPermissions
(
    room_id INTEGER REFERENCES chats(id),
    user_id INTEGER REFERENCES Users(id),
    permission_id INTEGER REFERENCES Permisions(id),
    PRIMARY KEY (room_id, user_id, permission_id)
)