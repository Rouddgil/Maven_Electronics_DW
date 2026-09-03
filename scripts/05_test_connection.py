import os
import psycopg2
from dotenv import load_dotenv

# Charger le fichier .env
load_dotenv()

# Récupérer les paramètres de connexion
host = os.getenv("SUPABASE_HOST")
port = os.getenv("SUPABASE_PORT")
database = os.getenv("SUPABASE_DB")
user = os.getenv("SUPABASE_USER")
password = os.getenv("SUPABASE_PASSWORD")

print("=" * 60)
print("TEST DE CONNEXION À SUPABASE")
print("=" * 60)

print("\nConnexion à Supabase en cours...")

try:

    connection = psycopg2.connect(
        host=host,
        port=port,
        database=database,
        user=user,
        password=password
    )

    print("\n✓ Connexion réussie à Supabase !")

    # Création du curseur
    cursor = connection.cursor()

    # Vérification de PostgreSQL
    cursor.execute("SELECT version();")

    version = cursor.fetchone()

    print("\nVersion PostgreSQL :")
    print(version[0])

    # Fermeture
    cursor.close()
    connection.close()

    print("\n✓ Connexion fermée correctement.")
    print("\nTEST TERMINÉ AVEC SUCCÈS.")

except Exception as e:

    print("\n✗ ERREUR DE CONNEXION")
    print("=" * 60)
    print(e)