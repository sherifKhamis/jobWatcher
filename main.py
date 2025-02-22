from db import init_db, save_to_db  # Import der Datenbank-Funktionen
from prefered_companies import bmw, sap, siemens  # Import der bevorzugten Unternehmen

def scrape_jobs_with_retry(company):
    """
    Versucht wiederholt, Jobs von einer Unternehmensquelle zu scrapen,
    bis mindestens ein Job gefunden wird.
    """
    jobs = []
    while not jobs:
        jobs = company.scrape_jobs()
    return jobs

def main():
    """
    Hauptfunktion zum Initialisieren der Datenbank, Scrapen der Jobs und Speichern in die Datenbank.
    """
    init_db()  # Initialisiert die Datenbank
    
    # Jobs von den bevorzugten Unternehmen abrufen
    bmw_jobs = scrape_jobs_with_retry(bmw)
    sap_jobs = scrape_jobs_with_retry(sap)
    siemens_jobs = scrape_jobs_with_retry(siemens)
    
    # Alle gescrapten Jobs zusammenführen
    jobs = bmw_jobs + sap_jobs + siemens_jobs
    
    # Falls Jobs gefunden wurden, speichere sie in der Datenbank
    if jobs:
        save_to_db(jobs)
        print(f"{len(jobs)} Jobs gespeichert.")
    else:
        print("Keine Jobs gefunden.")

if __name__ == "__main__":
    main()
