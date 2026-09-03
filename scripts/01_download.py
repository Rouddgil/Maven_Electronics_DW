import requests
import zipfile
from pathlib import Path

url = "https://maven-datasets.s3.amazonaws.com/Global+Electronics+Retailer/Global+Electronics+Retailer.zip"
project_dir = Path(__file__).resolve().parent.parent
raw_dir = project_dir / "data" / "raw"
raw_dir.mkdir(parents=True, exist_ok=True)
zip_path = raw_dir / "Global_Electronics_Retailer.zip"
print("Téléchargement du dataset Maven...")
response = requests.get(url)
response.raise_for_status()
with open(zip_path, "wb") as file:
    file.write(response.content)
print("Téléchargement terminé.")
# Extraire le ZIP
print("Extraction des fichiers...")
with zipfile.ZipFile(zip_path, "r") as zip_ref:
    zip_ref.extractall(raw_dir)
print("Extraction terminée.")
# Supprimer le ZIP après extraction
zip_path.unlink()
print("Fichier ZIP supprimé.")
print("Dataset Maven téléchargé avec succès !")
