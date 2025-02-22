import sqlite3

# Datenbank initialisieren
def init_db():
    conn = sqlite3.connect("jobs.db")
    cursor = conn.cursor()
    cursor.execute("""    DROP TABLE jobs;    """)
    cursor.execute("""       
        CREATE TABLE jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            company TEXT,
            location TEXT,
            link TEXT
        )
    """)
    conn.commit()
    conn.close()

# Jobs in die Datenbank speichern
def save_to_db(jobs):
    conn = sqlite3.connect("jobs.db")
    cursor = conn.cursor()
    cursor.executemany("INSERT INTO jobs (title, company, location, link) VALUES (:job_title, :company, :location, :link)", jobs)
    conn.commit()
    conn.close()