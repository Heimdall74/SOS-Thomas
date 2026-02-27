# Configuration Base de Données - SOS Thomas

## Configuration PostgreSQL

L'application est maintenant configurée pour utiliser une base de données PostgreSQL en production et SQLite en développement.

### Variables d'environnement

Le fichier `.env` contient la configuration de la base de données :

```env
# Configuration Base de données
DATABASE_URL=postgresql://alexandre:WHcG9LRIKYxZnB94ZQuoGJWaEeSz6YPF@dpg-d6c91arh46gs73e46qag-a.frankfurt-postgres.render.com/dbst_na2t
```

### Fonctionnement

L'application bascule automatiquement entre :
- **Développement local** : SQLite (`sos_thomas.db`)
- **Production (Render)** : PostgreSQL via `DATABASE_URL`

Le code dans `app.py` gère cette bascule :

```python
if os.environ.get("DATABASE_URL"):
    # Mode production (Render/Heroku/etc.)
    DATABASE_URL = os.environ.get("DATABASE_URL")
    app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
else:
    # Mode développement local
    DATABASE_URL = "sqlite:///sos_thomas.db"
    app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
```

### Installation des dépendances

```bash
pip install -r requirements.txt
```

Les dépendances principales pour la base de données :
- `Flask-SQLAlchemy==3.0.5`
- `psycopg2-binary==2.9.7`
- `python-dotenv==1.0.0`

### Initialisation de la base de données

Pour créer les tables sur PostgreSQL :

```bash
python init_db.py
```

### Vérification de la connexion

Pour tester la connexion à la base de données PostgreSQL :

```python
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
database_url = os.environ.get("DATABASE_URL")

try:
    conn = psycopg2.connect(database_url)
    print("Connexion réussie!")
    conn.close()
except Exception as e:
    print(f"Erreur: {e}")
```

### Tables créées

L'application crée automatiquement 15 tables :
- `users` - Utilisateurs
- `events` - Événements agenda
- `projects` - Projets
- `tasks` - Tâches
- `project_tasks` - Tâches de projets
- `notes` - Notes
- `accounts` - Comptes
- `mails` - Emails
- `photos` - Photos
- `calls` - Appels
- `messages` - Messages
- `links` - Liens
- `project_members` - Membres de projets
- `project_files` - Fichiers de projets
- `folders` - Dossiers

### Déploiement sur Render

1. Assurez-vous que la variable d'environnement `DATABASE_URL` est configurée sur Render
2. L'application utilisera automatiquement PostgreSQL en production
3. Les tables seront créées automatiquement au premier démarrage

### Développement local

Pour utiliser SQLite localement (par défaut) :
- Commentez ou supprimez la ligne `DATABASE_URL` du fichier `.env`
- L'application utilisera automatiquement `sqlite:///sos_thomas.db`

### Migration de données

Si vous avez des données dans SQLite et voulez les migrer vers PostgreSQL :

1. Exportez les données depuis SQLite
2. Importez-les dans PostgreSQL en utilisant les modèles SQLAlchemy
3. Le script `init_db.py` peut être adapté pour cette migration
