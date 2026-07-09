# 🗂️ Le dilemme de l'architecte Data — ETL vs ELT

> Projet académique de Data Engineering — Comparaison théorique et pratique des architectures ETL et ELT à l'ère du Big Data.

## 👥 Auteurs

| Nom | Rôle |
|---|---|
| **Imane Alouani** | Co-auteure — Recherche, rédaction du rapport, conception de la présentation, développement du pipeline ETL |
| **Marouane Daouki** | Co-auteur — Recherche, études de cas, développement du pipeline ELT, préparation à la soutenance |

**Encadrante :**  Monsieur Bentaib Mohssine
**Établissement :** Master Intelligence Artificielle / Data Engineering — Faculté des Sciences Ben M'Sik, Université Hassan II de Casablanca
**Année universitaire :** 2025 – 2026

---

## 📖 Contexte du projet

Ce projet répond au sujet 3 de soutenance de Data Engineering : *"Le dilemme de l'architecte Data : Choisir entre ETL et ELT à l'ère du Big Data"*. Il combine :

1. Une **recherche documentaire** sur les tendances actuelles ETL/ELT, les architectures Lakehouse/Zero-ETL/Data Mesh, et des cas réels d'entreprises (2025-2026)
2. Un **rapport académique complet** (Word) structuré en 9 sections : contexte Big Data, fondamentaux, comparaison technique, écosystème d'outils, études de cas, grille de décision, discussion critique, conclusion argumentée, bibliographie
3. Une **démonstration pratique exécutable** : deux mini-pipelines de données (ETL et ELT) codés et testés sur un jeu de données commun
4. Une **présentation PowerPoint** (22 slides avec notes de présentateur) pour la soutenance orale
5. Une **préparation à la soutenance** : questions de jury anticipées avec éléments de réponse, plan de timing

---

## 🎯 Objectif de la démonstration pratique

Illustrer concrètement, par le code, la différence architecturale entre :

- **ETL (Extract → Transform → Load)** : la donnée est nettoyée entièrement en mémoire (Python/Pandas) **avant** d'être chargée dans l'entrepôt cible.
- **ELT (Extract → Load → Transform)** : la donnée brute est chargée immédiatement dans l'entrepôt, et **toute la transformation se fait ensuite en SQL**, à l'intérieur même du moteur de calcul (DuckDB), à la manière de dbt (couches raw → staging → mart).

Les deux pipelines partent du **même fichier CSV brut** pour garantir une comparaison équitable.

---

## 📂 Structure du dépôt

ETL_ELT_Demo/
├── generate_data.py       # Génère le jeu de données brut et "sale" (raw_orders.csv)
├── etl_pipeline.py        # Pipeline ETL : nettoyage Python/Pandas → chargement SQLite
├── elt_pipeline.py        # Pipeline ELT : chargement brut DuckDB → transformation SQL
├── README.md               # Ce fichier
├── raw_orders.csv          # (généré) jeu de données source, 20 000 lignes
├── etl_warehouse.db        # (généré) résultat du pipeline ETL
├── etl_metrics.txt         # (généré) métriques du pipeline ETL
├── elt_warehouse.duckdb    # (généré) résultat du pipeline ELT
└── elt_metrics.txt         # (généré) métriques du pipeline ELT

---

## ⚙️ Stack technique

| Composant | Technologie |
|---|---|
| Génération de données | Python (csv, random, datetime) |
| Pipeline ETL | Python, Pandas, NumPy, SQLite3 |
| Pipeline ELT | Python, DuckDB (SQL) |
| Rapport académique | Word (.docx) |
| Présentation | PowerPoint (.pptx) |

---

## 🚀 Installation et exécution

### Prérequis
- Python 3.9 ou supérieur

### 1. Installer les dépendances
```bash
python -m pip install pandas numpy duckdb
```

### 2. Exécuter les scripts dans l'ordre
```bash
python generate_data.py    # étape 1 : génère raw_orders.csv (20 000 lignes)
python etl_pipeline.py     # étape 2 : exécute le pipeline ETL
python elt_pipeline.py     # étape 3 : exécute le pipeline ELT
```

Chaque script affiche ses métriques dans le terminal et les enregistre dans un fichier `.txt` correspondant.

---

## 📊 Jeu de données

`generate_data.py` produit 20 000 commandes e-commerce **volontairement imparfaites**, pour simuler un export réel de système transactionnel :

- 3 formats de dates différents dans la même colonne
- ~3% de doublons volontaires
- Valeurs manquantes (prix, remises)
- Casse incohérente (villes, catégories, moyens de paiement)
- Quantités aberrantes (valeurs négatives)
- Emails invalides ou vides (test de conformité RGPD)

---

## 📈 Résultats mesurés

| Métrique | Pipeline ETL (Pandas → SQLite) | Pipeline ELT (DuckDB → SQL) |
|---|---|---|
| Lignes brutes en entrée | 20 000 | 20 000 |
| Lignes conservées après transformation | 15 912 | 15 912 *(résultat identique — validation croisée)* |
| Temps total du pipeline | ≈ 3,00 s | ≈ 0,32 s |
| Lignes de code (hors commentaires) | ≈ 56 | ≈ 68 |

📌 Analyse complète de ces résultats dans le rapport (section 3.2) et la présentation (slides 18–20).

### ⚠️ Limites honnêtes de cette démonstration
- Échelle réduite (20 000 lignes) : ne reproduit pas les effets réels du Big Data à grande échelle (partitionnement, cluster multi-nœud)
- Environnement 100% local (SQLite, DuckDB embarqués) — non représentatif d'un entrepôt cloud de production facturé à l'usage
- L'écart de vitesse (~9x) s'explique surtout par le parsing de dates ligne à ligne en Python pur vs le moteur vectorisé de DuckDB — un ETL optimisé (Spark, calcul vectorisé) réduirait fortement cet écart
- Le nombre de lignes de code est un indicateur grossier : il ne capture ni lisibilité, ni testabilité, ni maintenabilité à long terme

---

## 🎓 Conclusion du projet

L'ELT constitue le choix par défaut le plus rationnel pour un projet cloud-natif en 2026, mais l'ETL reste pertinent lorsque la conformité réglementaire (RGPD, HIPAA), l'existant on-premise, ou des traitements hors SQL (feature engineering ML/NLP) l'exigent. La recommandation finale est une **architecture hybride assumée** : ELT par défaut, ETL ciblé sur les étapes où la gouvernance l'impose.

---

## 📝 Licence

Projet académique réalisé dans le cadre du Master Intelligence Artificielle / Data Engineering — Université Hassan II de Casablanca. Usage pédagogique.

## 🙏 Remerciements
Merci a toute personne qui a contribuer a realiser ce projet.
