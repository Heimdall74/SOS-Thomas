#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script d'initialisation de la base de données
Crée toutes les tables nécessaires pour l'application SOS Thomas
"""

import os
import sys
from pathlib import Path

# Ajouter le répertoire parent au chemin Python
sys.path.insert(0, str(Path(__file__).parent))

from app import app, db

def init_database():
    """Initialise la base de données avec toutes les tables"""
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
            
        except Exception as e:
            print(f"Erreur lors de l'initialisation de la base de données: {e}")
            sys.exit(1)

if __name__ == "__main__":
    init_database()
