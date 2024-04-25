import sqlite3
import bcrypt

connection = sqlite3.connect('capstone_database.db')

cursor = connection.cursor()


salt = bcrypt.gensalt()
hashed_password = bcrypt.hashpw("password".encode("utf-8"), salt)

cursor.execute('''
    CREATE TABLE IF NOT EXISTS Users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        phone TEXT,
        email TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL UNIQUE,
        active INTEGER NOT NULL DEFAULT 1,
        date_created TEXT,
        hire_date TEXT,
        user_type TEXT NOT NULL DEFAULT 'user'
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS Competencies (
        competency_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        date_created TEXT
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS Assessments (
        assessment_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        date_created TEXT,
        competency_id INTEGER NOT NULL,
        FOREIGN KEY (competency_id) REFERENCES Competencies(competency_id)
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS Assessment_Results (
        result_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        assessment_id INTEGER NOT NULL,
        score INTEGER NOT NULL,
        date_taken TEXT,
        manager_id INTEGER NOT NULL,
        FOREIGN KEY (user_id) REFERENCES Users(user_id),
        FOREIGN KEY (assessment_id) REFERENCES Assessments(assessment_id),
        FOREIGN KEY (manager_id) REFERENCES Users(user_id)
    )
''')

users_data = [
    (1, 'John', 'Doe', '123-456-7890', 'john@example.com', hashed_password, 1, '2024-01-01', '2022-01-01', 'user'),
    (2, 'Jane', 'Smith', '987-654-3210', 'jane@example.com', hashed_password, 1, '2024-01-02', '2022-01-02', 'manager'),
    (3, 'Alice', 'Johnson', '456-789-0123', 'alice@example.com', hashed_password, 1, '2024-01-03', '2022-01-03', 'user')
]

competencies_data = [
    (1, 'Computer Anatomy', '2024-01-01'),
    (2, 'Data Types', '2024-01-02'),
    (3, 'Variables', '2024-01-03'),
    (4, 'Functions', '2024-01-04'),
    (5, 'Boolean Logic', '2024-01-05'),
    (6, 'Conditionals', '2024-01-06'),
    (7, 'Loops', '2024-01-07'),
    (8, 'Data Structures', '2024-01-08'),
    (9, 'Lists', '2024-01-09'),
    (10, 'Dictionaries', '2024-01-10'),
    (11, 'Working with Files', '2024-01-11'),
    (12, 'Exception Handling', '2024-01-12'),
    (13, 'Quality Assurance (QA)', '2024-01-13'),
    (14, 'Object-Oriented Programming', '2024-01-14'),
    (15, 'Recursion', '2024-01-15'),
    (16, 'Databases', '2024-01-16')
]

assessments_data = [
    (1, 'Computer Anatomy Test', '2024-01-01', 1),
    (2, 'Data Types Test', '2024-01-02', 2),
    (3, 'Variables Test', '2024-01-03', 3)
]

assessment_results_data = [
    (1, 1, 1, 3, '2024-01-05', 2),
    (2, 2, 2, 4, '2024-01-06', 2),
    (3, 3, 3, 2, '2024-01-07', 2)
]

cursor.executemany('''
    INSERT INTO Users (user_id, first_name, last_name, phone, email, password_hash, active, date_created, hire_date, user_type)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
''', users_data)

cursor.executemany('''
    INSERT INTO Competencies (competency_id, name, date_created)
    VALUES (?, ?, ?)
''', competencies_data)

cursor.executemany('''
    INSERT INTO Assessments (assessment_id, name, date_created, competency_id)
    VALUES (?, ?, ?, ?)
''', assessments_data)

cursor.executemany('''
    INSERT INTO Assessment_Results (result_id, user_id, assessment_id, score, date_taken, manager_id)
    VALUES (?, ?, ?, ?, ?, ?)
''', assessment_results_data)

connection.commit()