from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
import time

def scrape_jobs():
    """
    Diese Funktion durchsucht die SAP-Jobseite nach Stellenangeboten basierend auf 
    vorgegebenen Filterkriterien (Abteilung, Karrierestatus, Land). 
    Stellenangebote in Ostdeutschland (hier exemplarisch: Dresden) werden ausgeschlossen.
    """
    # Konfiguration der Chrome-Optionen (Headless-Modus auskommentiert, falls benötigt)
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Aktiviert den Headless-Modus (ohne GUI)

    # Initialisiere den WebDriver
    driver = webdriver.Chrome(options=chrome_options)

    # URL der SAP-Jobseite
    url = "https://jobs.sap.com/search/?createNewAlert=false&q=&locationsearch=&optionsFacetsDD_department=&optionsFacetsDD_customfield3=&optionsFacetsDD_country=&locale=de_DE"

    # Filterparameter definieren
    departments = [
        "Information Technology", 
        "Software-Design und Entwicklung", 
        "Software-Development Operations", 
        "Software-User Experience", 
        "Solution und Produkt Management"
    ]
    career_status = ["Absolventen", "Berufserfahren"]
    country = "Deutschland"

    jobs = []

    # Öffne die Jobseite
    driver.get(url)

    # Cookie-Akzeptieren-/Ablehnen-Button finden und klicken (hier wird 'Alle ablehnen' genutzt)
    try:
        cookie_button = WebDriverWait(driver, 10).until(
            lambda d: d.find_element(By.XPATH, "//button[contains(text(), 'Alle ablehnen')]")
        )
        driver.execute_script("arguments[0].click();", cookie_button)
    except Exception as e:
        jobs = []
        return jobs

    # Iteriere über alle Kombinationen von Abteilungen und Karrierestatus
    for department in departments:
        for status in career_status:
            # Warte, bis die Seite vollständig geladen ist
            WebDriverWait(driver, 10).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            # Kurze Pause, um sicherzustellen, dass die Dropdowns bereit sind
            time.sleep(15)

            # Wähle im Dropdown für Abteilungen den aktuellen Filterwert aus
            try:
                department_dropdown = Select(driver.find_element(By.ID, "optionsFacetsDD_department"))
                department_dropdown.select_by_visible_text(department)
            except Exception as e:
                jobs = []
                return jobs

            # Wähle im Dropdown für Karrierestatus den aktuellen Filterwert aus
            try:
                career_dropdown = Select(driver.find_element(By.ID, "optionsFacetsDD_customfield3"))
                career_dropdown.select_by_visible_text(status)
            except Exception as e:
                jobs = []
                return jobs

            # Wähle im Dropdown für Land/Region den Filterwert "Deutschland" aus
            try:
                country_dropdown = Select(driver.find_element(By.ID, "optionsFacetsDD_country"))
                country_dropdown.select_by_visible_text(country)
            except Exception as e:
                jobs = []
                return jobs

            # Klicke auf den "Suche starten"-Button, um die Filter anzuwenden
            try:
                search_button = driver.find_element(By.XPATH, "//input[@type='submit' and @value='Suche starten']")
                search_button.click()
            except Exception as e:
                jobs = []
                return jobs

            time.sleep(2)  # Kurze zusätzliche Wartezeit, falls nötig

            # Sammle alle Job-Einträge
            job_elements = driver.find_elements(By.CSS_SELECTOR, ".data-row")
            for job in job_elements:
                try:
                    # Extrahiere den Jobtitel
                    title = job.find_element(By.CSS_SELECTOR, ".jobTitle-link").text
                    # Extrahiere die Standortangaben
                    location_elements = job.find_elements(By.CSS_SELECTOR, "span.jobLocation")
                    location_text = next((el.text.strip() for el in location_elements if el.text.strip()), "")
                    # Extrahiere den Link und füge die Basis-URL hinzu
                    link = "https://jobs.sap.com" + job.find_element(By.TAG_NAME, "a").get_attribute("href")
                    
                    # Überspringe den Job, wenn er in Ostdeutschland (z. B. Dresden) liegt
                    ostdeutschland = any("Dresden" in loc.text for loc in location_elements)
                    if ostdeutschland:
                        continue

                    # Füge den Job der Ergebnisliste hinzu
                    jobs.append({
                        "job_title": title,
                        "company": "SAP SE",
                        "location": location_text,
                        "link": link
                    })
                except Exception as e:
                    jobs = []
                    return jobs

    # Schließe den WebDriver
    driver.quit()
    return jobs
