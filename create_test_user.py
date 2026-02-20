#!/usr/bin/env python3
import json
import uuid
from datetime import datetime
from pathlib import Path
from werkzeug.security import generate_password_hash

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / 'data'
USERS_FILE = DATA_DIR / 'users.json'

# Créer le dossier data s'il n'existe pas
DATA_DIR.mkdir(exist_ok=True)

# Charger les utilisateurs existants
users = {}
if USERS_FILE.exists():
    with open(USERS_FILE, 'r', encoding='utf-8') as f:
        users = json.load(f)

# Créer un utilisateur de test
user_id = str(uuid.uuid4())
users[user_id] = {
    'id': user_id,
    'username': 'test',
    'email': 'test@example.com',
    'password': generate_password_hash('test123'),
    'created_at': datetime.now().isoformat()
}

# Sauvegarder
with open(USERS_FILE, 'w', encoding='utf-8') as f:
    json.dump(users, f, indent=2, ensure_ascii=False)

print("Utilisateur de test créé:")
print("Email: test@example.com")
print("Nom d'utilisateur: test")
print("Mot de passe: test123")
print("Connectez-vous sur: http://localhost:5000/login")
