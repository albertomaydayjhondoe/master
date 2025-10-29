"""
Script para descargar el dataset COCO 2017 (train/val) en entorno Railway o local.
Coloca los datos en /app/data/datasets/coco/ por defecto.
"""
import os
import requests
from zipfile import ZipFile

COCO_URLS = {
    "train_images": "http://images.cocodataset.org/zips/train2017.zip",
    "val_images": "http://images.cocodataset.org/zips/val2017.zip",
    "annotations": "http://images.cocodataset.org/annotations/annotations_trainval2017.zip"
}

TARGET_DIR = os.environ.get("COCO_DATASET_DIR", "/app/data/datasets/coco/")
os.makedirs(TARGET_DIR, exist_ok=True)

def download_and_extract(url, dest_dir):
    local_zip = os.path.join(dest_dir, url.split("/")[-1])
    if not os.path.exists(local_zip):
        print(f"Descargando {url}...")
        r = requests.get(url, stream=True)
        with open(local_zip, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    else:
        print(f"{local_zip} ya existe, omitiendo descarga.")
    print(f"Extrayendo {local_zip}...")
    with ZipFile(local_zip, 'r') as zip_ref:
        zip_ref.extractall(dest_dir)

if __name__ == "__main__":
    for name, url in COCO_URLS.items():
        download_and_extract(url, TARGET_DIR)
    print(f"COCO descargado y extraído en {TARGET_DIR}")
