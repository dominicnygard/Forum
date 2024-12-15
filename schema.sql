CREATE TABLE Users
(
    id          SERIAL PRIMARY KEY,
    username    TEXT UNIQUE,
    password    TEXT
);

CREATE TABLE Posts
(
    id          SERIAL PRIMARY KEY,
    user_id     INTEGER REFERENCES Users(id),
    title       TEXT,
    content     TEXT,
    sent_at     TIMESTAMP
);

CREATE TABLE Comments
(
    id          SERIAL PRIMARY KEY,
    post_id     INTEGER REFERENCES Posts(id) ON DELETE CASCADE,
    user_id     INTEGER REFERENCES Users(id),
    content     TEXT,
    sent_at     TIMESTAMP
);

CREATE TABLE chats
(
    id              SERIAL PRIMARY KEY,
    room_id         TEXT UNIQUE
);

Create TABLE Messages
(
    id              SERIAL PRIMARY KEY,
    chat_id         INTEGER REFERENCES chats(id) ON DELETE CASCADE,
    sender_id       INTEGER REFERENCES Users(id),
    content         TEXT,
    sent_at         TIMESTAMP
);


CREATE TABLE chatParticipants (
    chat_id         INTEGER REFERENCES chats(id),
    user_id         INTEGER REFERENCES users(id),
    PRIMARY KEY (chat_id, user_id)
);

CREATE TABLE Permissions
(
    id              SERIAL PRIMARY KEY,
    permission_name TEXT UNIQUE
);

CREATE TABLE UserPermissions
(
    room_id INTEGER REFERENCES chats(id),
    user_id INTEGER REFERENCES Users(id),
    permission_id INTEGER REFERENCES Permissions(id),
    PRIMARY KEY (room_id, user_id, permission_id)
);

CREATE TABLE PublicPermissions
(
    user_id INTEGER REFERENCES Users(id),
    permission_id INTEGER REFERENCES Permissions(id),
    PRIMARY KEY (user_id, permission_id)
);

INSERT INTO Permissions (permission_name) VALUES ('view'), ('send'), ('post'), ('comment'), ('delete'), ('admin')