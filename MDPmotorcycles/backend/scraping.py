from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from sqlalchemy.orm import Session
from backend import models
from backend.database import SessionLocal
import time
import traceback
import os
import re

URL_MOTOS = "https://dismerca.com/motos/"

def clean_text(text):
    return re.sub(r'\s+', ' ', text).strip()

def scrape_and_store_motos(headless=True):
    options = Options()
    options.headless = headless
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    try:
        driver.get(URL_MOTOS)
        try:
            WebDriverWait(driver, 20).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a.text-decoration-none"))
            )
        except Exception as wait_exc:
            timestamp = int(time.time())
            filename = f"debug_page_source_{timestamp}.html"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(driver.page_source)
            print(f"Timeout waiting for moto cards. Page source saved to {filename}")
            raise wait_exc

        moto_links = driver.find_elements(By.CSS_SELECTOR, "a.text-decoration-none")
        print(f"Found {len(moto_links)} moto elements on the page.")

        db: Session = SessionLocal()
        count = 0

        for moto_link in moto_links:
            try:
                nombre = None
                try:
                    nombre_el = moto_link.find_element(By.CSS_SELECTOR, ".card-product .card-body .row .col h3")
                    nombre = clean_text(nombre_el.text)
                except:
                    href = moto_link.get_attribute("href")
                    nombre = href.split("/")[-2].replace("-", " ").title()
                if not nombre:
                    nombre = "No Name"
            except:
                nombre = "No Name"

            try:
                marca = None
                try:
                    marca_el = moto_link.find_element(By.CSS_SELECTOR, ".card-product .card-body .row .col p")
                    marca = clean_text(marca_el.text)
                except:
                    marca = nombre.split()[0] if nombre else "Unknown"
                if not marca:
                    marca = "Unknown"
            except:
                marca = "Unknown"

            try:
                precio_text = ""
                price_elements = moto_link.find_elements(By.CSS_SELECTOR, "div, span, p")
                for elem in price_elements:
                    text = elem.text.strip()
                    if "$" in text:
                        precio_text = text
                        break
                precio = 0.0
                if precio_text:
                    precio_clean = precio_text.replace("$", "").replace(",", "").strip()
                    precio = float(precio_clean) if precio_clean.replace('.', '', 1).isdigit() else 0.0
            except:
                precio = 0.0

            try:
                img_url = moto_link.find_element(By.TAG_NAME, "img").get_attribute("src")
            except:
                img_url = None

            nombre_norm = nombre.lower().strip()
            marca_norm = marca.lower().strip()

            existing = db.query(models.Moto).filter(
                models.Moto.nombre.ilike(nombre_norm),
                models.Moto.marca.ilike(marca_norm)
            ).first()
            if existing:
                continue

            new_moto = models.Moto(
                nombre=nombre,
                marca=marca,
                precio=precio,
                img_url=img_url
            )
            db.add(new_moto)
            count += 1

        db.commit()
        db.close()
        print(f"Stored {count} new motos in the database.")
    except Exception as e:
        print(f"Error during scraping: {e}")
        traceback.print_exc()
    finally:
        try:
            driver.quit()
        except Exception:
            pass

if __name__ == "__main__":
    scrape_and_store_motos(headless=False)
