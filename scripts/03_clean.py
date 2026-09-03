import pandas as pd
from pathlib import Path

project_dir = Path(__file__).resolve().parent.parent
raw_dir = project_dir / "data" / "raw"
cleaned_dir = project_dir / "data" / "cleaned"
cleaned_dir.mkdir(parents=True, exist_ok=True)

def read_csv(file):
    """
    Lit un fichier CSV avec l'encodage latin1.
    """
    return pd.read_csv(file, encoding="latin1")

print("\n" + "=" * 60)
print("NETTOYAGE : CUSTOMERS")
print("=" * 60)

customers = read_csv(raw_dir / "Customers.csv")
customers = customers.rename(columns={
    "CustomerKey": "customer_key",
    "Gender": "gender",
    "Name": "name",
    "City": "city",
    "State Code": "state_code",
    "State": "state",
    "Zip Code": "zip_code",
    "Country": "country",
    "Continent": "continent",
    "Birthday": "birthday"
})

# Conversion de la date de naissance
customers["birthday"] = pd.to_datetime(
    customers["birthday"],
    errors="coerce"
)

# Les State Code manquants sont conservés comme NULL
customers["state_code"] = customers["state_code"].replace(
    r"^\s*$", pd.NA, regex=True
)

# Suppression des doublons
customers = customers.drop_duplicates()

# Sauvegarde
customers.to_csv(
    cleaned_dir / "dim_customer.csv",
    index=False,
    encoding="utf-8"
)

print(f"Clients nettoyés : {len(customers)}")
print("Fichier créé : dim_customer.csv")

print("\n" + "=" * 60)
print("NETTOYAGE : PRODUCTS")
print("=" * 60)

products = read_csv(raw_dir / "Products.csv")

# Standardisation des noms de colonnes
products = products.rename(columns={
    "ProductKey": "product_key",
    "Product Name": "product_name",
    "Brand": "brand",
    "Color": "color",
    "Unit Cost USD": "unit_cost_usd",
    "Unit Price USD": "unit_price_usd",
    "SubcategoryKey": "subcategory_key",
    "Subcategory": "subcategory",
    "CategoryKey": "category_key",
    "Category": "category"
})

# Conversion des prix en valeurs numériques
products["unit_cost_usd"] = (
    products["unit_cost_usd"]
    .astype(str)
    .str.replace("$", "", regex=False)
    .str.replace(",", "", regex=False)
    .str.strip()
)

products["unit_price_usd"] = (
    products["unit_price_usd"]
    .astype(str)
    .str.replace("$", "", regex=False)
    .str.replace(",", "", regex=False)
    .str.strip()
)

products["unit_cost_usd"] = pd.to_numeric(
    products["unit_cost_usd"],
    errors="coerce"
)

products["unit_price_usd"] = pd.to_numeric(
    products["unit_price_usd"],
    errors="coerce"
)

# Suppression des doublons
products = products.drop_duplicates()

# Sauvegarde
products.to_csv(
    cleaned_dir / "dim_product.csv",
    index=False,
    encoding="utf-8"
)

print(f"Produits nettoyés : {len(products)}")
print("Fichier créé : dim_product.csv")

print("\n" + "=" * 60)
print("NETTOYAGE : STORES")
print("=" * 60)

stores = read_csv(raw_dir / "Stores.csv")

stores = stores.rename(columns={
    "StoreKey": "store_key",
    "Country": "country",
    "State": "state",
    "Square Meters": "square_meters",
    "Open Date": "open_date"
})

# Conversion de la date d'ouverture
stores["open_date"] = pd.to_datetime(
    stores["open_date"],
    errors="coerce"
)

# Conversion numérique
stores["square_meters"] = pd.to_numeric(
    stores["square_meters"],
    errors="coerce"
)

# on utilise la médiane des magasins
median_area = stores["square_meters"].median()

stores["square_meters"] = stores["square_meters"].fillna(
    median_area
)

# Suppression des doublons
stores = stores.drop_duplicates()

# Sauvegarde
stores.to_csv(
    cleaned_dir / "dim_store.csv",
    index=False,
    encoding="utf-8"
)

print(f"Magasins nettoyés : {len(stores)}")
print("Fichier créé : dim_store.csv")

print("\n" + "=" * 60)
print("NETTOYAGE : SALES")
print("=" * 60)

sales = read_csv(raw_dir / "Sales.csv")

sales = sales.rename(columns={
    "Order Number": "order_number",
    "Line Item": "line_item",
    "Order Date": "order_date",
    "Delivery Date": "delivery_date",
    "CustomerKey": "customer_key",
    "StoreKey": "store_key",
    "ProductKey": "product_key",
    "Quantity": "quantity",
    "Currency Code": "currency_code"
})

# Conversion des dates
sales["order_date"] = pd.to_datetime(
    sales["order_date"],
    errors="coerce"
)

sales["delivery_date"] = pd.to_datetime(
    sales["delivery_date"],
    errors="coerce"
)

# Conversion de Quantity
sales["quantity"] = pd.to_numeric(
    sales["quantity"],
    errors="coerce"
)

sales = sales.dropna(subset=["order_date"])

# Création de la clé de date de commande
sales["order_date_key"] = (
    sales["order_date"]
    .dt.strftime("%Y%m%d")
    .astype(int)
)

# Les valeurs manquantes restent NULL.
sales["delivery_date_key"] = pd.to_numeric(
    sales["delivery_date"].dt.strftime("%Y%m%d"),
    errors="coerce"
).astype("Int64")

# Suppression des doublons exacts
sales = sales.drop_duplicates()

# Sauvegarde
sales.to_csv(
    cleaned_dir / "fact_sales.csv",
    index=False,
    encoding="utf-8"
)

print(f"Lignes de ventes nettoyées : {len(sales)}")
print("Fichier créé : fact_sales.csv")

print("\n" + "=" * 60)
print("NETTOYAGE : EXCHANGE RATES")
print("=" * 60)

exchange_rates = read_csv(
    raw_dir / "Exchange_Rates.csv"
)

exchange_rates = exchange_rates.rename(columns={
    "Date": "date",
    "Currency": "currency",
    "Exchange": "exchange_rate"
})

# Conversion de la date
exchange_rates["date"] = pd.to_datetime(
    exchange_rates["date"],
    errors="coerce"
)

# Conversion du taux
exchange_rates["exchange_rate"] = pd.to_numeric(
    exchange_rates["exchange_rate"],
    errors="coerce"
)

# Suppression des lignes dont les informations essentielles sont absentes
exchange_rates = exchange_rates.dropna(
    subset=["date", "currency", "exchange_rate"]
)

# Création de la clé de date
exchange_rates["date_key"] = (
    exchange_rates["date"]
    .dt.strftime("%Y%m%d")
    .astype(int)
)

# Suppression des doublons
exchange_rates = exchange_rates.drop_duplicates()

# Sauvegarde
exchange_rates.to_csv(
    cleaned_dir / "dim_exchange_rate.csv",
    index=False,
    encoding="utf-8"
)

print(f"Taux de change nettoyés : {len(exchange_rates)}")
print("Fichier créé : dim_exchange_rate.csv")

print("\n" + "=" * 60)
print("CRÉATION : DIM DATE")
print("=" * 60)

min_date = sales["order_date"].min()
max_order_date = sales["order_date"].max()

# On inclut également les dates de livraison disponibles
if sales["delivery_date"].notna().any():

    max_delivery_date = sales["delivery_date"].max()

    if max_delivery_date > max_order_date:
        max_date = max_delivery_date
    else:
        max_date = max_order_date

else:
    max_date = max_order_date


# Création du calendrier
date_range = pd.date_range(
    start=min_date,
    end=max_date,
    freq="D"
)

dim_date = pd.DataFrame({
    "full_date": date_range
})

# Clé de date
dim_date["date_key"] = (
    dim_date["full_date"]
    .dt.strftime("%Y%m%d")
    .astype(int)
)

# Informations calendaires
dim_date["day"] = dim_date["full_date"].dt.day
dim_date["month"] = dim_date["full_date"].dt.month
dim_date["quarter"] = dim_date["full_date"].dt.quarter
dim_date["year"] = dim_date["full_date"].dt.year
dim_date["day_of_week"] = dim_date["full_date"].dt.dayofweek + 1

# Noms des mois et jours
dim_date["month_name"] = dim_date["full_date"].dt.month_name()
dim_date["day_name"] = dim_date["full_date"].dt.day_name()

# Réorganisation
dim_date = dim_date[
    [
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
]

# Sauvegarde
dim_date.to_csv(
    cleaned_dir / "dim_date.csv",
    index=False,
    encoding="utf-8"
)

print(f"Dates créées : {len(dim_date)}")
print("Fichier créé : dim_date.csv")

# 9. RAPPORT FINAL DU NETTOYAGE

print("\n" + "=" * 60)
print("NETTOYAGE TERMINÉ")
print("=" * 60)

print("\nFichiers créés dans data/cleaned :")

for file in sorted(cleaned_dir.glob("*.csv")):
    print(f"  ✓ {file.name}")

print("\nNombre total de fichiers nettoyés :",
      len(list(cleaned_dir.glob("*.csv"))))

print("\nLe nettoyage est terminé avec succès.")