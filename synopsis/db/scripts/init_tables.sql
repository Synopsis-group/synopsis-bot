CREATE TABLE if not exists users (
	user_id INTEGER PRIMARY KEY,
	parent_id INTEGER,
    user_role INTEGER NOT NULL,
    city TEXT
);

CREATE TABLE if not exists events (
	event_id TEXT PRIMARY KEY,
    event_status INTEGER,
	author_id INTEGER NOT NULL,
	creation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    editor_id INTEGER,
    changed_date TIMESTAMP,

    title TEXT NOT NULL,
    event_type INTEGER NOT NULL,
    start_time INTEGER NOT NULL,
    event_date INTEGER NOT NULL,
    duration INTEGER NOT NULL,
    organization TEXT NOT NULL
);
