import sqlite3

def init_db():
    """
    Initialisiert die Datenbank, indem sie die vorhandene "jobs"-Tabelle löscht (falls vorhanden)
    und eine neue Tabelle erstellt.
    """
    conn = sqlite3.connect("jobs.db")
    cursor = conn.cursor()
    
    # Sicherstellen, dass die Tabelle existiert, bevor sie gelöscht wird
    cursor.execute("DROP TABLE IF EXISTS jobs;")
    
    # Neue Tabelle erstellen
    cursor.execute("""
        CREATE TABLE jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            company TEXT NOT NULL,
            location TEXT,
            link TEXT
        )
    """)
    
    conn.commit()
    conn.close()

def save_to_db(jobs):
    """
    Speichert eine Liste von Jobs in die Datenbank.
    Jeder Job muss ein Dictionary mit den Schlüsseln 'job_title', 'company', 'location' und 'link' sein.
    """
    conn = sqlite3.connect("jobs.db")
    cursor = conn.cursor()
    
    # Jobs in die Datenbank einfügen
    cursor.executemany(
        "INSERT INTO jobs (title, company, location, link) VALUES (:job_title, :company, :location, :link)",
        jobs
    )
    
    conn.commit()
    conn.close()
