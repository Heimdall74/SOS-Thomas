#!/usr/bin/env python3
"""
Test de connexion à la base de données PostgreSQL
"""

from app import app, db, Classe, User

with app.app_context():
    try:
        classes_count = Classe.query.count()
        users_count = User.query.count()
        print(f'Classes: {classes_count}, Users: {users_count}')
        print('Connexion à PostgreSQL réussie!')
    except Exception as e:
        print(f'Erreur de connexion: {e}')
