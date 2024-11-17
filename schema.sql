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
    sent_at     TIMESTAMP
)

CREATE TABLE Comments
(
    id          SERIAL PRIMARY KEY,
    post_id     INTEGER REFERENCES Posts(id),
    user_id     INTEGER REFERENCES Users(id),
    content     TEXT,
    sent_at     TIMESTAMP
)

Create TABLE Messages
(
    id              SERIAL PRIMARY KEY,
    chat_id         INTEGER REFERENCES chats(id),
    sender_id       INTEGER REFERENCES Users(id),
    content         TEXT,
    sent_at         TIMESTAMP
)

CREATE TABLE chats
(
    id              SERIAL PRIMARY KEY,
    room_id         TEXT UNIQUE
)

CREATE TABLE chatParticipants (
    chat_id         INTEGER REFERENCES chats(id),
    user_id         INTEGER REFERENCES users(id),
    PRIMARY KEY (chat_id, user_id)
)

CREATE TABLE Permissions
(
    id              SERIAL PRIMARY KEY,
    permission_name TEXT UNIQUE
)

CREATE TABLE ChatPermissions
(
    chat_id INTEGER REFERENCES chats(id),
    user_id INTEGER REFERENCES Users(id),
    permission_id INTEGER REFERENCES Permissions(id),
    PRIMARY KEY (room_id, user_id, permission_id)
)

CREATE TABLE PublicPermissions
(
    user_id INTEGER REFERENCES Users(id),
    permission_id INTEGER REFERENCES Permissions(id),
    PRIMARY KEY (user_id, permission_id)
)