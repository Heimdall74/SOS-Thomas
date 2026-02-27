#!/usr/bin/env python3
"""
Script de migration pour PostgreSQL - Création des tables et insertion des données initiales
"""

import os
import sys
from pathlib import Path

# Ajouter le répertoire parent au chemin Python
sys.path.append(str(Path(__file__).parent))

from app import app, db, Classe, User

def migrate_postgres():
    """Crée les tables et insère les données initiales pour PostgreSQL"""
    
    with app.app_context():
        try:
            print("Creation des tables dans PostgreSQL...")
            
            # Créer toutes les tables
            db.create_all()
            print("Tables creees avec succes!")
            
            # Vérifier si des classes existent déjà
            existing_classes = Classe.query.count()
            if existing_classes == 0:
                print("Insertion des classes par defaut...")
                
                # Classes par défaut
                classes_data = [
                    ('TC1', 'TC1'),
                    ('TC2', 'TC2'),
                    ('TC3', 'TC3'),
                    ('TC4', 'TC4'),
                    ('TC5', 'TC5'),
                    ('AI1', 'AI1'),
                    ('AI2', 'AI2'),
                    ('AI3', 'AI3'),
                    ('AI4', 'AI4'),
                    ('AI5', 'AI5')
                ]
                
                for nom, code in classes_data:
                    classe = Classe(nom=nom, code=code)
                    db.session.add(classe)
                
                db.session.commit()
                print(f"{len(classes_data)} classes inserees avec succes!")
            else:
                print(f"{existing_classes} classes existent deja dans la base de donnees.")
            
            # Vérifier la connexion
            users_count = User.query.count()
            print(f"Utilisateurs existants: {users_count}")
            classes_count = Classe.query.count()
            print(f"Classes existantes: {classes_count}")
            
            print("Migration PostgreSQL terminee avec succes!")
            
        except Exception as e:
            print(f"Erreur lors de la migration: {e}")
            db.session.rollback()
            raise

if __name__ == "__main__":
    migrate_postgres()
