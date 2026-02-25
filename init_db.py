#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script d'initialisation de la base de données
Crée toutes les tables nécessaires pour l'application SOS Thomas
Importe les données depuis les fichiers JSON
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

# Ajouter le répertoire parent au chemin Python
sys.path.insert(0, str(Path(__file__).parent))

from app import app, db
from app import User, Event
from werkzeug.security import generate_password_hash

def import_users_from_json():
    """Importe les utilisateurs depuis le fichier data/users.json"""
    users_file = Path(__file__).parent / 'data' / 'users.json'
    
    if not users_file.exists():
        print("⚠️  Fichier data/users.json non trouvé, passage de l'import des utilisateurs")
        return
    
    try:
        print("📥 Importation des utilisateurs depuis data/users.json...")
        
        with open(users_file, 'r', encoding='utf-8') as f:
            users_data = json.load(f)
        
        imported_count = 0
        
        for user_data in users_data:
            # Vérifier si l'utilisateur existe déjà
            existing_user = User.query.filter(
                (User.username == user_data.get('username')) | 
                (User.email == user_data.get('email'))
            ).first()
            
            if existing_user:
                print(f"  ⚠️  Utilisateur '{user_data.get('username')}' existe déjà, ignoré")
                continue
            
            # Créer le nouvel utilisateur
            user = User(
                username=user_data.get('username'),
                email=user_data.get('email')
            )
            
            # Hasher le mot de passe si fourni
            password = user_data.get('password', 'default123')
            user.set_password(password)
            
            db.session.add(user)
            db.session.commit()
            imported_count += 1
            print(f"  ✅ Utilisateur '{user_data.get('username')}' importé")
        
        print(f"🎉 Importation des utilisateurs terminée: {imported_count} utilisateurs ajoutés")
        
    except Exception as e:
        print(f"❌ Erreur lors de l'importation des utilisateurs: {e}")
        db.session.rollback()

def import_events_from_json():
    """Importe les événements depuis le fichier data/events.json"""
    events_file = Path(__file__).parent / 'data' / 'events.json'
    
    if not events_file.exists():
        print("⚠️  Fichier data/events.json non trouvé, passage de l'import des événements")
        return
    
    try:
        print("📥 Importation des événements depuis data/events.json...")
        
        with open(events_file, 'r', encoding='utf-8') as f:
            events_data = json.load(f)
        
        imported_count = 0
        
        for event_data in events_data:
            # Récupérer l'utilisateur (premier utilisateur ou user_id spécifié)
            user_id = event_data.get('user_id')
            if not user_id:
                # Prendre le premier utilisateur disponible
                first_user = User.query.first()
                if not first_user:
                    print("  ⚠️  Aucun utilisateur trouvé, impossible d'importer les événements")
                    break
                user_id = first_user.id
            
            # Créer l'événement
            event = Event(
                user_id=user_id,
                date=event_data.get('date'),
                time=event_data.get('time'),
                title=event_data.get('title'),
                category=event_data.get('category')
            )
            
            db.session.add(event)
            db.session.commit()
            imported_count += 1
            print(f"  ✅ Événement '{event_data.get('title')}' importé")
        
        print(f"🎉 Importation des événements terminée: {imported_count} événements ajoutés")
        
    except Exception as e:
        print(f"❌ Erreur lors de l'importation des événements: {e}")
        db.session.rollback()

def init_database():
    """Initialise la base de données avec toutes les tables et importe les données"""
    with app.app_context():
        try:
            print("Création des tables de la base de données...")
            
            # Créer toutes les tables définies dans les modèles
            db.create_all()
            
            print("Base de données initialisée avec succès!")
            print("Tables créées:")
            
            # Lister les tables créées
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            
            for table in sorted(tables):
                print(f"  - {table}")
                
            print(f"\nTotal: {len(tables)} tables créées")
            
            # Importer les données depuis les fichiers JSON
            print("\n" + "="*50)
            print("DÉBUT DE L'IMPORTATION DES DONNÉES")
            print("="*50)
            
            import_users_from_json()
            print()
            import_events_from_json()
            
            print("\n" + "="*50)
            print("INITIALISATION TERMINÉE AVEC SUCCÈS")
            print("="*50)
            
        except Exception as e:
            print(f"❌ Erreur lors de l'initialisation de la base de données: {e}")
            sys.exit(1)

if __name__ == "__main__":
    init_database()
