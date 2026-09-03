# Maven Electronics — Data Warehouse & BI

## 1. Présentation du projet

Ce projet consiste à concevoir et mettre en œuvre un **Data Warehouse décisionnel** pour l’entreprise **Maven Electronics**, spécialisée dans la vente de produits électroniques à travers plusieurs magasins et zones géographiques.

L’objectif principal est de centraliser, nettoyer et structurer les données commerciales afin de faciliter l’analyse des ventes et de soutenir la prise de décision.

Le projet couvre l’ensemble de la chaîne décisionnelle :

**Sources de données → ETL → Data Warehouse → Modèle dimensionnel → Power BI**

L’architecture mise en place permet également d’assurer la **reproductibilité du traitement des données** grâce à l’orchestration avec **Prefect** et au versionnement du code avec **Git/GitHub**.

---

## 2. Objectifs

Les principaux objectifs du projet sont :

* analyser les données commerciales de Maven Electronics ;
* identifier le processus métier principal ;
* définir la granularité du processus de vente ;
* concevoir un modèle dimensionnel cohérent ;
* nettoyer et harmoniser les données sources ;
* construire physiquement le Data Warehouse ;
* automatiser le pipeline ETL ;
* charger les données dans PostgreSQL ;
* contrôler la qualité et l'intégrité des données ;
* créer des indicateurs décisionnels ;
* développer un tableau de bord interactif avec Power BI ;
* assurer la reproductibilité du projet grâce à GitHub et Prefect.

---

## 3. Sources de données

Les données sources proviennent du jeu de données **Global Electronics Retailer** de Maven Analytics.

Les principaux fichiers utilisés sont :

| Fichier source        | Description                   |
| --------------------- | ----------------------------- |
| `Customers.csv`       | Informations sur les clients  |
| `Products.csv`        | Informations sur les produits |
| `Stores.csv`          | Informations sur les magasins |
| `Sales.csv`           | Transactions de vente         |
| `Exchange_Rates.csv`  | Taux de change                |
| `Data_Dictionary.csv` | Description des variables     |

Le fichier `Data_Dictionary.csv` est utilisé comme documentation des données et n'est pas chargé comme table du Data Warehouse.

---

## 4. Processus métier et granularité

### Processus métier

Le processus métier étudié est le **processus de vente**.

Il correspond aux transactions commerciales réalisées par Maven Electronics et permet d'analyser les ventes selon plusieurs axes : date, client, produit, magasin et devise.

### Granularité

La granularité de la table de faits est :

> **Une ligne de produit vendue dans une commande, à une date donnée, pour un client et un magasin donnés.**

Cette granularité est notamment définie par la combinaison :

`Order Number + Line Item`

Cette combinaison permet d'identifier de manière unique chaque ligne de vente.

---

## 5. Architecture du Data Warehouse

L'architecture générale du projet est la suivante :

```text
                  SOURCES DE DONNÉES
                         │
                         ▼
              ┌─────────────────────┐
              │   01_download.py    │
              │ Téléchargement      │
              └──────────┬──────────┘
                         │
                         ▼
                    data/raw/
                         │
                         ▼
              ┌─────────────────────┐
              │   02_inspect.py     │
              │ Inspection / Profil │
              └──────────┬──────────┘
                         │
                         ▼
              ┌─────────────────────┐
              │    03_clean.py      │
              │ Nettoyage / ETL     │
              └──────────┬──────────┘
                         │
                         ▼
                   data/cleaned/
                         │
                         ▼
              ┌─────────────────────┐
              │ 04_create_dw.py    │
              │ Création du DW      │
              └──────────┬──────────┘
                         │
                         ▼
              ┌─────────────────────┐
              │ 06_load_dw.py      │
              │ Chargement          │
              └──────────┬──────────┘
                         │
                         ▼
                PostgreSQL / Supabase
                         │
                         ▼
                 Data Warehouse
                         │
                         ▼
                      Power BI
```

---

## 6. Modèle dimensionnel

Le Data Warehouse repose sur un **schéma en étoile** centré sur la table de faits `fact_sales`.

### Table de faits

`fact_sales`

Elle contient les mesures et les clés permettant d'analyser les transactions commerciales.

Principales colonnes :

* `sales_key`
* `order_number`
* `line_item`
* `order_date_key`
* `delivery_date_key`
* `customer_key`
* `store_key`
* `product_key`
* `quantity`
* `currency_code`

### Dimensions

Le modèle comprend les dimensions suivantes :

* `dim_date`
* `dim_customer`
* `dim_product`
* `dim_store`
* `dim_exchange_rate`

### Schéma conceptuel

```text
                       dim_customer
                            │
                            │
                            ▼
dim_date ───────────► fact_sales ◄────────── dim_product
                            │
                            │
                            ▼
                       dim_store

                            │
                            │
                            ▼
                    dim_exchange_rate
```

La dimension `dim_date` permet notamment l'analyse temporelle des ventes.

La relation avec `order_date_key` est utilisée comme relation active pour l'analyse des commandes. La date de livraison peut être utilisée comme seconde relation temporelle lorsque nécessaire.

---

## 7. Pipeline ETL

Le pipeline ETL est composé de plusieurs étapes.

### Étape 1 — Téléchargement

Le script `01_download.py` télécharge automatiquement le jeu de données Maven Analytics et extrait les fichiers sources dans :

```text
data/raw/
```

### Étape 2 — Inspection

Le script `02_inspect.py` permet de réaliser un premier contrôle des données :

* nombre de lignes ;
* nombre de colonnes ;
* types de données ;
* valeurs manquantes ;
* doublons ;
* informations générales sur les tables.

### Étape 3 — Nettoyage et transformation

Le script `03_clean.py` réalise notamment :

* le traitement des valeurs manquantes ;
* la conversion des types de données ;
* l'harmonisation des dates ;
* la création de clés de dimensions ;
* la préparation des dimensions ;
* la préparation de la table de faits ;
* la génération des fichiers nettoyés.

Les données nettoyées sont enregistrées dans :

```text
data/cleaned/
```

Les fichiers générés comprennent :

```text
dim_customer.csv
dim_date.csv
dim_exchange_rate.csv
dim_product.csv
dim_store.csv
fact_sales.csv
```

### Étape 4 — Création du Data Warehouse

Le script `04_create_dw.py` crée les structures physiques du Data Warehouse dans PostgreSQL.

Il crée les tables :

```text
dim_date
dim_customer
dim_product
dim_store
dim_exchange_rate
fact_sales
```

Les clés primaires et clés étrangères sont également définies.

### Étape 5 — Test de connexion

Le script `05_test_connection.py` vérifie la connexion entre l'environnement Python et PostgreSQL/Supabase.

### Étape 6 — Chargement

Le script `06_load_dw.py` charge les données nettoyées dans les tables du Data Warehouse.

### Étape 7 — Validation

Le fichier :

```text
sql/01_validation_dw.sql
```

contient les contrôles permettant de vérifier :

* les nombres de lignes ;
* les clés primaires ;
* les clés étrangères ;
* les lignes orphelines ;
* l'unicité des transactions ;
* les statistiques de base de la table de faits.

---

## 8. Orchestration avec Prefect

Le pipeline ETL est orchestré avec **Prefect**.

Le script :

```text
scripts/07_orchestrate.py
```

regroupe les différentes étapes du pipeline sous la forme d'un workflow.

Le flux est organisé comme suit :

```text
Téléchargement
      ↓
Inspection
      ↓
Nettoyage
      ↓
Test connexion PostgreSQL
      ↓
Création du Data Warehouse
      ↓
Chargement
```

Cette orchestration permet :

* d'exécuter les étapes dans un ordre contrôlé ;
* de suivre l'état de chaque tâche ;
* d'identifier les erreurs ;
* de faciliter la reproductibilité ;
* de disposer d'une interface de suivi des exécutions.

Le pipeline peut être lancé avec :

```powershell
python scripts\07_orchestrate.py
```

---

## 9. Data Warehouse avec Supabase PostgreSQL

Le Data Warehouse est hébergé dans **PostgreSQL via Supabase**.

Supabase fournit l'environnement PostgreSQL utilisé pour stocker les tables dimensionnelles et la table de faits.

Les tables principales sont :

```text
public.dim_date
public.dim_customer
public.dim_product
public.dim_store
public.dim_exchange_rate
public.fact_sales
```

### Volumétrie chargée

Après nettoyage et chargement, le Data Warehouse contient :

| Table               | Nombre de lignes |
| ------------------- | ---------------: |
| `dim_date`          |            1 885 |
| `dim_customer`      |           15 266 |
| `dim_product`       |            2 517 |
| `dim_store`         |               67 |
| `dim_exchange_rate` |           11 215 |
| `fact_sales`        |           62 884 |

Ces contrôles permettent de vérifier que le chargement du Data Warehouse correspond aux données préparées lors du processus ETL.

---

## 10. Power BI

**Power BI** est utilisé comme outil de Business Intelligence et de visualisation.

Power BI est connecté directement au Data Warehouse PostgreSQL hébergé dans Supabase.

Les principales analyses réalisées portent sur :

* le chiffre d'affaires ;
* la marge brute ;
* le taux de marge brute ;
* la quantité vendue ;
* le nombre de commandes ;
* l'évolution des ventes dans le temps ;
* les ventes par catégorie ;
* les ventes par pays ;
* les performances des magasins ;
* les produits les plus vendus.

### Exemples de mesures DAX

#### Chiffre d'affaires

```DAX
Chiffre d'affaires =
SUMX(
    fact_sales,
    fact_sales[quantity] * RELATED(dim_product[unit_price_usd])
)
```

#### Coût total

```DAX
Coût total =
SUMX(
    fact_sales,
    fact_sales[quantity] * RELATED(dim_product[unit_cost_usd])
)
```

#### Marge brute

```DAX
Marge brute =
[Chiffre d'affaires] - [Coût total]
```

#### Taux de marge brute

```DAX
Taux de marge brute =
DIVIDE(
    [Marge brute],
    [Chiffre d'affaires],
    0
)
```

#### Nombre de commandes

```DAX
Nombre de commandes =
DISTINCTCOUNT(fact_sales[order_number])
```

#### Quantité totale

```DAX
Quantité totale =
SUM(fact_sales[quantity])
```

---

## 11. Structure du projet

```text
Maven_Electronics_DW/
│
├── data/
│   ├── raw/
│   └── cleaned/
│
├── scripts/
│   ├── 01_download.py
│   ├── 02_inspect.py
│   ├── 03_clean.py
│   ├── 04_create_dw.py
│   ├── 05_test_connection.py
│   ├── 06_load_dw.py
│   └── 07_orchestrate.py
│
├── sql/
│   └── 01_validation_dw.sql
│
├── notebooks/
│
├── .env
├── .gitignore
├── countries.json
└── requirements.txt
```

### Sécurité

Le fichier `.env` contient les informations de connexion à PostgreSQL et **n'est pas versionné dans Git**.

Les répertoires suivants sont également exclus du dépôt GitHub :

```text
data/raw/
data/cleaned/
```

Cela permet d'éviter de publier des données ou des informations de connexion qui ne doivent pas être exposées.

---

## 12. Installation

### Prérequis

Le projet nécessite notamment :

* Python 3.13 ou version compatible ;
* Git ;
* un compte GitHub ;
* une base PostgreSQL/Supabase ;
* Power BI Desktop pour la partie visualisation.

### Cloner le projet

```powershell
git clone https://github.com/Rouddgil/Maven_Electronics_DW.git
cd Maven_Electronics_DW
```

### Installer les dépendances

```powershell
pip install -r requirements.txt
```

Les principales bibliothèques utilisées sont :

```text
pandas
numpy
requests
python-dotenv
psycopg2-binary
prefect
```

### Configurer les variables d'environnement

Créer un fichier `.env` à la racine du projet avec les paramètres de connexion PostgreSQL nécessaires.

Le fichier `.env` ne doit jamais être publié sur GitHub.

---

## 13. Exécution du pipeline

Le pipeline peut être exécuté étape par étape :

```powershell
python scripts\01_download.py
python scripts\02_inspect.py
python scripts\03_clean.py
python scripts\05_test_connection.py
python scripts\04_create_dw.py
python scripts\06_load_dw.py
```

Ou directement à travers Prefect :

```powershell
python scripts\07_orchestrate.py
```

L'utilisation de Prefect est recommandée pour l'exécution complète et reproductible du pipeline.

---

## 14. Validation du Data Warehouse

Après le chargement, les contrôles SQL peuvent être exécutés à partir de :

```text
sql/01_validation_dw.sql
```

Les validations portent notamment sur :

* l'existence des tables ;
* le nombre de lignes ;
* les clés primaires ;
* les clés étrangères ;
* les relations entre les dimensions et la table de faits ;
* l'absence de lignes orphelines ;
* l'unicité des lignes de vente.

---

## 15. Reproductibilité

L'objectif du projet est de permettre à un autre utilisateur de reproduire le traitement à partir du code disponible dans GitHub.

Le processus reproductible est :

```text
1. Cloner le dépôt GitHub
          ↓
2. Installer les dépendances
          ↓
3. Configurer les variables .env
          ↓
4. Télécharger les données
          ↓
5. Inspecter les données
          ↓
6. Nettoyer et transformer
          ↓
7. Créer les tables PostgreSQL
          ↓
8. Charger le Data Warehouse
          ↓
9. Valider les données
          ↓
10. Connecter Power BI
```

Le versionnement du code avec Git/GitHub permet de conserver l'historique des modifications et de faciliter la collaboration et la maintenance du projet.

---

## 16. Technologies utilisées

| Technologie | Rôle                                       |
| ----------- | ------------------------------------------ |
| Python      | Développement du pipeline ETL              |
| Pandas      | Manipulation et transformation des données |
| NumPy       | Traitement numérique                       |
| PostgreSQL  | Système de gestion de base de données      |
| Supabase    | Hébergement PostgreSQL                     |
| Psycopg2    | Connexion Python à PostgreSQL              |
| Prefect     | Orchestration du pipeline ETL              |
| Power BI    | Analyse et visualisation                   |
| Git         | Gestion des versions                       |
| GitHub      | Hébergement du code source                 |

---

## 17. Résultat attendu

À l'issue du projet, l'organisation dispose d'une architecture décisionnelle permettant de transformer les données transactionnelles brutes en informations exploitables.

L'architecture finale peut être résumée ainsi :

```text
Maven Analytics
      │
      ▼
Données brutes
      │
      ▼
Python / Pandas
      │
      ▼
Nettoyage & Transformation
      │
      ▼
Prefect
      │
      ▼
PostgreSQL / Supabase
      │
      ▼
Data Warehouse
      │
      ▼
Schéma en étoile
      │
      ▼
Power BI
      │
      ▼
Tableau de bord décisionnel
```

---

## 18. Conclusion

Ce projet met en œuvre une solution complète de Business Intelligence pour Maven Electronics. La centralisation des données dans un Data Warehouse structuré selon un schéma en étoile permet de faciliter l'analyse des ventes selon différentes dimensions.

L'automatisation du processus ETL avec Python et Prefect améliore la reproductibilité du traitement, tandis que PostgreSQL/Supabase assure le stockage centralisé des données. Enfin, Power BI permet de transformer les données du Data Warehouse en indicateurs et visualisations destinés à l'analyse et à la prise de décision.

Le projet constitue ainsi une chaîne décisionnelle complète allant de l'acquisition des données jusqu'à leur exploitation analytique.
