from db import *
from prefered_companies import bmw, sap

def main():
    init_db()
    jobs = bmw.scrape_jobs() + sap.scrape_jobs()

    if jobs:
        save_to_db(jobs)
        print(f"{len(jobs)} Jobs gespeichert.")
    else: 
        print("Keine Jobs gefunden")
main()

