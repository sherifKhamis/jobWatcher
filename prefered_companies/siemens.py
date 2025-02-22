from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
from selenium.webdriver.common.keys import Keys

def scrape_jobs():
    # Start Selenium WebDriver
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Falls kein sichtbarer Browser benötigt wird
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    # Siemens Job-Seite öffnen
    driver.get("https://jobs.siemens.com/careers?location=any&pid=563156123593441&domain=siemens.com&sort_by=relevance&triggerGoButton=false&triggerGoButton=true")
    
    try:
        # Warte auf das erste Shadow DOM - "usercentrics-root"
        shadow_host = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "usercentrics-root"))
        )
        shadow_root = driver.execute_script("return arguments[0].shadowRoot", shadow_host)
        
        # Cookie-Button finden und klicken
        cookie_button = shadow_root.find_element(By.CSS_SELECTOR, "button[data-testid='uc-deny-all-button']")
        driver.execute_script("arguments[0].click();", cookie_button)
    except Exception:
        pass  # Falls das Cookie-Banner nicht erscheint, einfach fortfahren
    
    # Warten und Filteroptionen öffnen
    filter_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "div.advanced-options-button"))
    )
    filter_button.click()
    
    # Erfahrungsebene auswählen
    experience_levels = [
        "div[data-test-id='advanced-options-pill-Experience-Level-early-professional']", 
        "//div[contains(@data-test-id, 'advanced-options-pill-Experience-Level-recent-college-graduate')]",
        "//div[contains(@data-test-id, 'advanced-options-pill-Experience-Level-mid-level-professional')]",
        "//div[contains(@data-test-id, 'advanced-options-pill-Experience-Level-mid-level-professional')]"
    ]
    
    for level in experience_levels:
        try:
            button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, level)) if "//" in level else EC.element_to_be_clickable((By.CSS_SELECTOR, level))
            )
            button.click()
            time.sleep(3)
        except Exception:
            jobs = []
            return jobs
        
    
    # Job-Familien auswählen
    job_families = [
        "div[data-test-id='advanced-options-pill-Job-Family-Cybersecurity']",
        "//div[contains(@data-test-id, 'Job-Family-Information-Technology')]",
        "//div[contains(@data-test-id, 'advanced-options-pill-Job-Family-Engineering')]",
        "div[data-test-id='advanced-options-pill-Job-Family-Research-&-Development']"
    ]
    
    for job in job_families:
        try:
            element = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, job)) if "//" in job else EC.element_to_be_clickable((By.CSS_SELECTOR, job))
            )
            element.click()
            time.sleep(3)
        except Exception:
            jobs = []
            return jobs
    
    # Suchfeld für Unternehmen eingeben
    search_box = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "main-search-box"))
    )
    search_box.clear()
    search_box.send_keys("Siemens AG, Siemens Mobility")
    search_box.send_keys(Keys.RETURN)
    
    # Standort setzen
    location_box = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "location-search-box"))
    )
    location_box.clear()
    location_box.send_keys("Germany")
    location_box.send_keys(Keys.RETURN)
    
    # Job-Daten abrufen
    job_list = []
    fully_loaded = False
    
    while not fully_loaded:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.job-card-container"))
        )
        driver.execute_script("window.scrollBy(window.innerWidth * 0.3, 10000);")
        time.sleep(2)
        driver.execute_script("window.scrollBy(window.innerWidth * 0.6, 10000);")
        time.sleep(2)
        driver.execute_script("window.scrollBy(window.innerWidth * 0.3, 10000);")
        time.sleep(2)
        fully_loaded = bool(driver.find_elements(By.CSS_SELECTOR, ".all-positions-loaded-div"))
        
        if not fully_loaded:
            try:
                iframe_button = driver.find_element(By.CSS_SELECTOR, ".show-more-positions")
                iframe_button.click()
            except Exception:
                break
    
    # Alle Job-Karten abrufen
    job_cards = driver.find_elements(By.CSS_SELECTOR, "div.job-card-container")
    
    for job in job_cards:
        try:
            title_element = job.find_element(By.CSS_SELECTOR, "h3.job-card-title")
            job_title = title_element.text.strip()
            
            location_element = job.find_element(By.CSS_SELECTOR, "p.field-label")
            job_location = location_element.text.strip()
            
            # Jobs in Sachsen ignorieren
            if "Sachsen" in job_location:
                continue
            
            job_list.append({
                "job_title": job_title,
                "company": "Siemens AG",
                "location": job_location,
                "link": "https://jobs.siemens.com/careers"
            })
        except Exception:
            jobs = []
            return jobs
    
    driver.quit()
    return job_list
