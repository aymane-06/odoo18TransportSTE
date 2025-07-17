# Transport Management Module

Module Odoo 18 pour la gestion complète des opérations de transport entre le Maroc et la France. Ce module centralise la gestion des véhicules, des trajets, des chauffeurs, des revenus et des dépenses, permettant un calcul précis de la rentabilité des missions.

## Table des matières

- [Introduction](#introduction)
- [Fonctionnalités](#fonctionnalités)
- [Technologies utilisées](#technologies-utilisées)
- [Installation](#installation)
- [Configuration](#configuration)
- [Utilisation](#utilisation)
- [Structure du module](#structure-du-module)
- [API REST](#api-rest)
- [Tests](#tests)
- [Contribution](#contribution)
- [Auteurs](#auteurs)
- [Licence](#licence)

## Introduction

Le module **transport_management** est une solution complète développée spécifiquement pour les sociétés de transport opérant sur les liaisons internationales Maroc-France. Il offre une gestion centralisée et automatisée de tous les aspects opérationnels et financiers des missions de transport.

## Fonctionnalités

### Gestion des Voyages
- Création et planification des missions de transport
- Affectation automatique des véhicules et chauffeurs
- Suivi en temps réel des statuts (en attente, en cours, terminé)
- Calcul automatique des distances et temps de trajet
- Gestion des arrêts multiples et itinéraires complexes

### Gestion des Véhicules
- Registre complet du parc automobile
- Suivi de l'état technique et documentaire
- Planification et historique des maintenances
- Contrôle des disponibilités et réservations
- Gestion des carburants et consommations

### Gestion des Chauffeurs
- Profils détaillés des conducteurs
- Affectation intelligente selon les compétences
- Suivi des trajets et performances
- Gestion des rapports d'incidents
- Contrôle des temps de conduite et repos

### Suivi Financier
- Saisie des revenus par mission
- Enregistrement détaillé des dépenses
- Calcul automatique de la rentabilité
- Analyse des coûts par type et période
- Prévisions budgétaires

### Tableaux de Bord
- Indicateurs clés de performance (KPI)
- Analyse des coûts, revenus et marges
- Graphiques interactifs en temps réel
- Rapports personnalisables
- Alertes et notifications

### Sécurité et Accès
- Gestion des rôles utilisateurs
- Droits d'accès granulaires
- Profils prédéfinis (Administrateur, Gestionnaire, Chauffeur)
- Audit trail complet
- Sécurisation des données sensibles

### Intégration Mobile
- API REST complète
- Synchronisation avec application Flutter
- Accès temps réel pour les chauffeurs
- Géolocalisation et suivi GPS
- Mode hors ligne disponible

## Technologies utilisées

- **Framework** : Odoo 18 (Python 3.12+)
- **Interface** : XML, QWeb, JavaScript
- **Base de données** : PostgreSQL 17
- **Frontend interactif** : OWL (Odoo Web Library)
- **API** : REST avec authentification JWT
- **Versioning** : Git
- **Conteneurisation** : Docker & Docker Compose

## Installation

### Prérequis

- Odoo 18 installé et configuré
- PostgreSQL 17 ou supérieur
- Python 3.12 ou supérieur
- Docker et Docker Compose (optionnel)

### Installation du module

1. **Copier le module dans le répertoire addons**
   ```bash
   cp -r transport_management /path/to/odoo/addons/
   ```

2. **Démarrer Odoo avec Docker Compose**
   ```bash
   docker-compose up -d
   ```

3. **Accéder à l'interface Odoo**
   - Ouvrir http://localhost:10018
   - Se connecter avec les identifiants administrateur

4. **Activer le mode développeur**
   - Aller dans Paramètres → Activer le mode développeur

5. **Mettre à jour la liste des modules**
   - Apps → Mettre à jour la liste des Apps

6. **Installer le module**
   - Rechercher "Transport Management"
   - Cliquer sur "Installer"

## Configuration

### Configuration initiale

1. **Créer les groupes d'utilisateurs**
   - Aller dans Paramètres → Utilisateurs et sociétés → Groupes
   - Vérifier la présence des groupes Transport

2. **Configurer les données de base**
   - Véhicules : Ajouter votre parc automobile
   - Chauffeurs : Enregistrer les conducteurs
   - Itinéraires : Définir les routes principales

3. **Paramétrer les coûts**
   - Coûts kilométriques par type de véhicule
   - Tarifs standards par destination
   - Frais fixes et variables

## Utilisation

### Création d'un voyage

1. Aller dans **Transport → Voyages**
2. Cliquer sur **Nouveau**
3. Renseigner les informations :
   - Origine et destination
   - Date et heure de départ
   - Type de marchandise
   - Client
4. Affecter véhicule et chauffeur
5. Confirmer le voyage

### Suivi financier

1. **Saisie des revenus**
   - Transport → Revenus → Nouveau
   - Lier au voyage correspondant

2. **Enregistrement des dépenses**
   - Transport → Dépenses → Nouveau
   - Catégoriser les coûts

3. **Analyse de rentabilité**
   - Transport → Rapports → Analyse des profits
   - Filtrer par période ou voyage

## Structure du module

```
transport_management/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   ├── trip.py                    # Gestion des voyages
│   ├── fleet_vehicle.py           # Extension véhicules
│   ├── hr_employee.py             # Extension employés
│   ├── trip_revenue.py            # Gestion des revenus
│   ├── trip_expense.py            # Gestion des dépenses
│   └── driver_report.py           # Rapports chauffeurs
├── views/
│   ├── menus.xml                  # Menus principaux
│   ├── trip_views.xml             # Vues des voyages
│   ├── fleet_vehicle_views.xml    # Vues des véhicules
│   ├── hr_employee_views.xml      # Vues des employés
│   ├── trip_revenue_views.xml     # Vues des revenus
│   ├── trip_expense_views.xml     # Vues des dépenses
│   └── transport_dashboard_views.xml # Tableau de bord
├── security/
│   ├── ir.model.access.csv        # Droits d'accès
│   ├── security.xml               # Groupes utilisateurs
│   └── driver_report_security.xml # Sécurité rapports
├── controllers/
│   ├── __init__.py
│   └── controllers.py             # API REST
├── data/
│   ├── transport_products.xml     # Produits transport
│   └── trip_data.xml              # Données de base
├── demo/
│   ├── demo_data.xml              # Données de démonstration
│   └── driver_report_demo.xml     # Démo rapports
├── reports/
│   ├── __init__.py
│   ├── trip_report.xml            # Rapport des voyages
│   ├── driver_report.xml          # Rapport des chauffeurs
│   └── profit_analysis_report.xml # Analyse rentabilité
├── static/
│   ├── description/
│   │   └── icon.png               # Icône du module
│   └── src/
│       ├── css/
│       ├── js/
│       └── xml/
└── i18n/
    ├── fr.po                      # Traduction française
    └── transport_management.pot   # Template traduction
```

## API REST

Le module expose une API REST complète pour l'intégration avec des applications externes.

### Endpoints principaux

- `GET /api/trips` - Liste des voyages
- `POST /api/trips` - Création d'un voyage
- `GET /api/trips/{id}` - Détails d'un voyage
- `PUT /api/trips/{id}` - Mise à jour d'un voyage
- `GET /api/vehicles` - Liste des véhicules
- `GET /api/drivers` - Liste des chauffeurs

### Authentification

L'API utilise l'authentification JWT d'Odoo. Inclure le token dans les headers :

```bash
Authorization: Bearer <token>
```

### Exemple d'utilisation

```python
import requests

# Authentification
response = requests.post('/web/session/authenticate', {
    'db': 'transport_db',
    'login': 'admin',
    'password': 'password'
})

# Récupération des voyages
trips = requests.get('/api/trips', headers={
    'Authorization': f'Bearer {token}'
})
```

## Tests

Le module inclut une suite de tests complète pour garantir la qualité du code.

### Tests unitaires

```bash
# Exécuter tous les tests
odoo-bin -d test_db -i transport_management --test-enable

# Tests spécifiques
odoo-bin -d test_db --test-tags transport_management
```

### Tests de régression

```bash
# Tests des modèles
python -m pytest tests/test_models.py

# Tests des contrôleurs
python -m pytest tests/test_controllers.py

# Tests des vues
python -m pytest tests/test_views.py
```

### Couverture de code

```bash
# Générer un rapport de couverture
coverage run --source=transport_management odoo-bin -d test_db -i transport_management --test-enable
coverage report -m
```

## Contribution

Les contributions sont les bienvenues ! Merci de suivre ces étapes :

1. Fork le projet
2. Créer une branche pour votre fonctionnalité (`git checkout -b feature/nouvelle-fonctionnalite`)
3. Commiter vos changements (`git commit -am 'Ajout d'une nouvelle fonctionnalité'`)
4. Pousser vers la branche (`git push origin feature/nouvelle-fonctionnalite`)
5. Créer une Pull Request

### Standards de développement

- Respecter les conventions PEP 8 pour Python
- Documenter les fonctions et classes
- Ajouter des tests pour les nouvelles fonctionnalités
- Utiliser des noms de variables explicites
- Suivre les bonnes pratiques Odoo

## Auteurs

- **Aymane Himame** - Développeur full stack
  - Email : aymane.himame@gmail.com
  - GitHub : [@aymane-himame](https://github.com/aymane-himame)

- **LeanSoft** - Équipe d'encadrement et supervision




**Transport Management Module** - Développé avec Odoo 18 pour optimiser les opérations de transport international.
