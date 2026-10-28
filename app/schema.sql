CREATE TABLE IF NOT EXISTS users (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    username      TEXT NOT NULL UNIQUE COLLATE NOCASE,
    password_hash TEXT NOT NULL,
    role          TEXT NOT NULL CHECK (role IN ('RECEPTIONIST', 'DOCTOR', 'ADMIN')),
    active        INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS patients (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name     TEXT NOT NULL,
    date_of_birth TEXT NOT NULL,
    gender        TEXT NOT NULL,
    phone         TEXT NOT NULL,
    address       TEXT NOT NULL DEFAULT '',
    active        INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS appointments (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER NOT NULL REFERENCES patients(id),
    doctor_id  INTEGER NOT NULL REFERENCES users(id),
    start_time TEXT NOT NULL,
    status     TEXT NOT NULL DEFAULT 'Scheduled'
        CHECK (status IN ('Scheduled', 'Cancelled', 'Completed'))
);

-- Database-level safety net: a doctor can never have two SCHEDULED
-- appointments at the same time, even if two requests race each other.
CREATE UNIQUE INDEX IF NOT EXISTS ux_doctor_slot
    ON appointments (doctor_id, start_time) WHERE status = 'Scheduled';

CREATE TABLE IF NOT EXISTS medical_records (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id   INTEGER NOT NULL REFERENCES patients(id),
    doctor_id    INTEGER NOT NULL REFERENCES users(id),
    created_at   TEXT NOT NULL,
    diagnosis    TEXT NOT NULL,
    treatment    TEXT NOT NULL DEFAULT '',
    prescription TEXT NOT NULL DEFAULT ''
);
