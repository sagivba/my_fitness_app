CREATE TABLE IF NOT EXISTS daily_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    log_date TEXT NOT NULL UNIQUE,
    body_weight_kg REAL,
    mood TEXT,
    energy_level INTEGER,
    notes TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS workout (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workout_date TEXT NOT NULL,
    workout_type TEXT NOT NULL,
    duration_minutes INTEGER,
    source TEXT NOT NULL DEFAULT 'manual',
    start_time TEXT,
    end_time TEXT,
    duration_seconds REAL,
    distance_meters REAL,
    calories INTEGER,
    average_heart_rate INTEGER,
    max_heart_rate INTEGER,
    elevation_gain_meters REAL,
    elevation_loss_meters REAL,
    external_activity_id TEXT,
    notes TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS strength_exercise (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workout_id INTEGER NOT NULL,
    exercise_name TEXT NOT NULL,
    exercise_order INTEGER NOT NULL,
    notes TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (workout_id) REFERENCES workout(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS strength_set (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    strength_exercise_id INTEGER NOT NULL,
    set_number INTEGER NOT NULL,
    reps INTEGER NOT NULL,
    weight_kg REAL,
    perceived_effort INTEGER,
    notes TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (strength_exercise_id) REFERENCES strength_exercise(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS sleep_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sleep_date TEXT NOT NULL UNIQUE,
    start_time TEXT,
    end_time TEXT,
    duration_minutes INTEGER,
    sleep_quality INTEGER,
    notes TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS meal (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    meal_date TEXT NOT NULL,
    meal_type TEXT NOT NULL,
    description TEXT NOT NULL,
    calories INTEGER,
    protein_grams REAL,
    carbs_grams REAL,
    fat_grams REAL,
    fiber_grams REAL,
    source TEXT NOT NULL DEFAULT 'manual',
    notes TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS imported_file (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    original_filename TEXT NOT NULL,
    stored_path TEXT NOT NULL,
    file_hash TEXT NOT NULL UNIQUE,
    file_type TEXT NOT NULL,
    import_status TEXT NOT NULL DEFAULT 'not_imported',
    import_error_message TEXT,
    imported_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
