import pandas as pd
from pathlib import Path
project_dir = Path(__file__).resolve().parent.parent

raw_dir = project_dir / "data" / "raw"
print("=" * 60)
print("INSPECTION DES DATASETS MAVEN")
print("=" * 60)

csv_files = list(raw_dir.rglob("*.csv"))

print(f"\nNombre de fichiers CSV trouvés : {len(csv_files)}\n")

for file in csv_files:

    print("\n" + "=" * 60)
    print(f"FICHIER : {file.name}")
    print("=" * 60)

    try:
        df = pd.read_csv(file, encoding="latin1")

        print(f"\nNombre de lignes : {df.shape[0]}")
        print(f"Nombre de colonnes : {df.shape[1]}")

        print("\nColonnes :")
        print(list(df.columns))

        print("\nTypes de données :")
        print(df.dtypes)

        print("\nValeurs manquantes :")
        print(df.isnull().sum())

        print("\nDoublons :")
        print(df.duplicated().sum())

        print("\nPremières lignes :")
        print(df.head(3))

    except Exception as e:
        print(f"\nERREUR lors de la lecture de {file.name}")
        print(f"Type d'erreur : {type(e).__name__}")
        print(f"Message : {e}")

print("\n" + "=" * 60)
print("INSPECTION TERMINÉE")
print("=" * 60)