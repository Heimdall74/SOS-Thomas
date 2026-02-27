#!/usr/bin/env python3
"""
Script de test pour vérifier le login
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from app import app, db, User
from werkzeug.security import check_password_hash

def test_login():
    """Tester le processus de login manuellement"""
    
    with app.app_context():
        print("=== Test de login ===")
        
        # 1. Vérifier que l'utilisateur admin existe
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            print("❌ L'utilisateur admin n'existe pas")
            return
        
        print("OK Utilisateur trouvé:", admin.username, "(", admin.email, ")")
        
        # 2. Tester le mot de passe
        if check_password_hash(admin.password_hash, 'admin123'):
            print("OK Mot de passe correct")
        else:
            print("ERREUR Mot de passe incorrect")
            return
        
        # 3. Simuler une session
        from flask import session
        with app.test_request_context():
            session['user_id'] = admin.id
            session['username'] = admin.username
            session['email'] = admin.email
            
            print("OK Session créée: user_id=", session.get('user_id'))
            print("OK Données de session:", dict(session))
        
        print("\n=== Test terminé ===")
        print("Si ce test passe, le problème vient probablement du frontend ou des cookies")

if __name__ == '__main__':
    test_login()
