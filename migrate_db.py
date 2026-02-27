#!/usr/bin/env python3
"""
Script de migration pour ajouter les colonnes classe_id et first_connection à la table users
"""

import sqlite3
import os

def migrate_database():
    """Ajoute les colonnes manquantes à la table users"""
    
    # Chemin vers la base de données
    db_path = 'instance/sos_thomas.db'
    
    if not os.path.exists(db_path):
        print("Base de données non trouvée. Veuillez d'abord lancer l'application.")
        return
    
    try:
        # Connexion à la base de données
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Vérifier si la colonne classe_id existe
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'classe_id' not in columns:
            print("Ajout de la colonne classe_id...")
            cursor.execute("ALTER TABLE users ADD COLUMN classe_id INTEGER")
            print("Colonne classe_id ajoutee")
        else:
            print("Colonne classe_id existe deja")
        
        if 'first_connection' not in columns:
            print("Ajout de la colonne first_connection...")
            cursor.execute("ALTER TABLE users ADD COLUMN first_connection BOOLEAN DEFAULT 1")
            print("Colonne first_connection ajoutee")
        else:
            print("Colonne first_connection existe deja")
        
        # Créer la table classes si elle n'existe pas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='classes'")
        if not cursor.fetchone():
            print("Création de la table classes...")
            cursor.execute('''
                CREATE TABLE classes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nom TEXT UNIQUE NOT NULL,
                    code TEXT UNIQUE NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Insérer les classes par défaut
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
            
            cursor.executemany("INSERT INTO classes (nom, code) VALUES (?, ?)", classes_data)
            print("Table classes creee avec les classes par defaut")
        else:
            print("Table classes existe deja")
        
        # Valider les changements
        conn.commit()
        print("Migration terminee avec succes!")
        
    except Exception as e:
        print(f"Erreur lors de la migration: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    migrate_database()
