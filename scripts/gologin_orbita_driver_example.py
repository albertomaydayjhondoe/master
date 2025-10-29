"""
Ejemplo de uso de OrbitaDriver (GoLogin) en Selenium.
Asegúrate de que drivers/orbita/orbitadriver.exe existe (descargado por CI/CD o manualmente).
"""
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import os

def get_orbita_driver():
    driver_path = os.path.abspath("drivers/orbita/orbitadriver.exe")
    options = Options()
    # Configura aquí tus opciones GoLogin/Orbita
    # Por ejemplo: options.add_argument(f"--user-data-dir=...gologin_profile_path...")
    # ...otros flags...
    service = Service(executable_path=driver_path)
    driver = webdriver.Chrome(service=service, options=options)
    return driver

if __name__ == "__main__":
    driver = get_orbita_driver()
    driver.get("https://www.google.com")
    print("Navegador Orbita lanzado correctamente.")
    driver.quit()
