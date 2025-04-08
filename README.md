# mspr6.1

# MSPr6.1 - Pipeline de Données & API

Ce projet, disponible sur [GitHub](https://github.com/MAHRAZ-Oussama/mspr6.1.git), a pour objectif de télécharger, nettoyer et stocker des données provenant de Kaggle dans une base de données PostgreSQL, puis de créer une API permettant d’exécuter des requêtes SQL et de visualiser les résultats. Ce dépôt est destiné aux membres de l’équipe utilisant macOS, Windows ou d'autres environnements.

## Table des matières

- [Vue d'ensemble](#vue-densemble)
- [Prérequis](#prerequis)
- [Installation et Configuration](#installation-et-configuration)
  - [1. Clonage du projet](#1-clonage-du-projet)
  - [2. Installation de Python et des dépendances](#2-installation-de-python-et-des-dépendances)
  - [3. Configuration de l'API Kaggle](#3-configuration-de-lapi-kaggle)
  - [4. Configuration de PostgreSQL et du fichier `.env`](#4-configuration-de-postgresql-et-du-fichier-env)
- [Pipeline de Données](#pipeline-de-données)
  - [Téléchargement et nettoyage](#téléchargement-et-nettoyage)
  - [Stockage dans PostgreSQL](#stockage-dans-postgresql)
- [API pour exécuter des requêtes SQL](#api-pour-exécuter-des-requêtes-sql)
- [Utilisation Multi-Plateforme (macOS & Windows)](#utilisation-multi-plateforme-macos--windows)
- [Sécurité et Bonnes Pratiques](#sécurité-et-bonnes-pratiques)
- [Dépannage](#dépannage)
- [Auteur / Équipe](#-auteur--équipe)

## Vue d'ensemble

Le projet se structure autour de trois modules principaux :

1. **Téléchargement et Nettoyage des Données**  
   - Téléchargement des datasets via l’API Kaggle.
   - Nettoyage et filtrage des données (conservation du dernier jour du mois par pays).
   - Ajout de la colonne `Total_Gueris`, calculée comme la différence entre les cas cumulés et les décès cumulés.

2. **Stockage dans PostgreSQL**  
   - Conversion des fichiers nettoyés en tables SQL via SQLAlchemy.
   - Utilisation de pandas pour le chargement et l’insertion des données dans la base.

3. **API d’Accès aux Données**  
   - Mise en place d’une API REST avec FastAPI, permettant d’exécuter des requêtes SQL.
   - Une route `/query` qui retourne les résultats sous forme de JSON.

## Prérequis

- **Python** (version 3.6 ou ultérieure)
- **PostgreSQL**
- **Git** (pour cloner le dépôt, si nécessaire)

### Bibliothèques Python

Les bibliothèques principales utilisées sont :
- `pandas`
- `kaggle`
- `python-dotenv`
- `SQLAlchemy`
- `psycopg2-binary`
- `fastapi`
- `uvicorn`

## Installation et Configuration

### 1. Clonage du projet

Clonez le dépôt dans votre répertoire de travail :

```bash
git clone https://github.com/MAHRAZ-Oussama/mspr6.1.git
cd mspr6.1
