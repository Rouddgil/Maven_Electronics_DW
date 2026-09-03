import os
import psycopg2
from dotenv import load_dotenv

# ============================================================
# CHARGEMENT DES VARIABLES D'ENVIRONNEMENT
# ============================================================

load_dotenv()

host = os.getenv("SUPABASE_HOST")
port = os.getenv("SUPABASE_PORT")
database = os.getenv("SUPABASE_DB")
user = os.getenv("SUPABASE_USER")
password = os.getenv("SUPABASE_PASSWORD")


# ============================================================
# CONNEXION À SUPABASE
# ============================================================

print("=" * 70)
print("CRÉATION DU DATA WAREHOUSE MAVEN ELECTRONICS")
print("=" * 70)

print("\nConnexion à Supabase...")

connection = None

try:

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
    # SUPPRESSION DES TABLES EXISTANTES
    # ========================================================

    print("\nSuppression des anciennes tables si elles existent...")

    cursor.execute("""
        DROP TABLE IF EXISTS fact_sales CASCADE;
        DROP TABLE IF EXISTS dim_exchange_rate CASCADE;
        DROP TABLE IF EXISTS dim_product CASCADE;
        DROP TABLE IF EXISTS dim_customer CASCADE;
        DROP TABLE IF EXISTS dim_store CASCADE;
        DROP TABLE IF EXISTS dim_date CASCADE;
    """)

    print("✓ Anciennes tables supprimées.")


    # ========================================================
    # 1. DIM_DATE
    # ========================================================

    print("\nCréation de Dim_Date...")

    cursor.execute("""
        CREATE TABLE dim_date (
            date_key INTEGER PRIMARY KEY,
            full_date DATE NOT NULL,
            day INTEGER,
            month INTEGER,
            month_name VARCHAR(20),
            quarter INTEGER,
            year INTEGER,
            day_of_week INTEGER,
            day_name VARCHAR(20)
        );
    """)

    print("✓ Dim_Date créée.")


    # ========================================================
    # 2. DIM_CUSTOMER
    # ========================================================

    print("\nCréation de Dim_Customer...")

    cursor.execute("""
        CREATE TABLE dim_customer (
            customer_key INTEGER PRIMARY KEY,
            gender VARCHAR(50),
            name VARCHAR(200),
            city VARCHAR(150),
            state_code VARCHAR(50),
            state VARCHAR(150),
            zip_code VARCHAR(50),
            country VARCHAR(150),
            continent VARCHAR(100),
            birthday DATE
        );
    """)

    print("✓ Dim_Customer créée.")


    # ========================================================
    # 3. DIM_PRODUCT
    # ========================================================

    print("\nCréation de Dim_Product...")

    cursor.execute("""
        CREATE TABLE dim_product (
            product_key INTEGER PRIMARY KEY,
            product_name VARCHAR(200),
            brand VARCHAR(100),
            color VARCHAR(100),
            unit_cost_usd NUMERIC(12,2),
            unit_price_usd NUMERIC(12,2),
            subcategory_key INTEGER,
            subcategory VARCHAR(100),
            category_key INTEGER,
            category VARCHAR(100)
        );
    """)

    print("✓ Dim_Product créée.")


    # ========================================================
    # 4. DIM_STORE
    # ========================================================

    print("\nCréation de Dim_Store...")

    cursor.execute("""
        CREATE TABLE dim_store (
            store_key INTEGER PRIMARY KEY,
            country VARCHAR(100),
            state VARCHAR(150),
            square_meters NUMERIC(12,2),
            open_date DATE
        );
    """)

    print("✓ Dim_Store créée.")


    # ========================================================
    # 5. DIM_EXCHANGE_RATE
    # ========================================================

    print("\nCréation de Dim_Exchange_Rate...")

    cursor.execute("""
        CREATE TABLE dim_exchange_rate (
            date_key INTEGER NOT NULL,
            date DATE NOT NULL,
            currency VARCHAR(20) NOT NULL,
            exchange_rate NUMERIC(18,6) NOT NULL,

            PRIMARY KEY (date_key, currency)
        );
    """)

    print("✓ Dim_Exchange_Rate créée.")


    # ========================================================
    # 6. FACT_SALES
    # ========================================================

    print("\nCréation de Fact_Sales...")

    cursor.execute("""
        CREATE TABLE fact_sales (
            sales_key BIGSERIAL PRIMARY KEY,

            order_number INTEGER NOT NULL,
            line_item INTEGER NOT NULL,

            order_date_key INTEGER NOT NULL,
            delivery_date_key INTEGER,

            customer_key INTEGER NOT NULL,
            store_key INTEGER NOT NULL,
            product_key INTEGER NOT NULL,

            quantity INTEGER NOT NULL,
            currency_code VARCHAR(20) NOT NULL,

            CONSTRAINT uq_fact_sales_order_line
                UNIQUE (order_number, line_item),

            CONSTRAINT fk_sales_order_date
                FOREIGN KEY (order_date_key)
                REFERENCES dim_date(date_key),

            CONSTRAINT fk_sales_delivery_date
                FOREIGN KEY (delivery_date_key)
                REFERENCES dim_date(date_key),

            CONSTRAINT fk_sales_customer
                FOREIGN KEY (customer_key)
                REFERENCES dim_customer(customer_key),

            CONSTRAINT fk_sales_store
                FOREIGN KEY (store_key)
                REFERENCES dim_store(store_key),

            CONSTRAINT fk_sales_product
                FOREIGN KEY (product_key)
                REFERENCES dim_product(product_key)
        );
    """)

    print("✓ Fact_Sales créée.")


    # ========================================================
    # VALIDATION
    # ========================================================

    connection.commit()

    print("\n" + "=" * 70)
    print("DATA WAREHOUSE CRÉÉ AVEC SUCCÈS !")
    print("=" * 70)


    # ========================================================
    # VÉRIFICATION DES TABLES
    # ========================================================

    cursor.execute("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
        AND table_name IN (
            'dim_date',
            'dim_customer',
            'dim_product',
            'dim_store',
            'dim_exchange_rate',
            'fact_sales'
        )
        ORDER BY table_name;
    """)

    tables = cursor.fetchall()

    print("\nTables créées :")

    for table in tables:
        print(f"  ✓ {table[0]}")


    # ========================================================
    # FERMETURE
    # ========================================================

    cursor.close()
    connection.close()

    print("\n✓ Connexion fermée.")
    print("\nÉtape terminée avec succès.")


except Exception as e:

    print("\n✗ ERREUR")
    print("=" * 70)
    print(e)

    if connection is not None:
        connection.rollback()
        connection.close()

    print("\nLes modifications ont été annulées.")