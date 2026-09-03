import subprocess
import sys
from pathlib import Path
from prefect import flow, task


# ============================================================
# ORCHESTRATION DU PIPELINE ETL
# Maven Electronics Data Warehouse
# ============================================================

project_dir = Path(__file__).resolve().parent.parent
scripts_dir = project_dir / "scripts"


@task(name="Téléchargement des données")
def download_data():
    print("\n>>> Téléchargement des données")
    subprocess.run(
        [sys.executable, str(scripts_dir / "01_download.py")],
        cwd=project_dir,
        check=True
    )


@task(name="Inspection des données")
def inspect_data():
    print("\n>>> Inspection des données")
    subprocess.run(
        [sys.executable, str(scripts_dir / "02_inspect.py")],
        cwd=project_dir,
        check=True
    )


@task(name="Nettoyage des données")
def clean_data():
    print("\n>>> Nettoyage des données")
    subprocess.run(
        [sys.executable, str(scripts_dir / "03_clean.py")],
        cwd=project_dir,
        check=True
    )


@task(name="Test de connexion Supabase")
def test_connection():
    print("\n>>> Test de connexion à Supabase")
    subprocess.run(
        [sys.executable, str(scripts_dir / "05_test_connection.py")],
        cwd=project_dir,
        check=True
    )


@task(name="Création du Data Warehouse")
def create_dw():
    print("\n>>> Création du Data Warehouse")
    subprocess.run(
        [sys.executable, str(scripts_dir / "04_create_dw.py")],
        cwd=project_dir,
        check=True
    )


@task(name="Chargement du Data Warehouse")
def load_dw():
    print("\n>>> Chargement du Data Warehouse")
    subprocess.run(
        [sys.executable, str(scripts_dir / "06_load_dw.py")],
        cwd=project_dir,
        check=True
    )


@flow(name="Maven Electronics ETL Pipeline")
def maven_electronics_pipeline():

    download_data()

    inspect_data()

    clean_data()

    test_connection()

    create_dw()

    load_dw()


# ============================================================
# LANCEMENT DU PIPELINE
# ============================================================

if __name__ == "__main__":
    maven_electronics_pipeline()