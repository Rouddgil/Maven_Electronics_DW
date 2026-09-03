import os
import pandas as pd
import psycopg2
from dotenv import load_dotenv
from pathlib import Path
from psycopg2.extras import execute_values


# ============================================================
# CONFIGURATION
# ============================================================

load_dotenv()

project_dir = Path(__file__).resolve().parent.parent
cleaned_dir = project_dir / "data" / "cleaned"

host = os.getenv("SUPABASE_HOST")
port = os.getenv("SUPABASE_PORT")
database = os.getenv("SUPABASE_DB")
user = os.getenv("SUPABASE_USER")
password = os.getenv("SUPABASE_PASSWORD")


# ============================================================
# FONCTION DE LECTURE DES CSV
# ============================================================

def read_csv(filename):

    file_path = cleaned_dir / filename

    if not file_path.exists():
        raise FileNotFoundError(
            f"Fichier introuvable : {file_path}"
        )

    return pd.read_csv(file_path)


# ============================================================
# FONCTION DE CHARGEMENT DES DONNÉES
# ============================================================

def load_table(cursor, table_name, dataframe, columns):

    # Sélection des colonnes nécessaires
    data = dataframe[columns].copy()

    # Remplacement des valeurs manquantes par None
    data = data.where(pd.notnull(data), None)

    values = []

    for row in data.itertuples(index=False, name=None):

        clean_row = []

        for value in row:

            # Valeur manquante
            if pd.isna(value):
                clean_row.append(None)

            # Conversion des types NumPy en types Python
            elif hasattr(value, "item"):
                clean_row.append(value.item())

            # Valeur normale
            else:
                clean_row.append(value)

        values.append(tuple(clean_row))

    if not values:
        print(f"⚠ Aucune donnée à charger dans {table_name}.")
        return 0

    column_names = ", ".join(columns)

    query = f"""
        INSERT INTO {table_name} ({column_names})
        VALUES %s
    """

    execute_values(
        cursor,
        query,
        values,
        page_size=1000
    )

    return len(values)


# ============================================================
# DÉBUT DU PROGRAMME
# ============================================================

print("=" * 70)
print("CHARGEMENT DU DATA WAREHOUSE MAVEN ELECTRONICS")
print("=" * 70)


connection = None

try:

    # ========================================================
    # CONNEXION À SUPABASE
    # ========================================================

    print("\nConnexion à Supabase...")

    connection = psycopg2.connect(
        host=host,
        port=port,
        database=database,
        user=user,
        password=password
    )

    cursor = connection.cursor()

    print("✓ Connexion réussie.")


    # ========================================================
    # LECTURE DES FICHIERS NETTOYÉS
    # ========================================================

    print("\nLecture des fichiers nettoyés...")

    dim_date = read_csv("dim_date.csv")
    dim_customer = read_csv("dim_customer.csv")
    dim_product = read_csv("dim_product.csv")
    dim_store = read_csv("dim_store.csv")
    dim_exchange_rate = read_csv("dim_exchange_rate.csv")
    fact_sales = read_csv("fact_sales.csv")

    print("✓ Tous les fichiers ont été trouvés.")


    # ========================================================
    # AFFICHAGE DU NOMBRE DE LIGNES
    # ========================================================

    print("\nNombre de lignes à charger :")

    print(f"  Dim_Date           : {len(dim_date)}")
    print(f"  Dim_Customer       : {len(dim_customer)}")
    print(f"  Dim_Product        : {len(dim_product)}")
    print(f"  Dim_Store          : {len(dim_store)}")
    print(f"  Dim_Exchange_Rate  : {len(dim_exchange_rate)}")
    print(f"  Fact_Sales         : {len(fact_sales)}")


    # ========================================================
    # SUPPRESSION DES ANCIENNES DONNÉES
    # ========================================================

    print("\nSuppression des anciennes données...")

    cursor.execute("""
        TRUNCATE TABLE
            fact_sales,
            dim_exchange_rate,
            dim_product,
            dim_customer,
            dim_store,
            dim_date
        RESTART IDENTITY CASCADE;
    """)

    print("✓ Anciennes données supprimées.")


    # ========================================================
    # 1. DIM_DATE
    # ========================================================

    print("\n[1/6] Chargement de Dim_Date...")

    columns = [
        "date_key",
        "full_date",
        "day",
        "month",
        "month_name",
        "quarter",
        "year",
        "day_of_week",
        "day_name"
    ]

    count = load_table(
        cursor,
        "dim_date",
        dim_date,
        columns
    )

    print(f"✓ {count} lignes chargées dans Dim_Date.")


    # ========================================================
    # 2. DIM_CUSTOMER
    # ========================================================

    print("\n[2/6] Chargement de Dim_Customer...")

    columns = [
        "customer_key",
        "gender",
        "name",
        "city",
        "state_code",
        "state",
        "zip_code",
        "country",
        "continent",
        "birthday"
    ]

    count = load_table(
        cursor,
        "dim_customer",
        dim_customer,
        columns
    )

    print(f"✓ {count} lignes chargées dans Dim_Customer.")


    # ========================================================
    # 3. DIM_PRODUCT
    # ========================================================

    print("\n[3/6] Chargement de Dim_Product...")

    columns = [
        "product_key",
        "product_name",
        "brand",
        "color",
        "unit_cost_usd",
        "unit_price_usd",
        "subcategory_key",
        "subcategory",
        "category_key",
        "category"
    ]

    count = load_table(
        cursor,
        "dim_product",
        dim_product,
        columns
    )

    print(f"✓ {count} lignes chargées dans Dim_Product.")


    # ========================================================
    # 4. DIM_STORE
    # ========================================================

    print("\n[4/6] Chargement de Dim_Store...")

    columns = [
        "store_key",
        "country",
        "state",
        "square_meters",
        "open_date"
    ]

    count = load_table(
        cursor,
        "dim_store",
        dim_store,
        columns
    )

    print(f"✓ {count} lignes chargées dans Dim_Store.")


    # ========================================================
    # 5. DIM_EXCHANGE_RATE
    # ========================================================

    print("\n[5/6] Chargement de Dim_Exchange_Rate...")

    columns = [
        "date_key",
        "date",
        "currency",
        "exchange_rate"
    ]

    count = load_table(
        cursor,
        "dim_exchange_rate",
        dim_exchange_rate,
        columns
    )

    print(f"✓ {count} lignes chargées dans Dim_Exchange_Rate.")


    # ========================================================
    # 6. FACT_SALES
    # ========================================================

    print("\n[6/6] Chargement de Fact_Sales...")

    columns = [
        "order_number",
        "line_item",
        "order_date_key",
        "delivery_date_key",
        "customer_key",
        "store_key",
        "product_key",
        "quantity",
        "currency_code"
    ]

    count = load_table(
        cursor,
        "fact_sales",
        fact_sales,
        columns
    )

    print(f"✓ {count} lignes chargées dans Fact_Sales.")


    # ========================================================
    # VALIDATION
    # ========================================================

    connection.commit()

    print("\n" + "=" * 70)
    print("CHARGEMENT TERMINÉ AVEC SUCCÈS !")
    print("=" * 70)


    # ========================================================
    # VÉRIFICATION DU NOMBRE DE LIGNES
    # ========================================================

    print("\nVérification des tables dans Supabase :")

    tables = [
        "dim_date",
        "dim_customer",
        "dim_product",
        "dim_store",
        "dim_exchange_rate",
        "fact_sales"
    ]

    for table in tables:

        cursor.execute(
            f"SELECT COUNT(*) FROM {table};"
        )

        result = cursor.fetchone()[0]

        print(f"  ✓ {table:<22} : {result} lignes")


    # ========================================================
    # FERMETURE DE LA CONNEXION
    # ========================================================

    cursor.close()
    connection.close()

    print("\n✓ Connexion fermée.")
    print("✓ Data Warehouse chargé correctement.")


# ============================================================
# GESTION DES ERREURS
# ============================================================

except Exception as e:

    print("\n✗ ERREUR PENDANT LE CHARGEMENT")
    print("=" * 70)
    print(e)

    if connection is not None:

        connection.rollback()
        connection.close()

    print("\nLes modifications ont été annulées.")