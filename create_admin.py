#!/usr/bin/env python3
"""
Script pour créer un utilisateur admin pour le développement local
"""

import os
import sys
from pathlib import Path

# Ajouter le répertoire parent au path
sys.path.append(str(Path(__file__).parent))

from app import app, db, User

def create_admin_user():
    """Créer un utilisateur admin pour le développement local"""
    
    with app.app_context():
        # Vérifier si l'utilisateur admin existe déjà
        existing_admin = User.query.filter_by(username='admin').first()
        if existing_admin:
            print("ERREUR: L'utilisateur 'admin' existe déjà avec l'email:", existing_admin.email)
            print("OK: Vous pouvez vous connecter avec:")
            print("   Username: admin")
            print("   Password: admin123")
            return
        
        # Créer l'utilisateur admin
        admin_user = User(
            username='admin',
            email='admin@local.dev'
        )
        admin_user.set_password('admin123')
        
        db.session.add(admin_user)
        db.session.commit()
        
        print("SUCCES: Utilisateur admin créé avec succès!")
        print("Identifiants de connexion:")
        print("   Username: admin")
        print("   Email: admin@local.dev")
        print("   Password: admin123")
        print("")
        print("Lancez l'application avec: python app.py")
        print("Connectez-vous sur: http://localhost:5000")

if __name__ == '__main__':
    create_admin_user()
