import os
import shutil
import sys
import subprocess
from pathlib import Path

PROFILE_ID = "69024236bf3f011ec1593d23"
TEMP_PROFILE_PATH = os.path.expandvars(r"%LOCALAPPDATA%/Temp/gologin_69024236bf3f011ec1593d23")


def kill_gologin_and_chrome():
    print("[INFO] Cerrando procesos de GoLogin y Chrome...")
    subprocess.call('taskkill /F /IM chrome.exe', shell=True)
    subprocess.call('taskkill /F /IM orbita.exe', shell=True)
    subprocess.call('taskkill /F /IM gologin.exe', shell=True)
    print("[INFO] Procesos cerrados.")

def remove_temp_profile():
    print(f"[INFO] Eliminando carpeta temporal: {TEMP_PROFILE_PATH}")
    if os.path.exists(TEMP_PROFILE_PATH):
        shutil.rmtree(TEMP_PROFILE_PATH, ignore_errors=True)
        print("[INFO] Carpeta temporal eliminada.")
    else:
        print("[INFO] Carpeta temporal no existe, nada que borrar.")

def main():
    kill_gologin_and_chrome()
    remove_temp_profile()
    print("[INFO] Listo. Ahora puedes volver a ejecutar tu script de automatización.")

if __name__ == "__main__":
    main()
