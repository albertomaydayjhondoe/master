from gologin import GoLogin
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import os

GOLOGIN_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2OTAxMjc4Y2NhYjg0MDdlNWFmZDRjZDkiLCJ0eXBlIjoiZGV2Iiwiand0aWQiOiI2OTAxZTgzYWNhYjg0MDdlNWFhYWM3MTMifQ.lip9owB1TtzlMRiXe3tWQ39YAnenIBW7-UXAGPVLuTY"
PROFILE_ID = "TU_PROFILE_ID"  # Reemplaza por tu ID de perfil GoLogin
N8N_URL = "http://localhost:5678"  # Cambia si tu instancia es remota
WORKFLOW_PATH = os.path.abspath("orchestration/n8n_workflows/meta_ads_auto_campaign.json")

gl = GoLogin({
    "token": GOLOGIN_TOKEN,
    "profile_id": PROFILE_ID
})

debugger_address = gl.start()
chrome_options = webdriver.ChromeOptions()
chrome_options.add_experimental_option("debuggerAddress", debugger_address)
driver = webdriver.Chrome(options=chrome_options)

try:
    driver.get(N8N_URL)
    time.sleep(5)

    import_btn = driver.find_element(By.XPATH, "//button[contains(., 'Import')]")
    import_btn.click()
    time.sleep(2)

    file_input = driver.find_element(By.XPATH, "//input[@type='file']")
    file_input.send_keys(WORKFLOW_PATH)
    time.sleep(2)

    confirm_btn = driver.find_element(By.XPATH, "//button[contains(., 'Import')]")
    confirm_btn.click()
    time.sleep(3)

    print("Workflow importado correctamente.")
finally:
    driver.quit()
    gl.stop()
