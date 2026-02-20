#!/usr/bin/env python3
"""
Script pour créer un utilisateur administrateur par défaut pour SOS Thomas
"""

import json
import os
from pathlib import Path
from datetime import datetime
import uuid
from werkzeug.security import generate_password_hash

# Configuration
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / 'data'
USERS_FILE = DATA_DIR / 'users.json'

def create_default_admin():
    """Crée un utilisateur administrateur par défaut"""
    
    # Créer le dossier data s'il n'existe pas
    os.makedirs(DATA_DIR, exist_ok=True)
    
    # Informations de l'administrateur par défaut
    admin_user = {
        'id': str(uuid.uuid4()),
        'username': 'admin',
        'email': 'admin@sosthomas.local',
        'password': generate_password_hash('admin123'),
        'created_at': datetime.now().isoformat()
    }
    
    # Charger les utilisateurs existants ou créer un nouveau dictionnaire
    users = {}
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            users = json.load(f)
    
    # Ajouter l'administrateur s'il n'existe pas déjà
    if not any(user['username'] == 'admin' for user in users.values()):
        users[admin_user['id']] = admin_user
        
        # Sauvegarder les utilisateurs
        with open(USERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(users, f, indent=2, ensure_ascii=False)
        
        print("Utilisateur administrateur cree avec succes !")
        print("\nIdentifiants de connexion :")
        print("   Nom d'utilisateur : admin")
        print("   Mot de passe      : admin123")
        print("   Email            : admin@sosthomas.local")
        print("\nVous pouvez maintenant vous connecter avec ces identifiants.")
        print("\nPensez a changer le mot de passe apres votre premiere connexion !")
        
    else:
        print("Un utilisateur 'admin' existe deja.")
        print("Utilisez les identifiants suivants :")
        print("   Nom d'utilisateur : admin")
        print("   Mot de passe      : admin123")

if __name__ == "__main__":
    create_default_admin()
