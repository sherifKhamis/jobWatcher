import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

def scrape_jobs():
    """
    Diese Funktion lädt die BMW Job-Seite, parst den HTML-Inhalt und filtert Jobeinträge,
    die folgende Kriterien erfüllen:
      - Der Job gehört zur BMW AG.
      - Der Jobtyp enthält "Absolventen" oder "Berufserfahrene".
      - Das Jobfeld enthält mindestens einen der gewünschten Begriffe.
      - Der Standort ist "München".
    Die gefilterten Jobs werden in einer Liste als Dictionaries gespeichert und zurückgegeben.
    """
    url = "https://www.bmwgroup.jobs/de/de/_jcr_content/main/layoutcontainer/jobfinder30_copy.jobfinder_table.content.html"
    
    # Konfiguration der Chrome-Optionen (Headless-Modus: ohne GUI)
    chrome_options = Options()
    chrome_options.add_argument("--headless")      # Ohne grafische Benutzeroberfläche
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    
    # Erstellen des Chrome-Webdrivers mithilfe von webdriver-manager
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    # Aufrufen der Ziel-URL
    driver.get(url)
    
    try:
        # Warten, bis das Element mit der CSS-Klasse "grp-jobfinder__table" geladen ist (max. 30 Sekunden)
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CLASS_NAME, "grp-jobfinder__table"))
        )
    except Exception as e:
        print("Timeout oder Fehler beim Laden der Job-Elemente:", e)
    
    # Zusätzliche Wartezeit, falls Inhalte dynamisch nachgeladen werden
    time.sleep(3)
    
    # Abrufen des Seitenquelltexts und Schließen des Browsers
    html_content = driver.page_source
    driver.quit()
    
    # Parsen des HTML-Inhalts mit BeautifulSoup
    soup = BeautifulSoup(html_content, "html.parser")
    
    # Finden aller Jobeinträge basierend auf der CSS-Klasse "grp-jobfinder__wrapper"
    job_elements = soup.find_all("div", class_="grp-jobfinder__wrapper")
    if not job_elements:
        print("Keine Jobeinträge gefunden. Bitte die Struktur der Seite überprüfen.")
        return []
    
    jobs_list = []  # Liste zur Speicherung der Jobdaten
    
    # Durchlaufen der gefundenen Jobeinträge
    for job in job_elements:
        # Suchen des Div-Elements mit den Job-spezifischen Daten
        data_div = job.find("div", class_="grp-jobfinder-cell-refno")
        if not data_div:
            continue

        # Extrahieren der benötigten Daten aus den Data-Attributen
        company   = data_div.get("data-job-legal-entity", "")
        job_field = data_div.get("data-job-field", "")
        job_type  = data_div.get("data-job-type", "")
        location  = data_div.get("data-job-location", "")
        
        # Filter: Nur Jobs der BMW AG
        if "BMW AG" not in company:
            continue
        
        # Filter: Jobtyp muss "Absolventen" oder "Berufserfahrene" beinhalten
        if not ("Absolventen" in job_type or "Berufserfahrene" in job_type):
            continue
        
        # Filter: Jobfeld muss mindestens einen der gewünschten Begriffe enthalten
        valid_fields = [
            "Data Science",
            "IT",
            "Forschung & Entwicklung",
            "Softwareentwicklung",
            "Fahrerassistenzsysteme"
        ]
        if not any(field in job_field for field in valid_fields):
            continue
        
        # Filter: Nur Jobs in München
        if "München" not in location:
            continue

        # Extrahieren des Jobtitels
        title_div = job.find("div", class_="grp-jobfinder__cell-title")
        job_title = title_div.get_text(strip=True) if title_div else "Kein Titel gefunden"
        
        # Extrahieren des Links zur Jobbeschreibung (suchen innerhalb des aktuellen Job-Elements)
        link_element = job.find("a", class_="grp-popup-link-js grp-jobfinder__link-jobdescription")
        if link_element and link_element.get("href"):
            link = "https://www.bmwgroup.jobs" + link_element.get("href")
        else:
            link = "Kein Link gefunden"
        
        # Speichern der Jobdaten als Dictionary
        job_data = {
            "job_title": job_title,
            "company": company,
            "location": location,
            "link": link
        }
        jobs_list.append(job_data)
    
    return jobs_list
