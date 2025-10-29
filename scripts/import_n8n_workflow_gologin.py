
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import os
import sys
import random
import socket

N8N_URL = "http://localhost:5678"  # Cambia si tu instancia es remota
WORKFLOW_PATH = os.path.abspath("orchestration/n8n_workflows/meta_ads_auto_campaign.json")

# Permitir especificar el puerto por variable de entorno o argumento, si no, elegir aleatorio libre
def get_free_port():
    for _ in range(20):
        port = random.randint(9000, 9999)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(("127.0.0.1", port)) != 0:
                return port
    return 9222

port = 9222
if len(sys.argv) > 1:
    try:
        port = int(sys.argv[1])
    except Exception:
        print("[WARN] Argumento de puerto inválido, usando 9222")
elif os.getenv("CHROME_DEBUG_PORT"):
    try:
        port = int(os.getenv("CHROME_DEBUG_PORT"))
    except Exception:
        print("[WARN] Variable de entorno CHROME_DEBUG_PORT inválida, usando 9222")
else:
    port = get_free_port()

print(f"[INFO] Conectando a Chrome/Orbita ya abierto en modo depuración (puerto {port})...")
chrome_options = webdriver.ChromeOptions()
chrome_options.add_experimental_option("debuggerAddress", f"127.0.0.1:{port}")
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
    # No cerramos el navegador, solo liberamos el driver
    driver.quit()
