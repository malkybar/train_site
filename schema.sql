DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS saves;

CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL,
    password TEXT NOT NULL
);

CREATE TABLE saves (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    crs_1 TEXT NOT NULL,
    station_1 TEXT NOT NULL,
    crs_2 TEXT NOT NULL,
    station_2 TEXT NOT NULL,
    dep_arr TEXT NOT NULL,
    user_id INTEGER,
    FOREIGN KEY(user_id) REFERENCES users(id),
    UNIQUE (crs_1, station_1, crs_2, station_2, dep_arr, user_id)
);