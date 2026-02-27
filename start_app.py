#!/usr/bin/env python3
"""
Script de démarrage de l'application SOS Thomas
Vérifie la connexion à la base de données et démarre l'application
"""

import sys
from pathlib import Path

# Ajouter le répertoire parent au chemin Python
sys.path.append(str(Path(__file__).parent))

from app import app, db, Classe, User

def check_and_setup_database():
    """Vérifie la connexion et configure la base de données"""
    
    with app.app_context():
        try:
            # Tester la connexion
            db.engine.execute("SELECT 1")
            print("Connexion à la base de données réussie!")
            
            # Créer les tables si elles n'existent pas
            db.create_all()
            print("Tables vérifiées/créées!")
            
            # Vérifier si des classes existent
            existing_classes = Classe.query.count()
            if existing_classes == 0:
                print("Insertion des classes par défaut...")
                
                classes_data = [
                    ('TC1', 'TC1'), ('TC2', 'TC2'), ('TC3', 'TC3'), ('TC4', 'TC4'), ('TC5', 'TC5'),
                    ('AI1', 'AI1'), ('AI2', 'AI2'), ('AI3', 'AI3'), ('AI4', 'AI4'), ('AI5', 'AI5')
                ]
                
                for nom, code in classes_data:
                    classe = Classe(nom=nom, code=code)
                    db.session.add(classe)
                
                db.session.commit()
                print(f"{len(classes_data)} classes insérées!")
            else:
                print(f"{existing_classes} classes existent déjà")
            
            # Afficher les statistiques
            users_count = User.query.count()
            classes_count = Classe.query.count()
            print(f"Base de données prête: {users_count} utilisateurs, {classes_count} classes")
            
            return True
            
        except Exception as e:
            print(f"Erreur de configuration de la base de données: {e}")
            return False

if __name__ == "__main__":
    print("Démarrage de SOS Thomas...")
    
    if check_and_setup_database():
        print("Démarrage de l'application Flask...")
        app.run(debug=True, host='0.0.0.0', port=5000)
    else:
        print("Impossible de démarrer l'application à cause d'erreurs de base de données.")
        sys.exit(1)
