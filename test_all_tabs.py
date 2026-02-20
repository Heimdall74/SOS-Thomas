import urllib.request
import urllib.parse
import json
import http.cookiejar

# Configuration
base_url = "http://localhost:5000"

# Créer un gestionnaire de cookies pour maintenir la session
cookie_jar = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie_jar))
urllib.request.install_opener(opener)

def login():
    """Se connecter à l'application"""
    login_url = f"{base_url}/login"
    
    # Récupérer la page de login pour obtenir le token CSRF
    response = opener.open(login_url)
    page_content = response.read().decode('utf-8')
    
    # Extraire le token CSRF
    import re
    csrf_match = re.search(r'name="csrf_token".*?value="([^"]+)"', page_content)
    if not csrf_match:
        print("Impossible de trouver le token CSRF")
        return False
    
    csrf_token = csrf_match.group(1)
    
    # Préparer les données de connexion
    login_data = {
        'username': 'admin',
        'password': 'admin123',
        'csrf_token': csrf_token
    }
    
    # Envoyer la requête de connexion
    data = urllib.parse.urlencode(login_data).encode('utf-8')
    req = urllib.request.Request(login_url, data=data)
    
    try:
        response = opener.open(req)
        print("Connexion reussie")
        return True
    except Exception as e:
        print(f"Erreur de connexion: {e}")
        return False

def test_all_tabs(project_id):
    """Tester que tous les onglets sont accessibles"""
    url = f"{base_url}/project/{project_id}"
    
    try:
        req = urllib.request.Request(url)
        response = opener.open(req)
        page_content = response.read().decode('utf-8')
        
        print("Verification de tous les onglets...")
        
        # Vérifier que tous les onglets existent
        tabs = [
            ("overview", "Vue d'ensemble"),
            ("tasks", "Tâches"),
            ("files", "Fichiers"),
            ("notes", "Notes"),
            ("members", "Membres"),
            ("activity", "Activité")
        ]
        
        all_good = True
        for tab_id, tab_name in tabs:
            if f'id="' + tab_id + '"' in page_content:
                print(f"✅ Onglet '{tab_name}' - Present")
            else:
                print(f"❌ Onglet '{tab_name}' - Manquant")
                all_good = False
        
        # Vérifier que la fonction switchTab existe
        if "function switchTab" in page_content:
            switchTab_count = page_content.count("function switchTab")
            if switchTab_count == 1:
                print("✅ Fonction switchTab presente (pas de conflit)")
            else:
                print(f"⚠️ {switchTab_count} fonctions switchTab (conflit possible)")
        else:
            print("❌ Fonction switchTab manquante")
            all_good = False
        
        return all_good
        
    except Exception as e:
        print(f"Erreur lors de la verification: {e}")
        return False

# Test complet
print("Test de tous les onglets de la page de details du projet...")

if login():
    project_id = "6abfa043-b440-4134-9750-dfd595d3964c"
    
    print(f"\\nTest de la page {project_id}...")
    if test_all_tabs(project_id):
        print("\\n✅ Tous les onglets sont presents!")
        print("\\n📋 Instructions pour tester:")
        print("1. Allez sur la page de details du projet")
        print("2. Testez chaque onglet:")
        print("   - Vue d'ensemble (deja active)")
        print("   - Cliquez sur 'Tâches'")
        print("   - Cliquez sur 'Fichiers'")
        print("   - Cliquez sur 'Notes'")
        print("   - Cliquez sur 'Membres'")
        print("   - Cliquez sur 'Activité'")
        print("3. Tous les onglets devraient etre fonctionnels")
    else:
        print("\\n❌ Certains onglets sont manquants")

print("\\nTest termine")
