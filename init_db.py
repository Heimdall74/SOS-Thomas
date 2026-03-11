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

from app import app, db, init_classes, create_user_with_classe
from app import User, Event, Classe
from werkzeug.security import generate_password_hash

def import_users_from_json():
    """Importe les utilisateurs depuis le fichier data/users.json"""
    users_file = Path(__file__).parent / 'data' / 'users.json'
    
    if not users_file.exists():
        print("ATTENTION: Fichier data/users.json non trouve, passage de l'import des utilisateurs")
        return
    
    try:
        print("Importation des utilisateurs depuis data/users.json...")
        
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
                print(f"  ATTENTION: Utilisateur '{user_data.get('username')}' existe deja, ignore")
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
            print(f"  OK: Utilisateur '{user_data.get('username')}' importe")
        
        print(f"Importation des utilisateurs terminee: {imported_count} utilisateurs ajoutes")
        
    except Exception as e:
        print(f"ERREUR: Erreur lors de l'importation des utilisateurs: {e}")
        db.session.rollback()

def import_events_from_json():
    """Importe les événements depuis le fichier data/events.json"""
    events_file = Path(__file__).parent / 'data' / 'events.json'
    
    if not events_file.exists():
        print("ATTENTION: Fichier data/events.json non trouve, passage de l'import des evenements")
        return
    
    try:
        print("Importation des evenements depuis data/events.json...")
        
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
                    print("  ATTENTION: Aucun utilisateur trouve, impossible d'importer les evenements")
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
            print(f"  OK: Evenement '{event_data.get('title')}' importe")
        
        print(f"Importation des evenements terminee: {imported_count} evenements ajoutes")
        
    except Exception as e:
        print(f"ERREUR: Erreur lors de l'importation des evenements: {e}")
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
            
            # Initialiser les classes par défaut
            print("\nInitialisation des classes par défaut...")
            init_classes()
            print("OK: Classes initialisées")
            
            # Créer un utilisateur par défaut si aucun n'existe
            user_count = User.query.count()
            if user_count == 0:
                print("Aucun utilisateur trouvé. Création d'un utilisateur par défaut...")
                
                # Récupérer la classe TC2
                tc2_classe = Classe.query.filter_by(code='TC2').first()
                if tc2_classe:
                    # Créer un utilisateur de test
                    test_user = create_user_with_classe(
                        username='thomas',
                        email='thomas@esitc.local',
                        password='test123',
                        classe_id=tc2_classe.id
                    )
                    print(f"OK: Utilisateur de test créé: {test_user.username} (mot de passe: test123)")
                else:
                    print("ATTENTION: Classe TC2 non trouvée")
            else:
                print(f"OK: {user_count} utilisateur(s) déjà présent(s) dans la base")
            
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
            print("\nVous pouvez maintenant lancer l'application avec: python app.py")
            
        except Exception as e:
            print(f"ERREUR: Erreur lors de l'initialisation de la base de données: {e}")
            sys.exit(1)

if __name__ == "__main__":
    init_database()
