# Spotify Controller - Instructions de Configuration

## 📋 Prérequis

- Python 3.11 ou supérieur
- Compte Spotify Premium (obligatoire pour le contrôle de lecture)
- Compte Spotify Developer

## 🚀 Installation

### 1. Cloner le projet

```bash
git clone <votre-repo>
cd sos-thomas-python
```

### 2. Installer les dépendances

```bash
pip install flask flask-wtf requests python-dotenv
```

### 3. Créer une application Spotify Developer

1. Allez sur [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Connectez-vous avec votre compte Spotify
3. Cliquez sur "Create an App"
4. Remplissez les informations :
   - **App name**: SOS Thomas Music Controller
   - **App description**: Application web pour contrôler Spotify
   - **Website**: `http://localhost:5000`
   - **Redirect URI**: `http://localhost:5000/callback`
5. Acceptez les termes et conditions
6. Notez votre **Client ID** et **Client Secret**

### 4. Configurer les variables d'environnement

Créez un fichier `.env` à la racine du projet :

```env
SPOTIFY_CLIENT_ID=votre_client_id_ici
SPOTIFY_CLIENT_SECRET=votre_client_secret_ici
SPOTIFY_REDIRECT_URI=http://localhost:5000/callback
```

Ou exportez les variables directement :

```bash
export SPOTIFY_CLIENT_ID="votre_client_id_ici"
export SPOTIFY_CLIENT_SECRET="votre_client_secret_ici"
export SPOTIFY_REDIRECT_URI="http://localhost:5000/callback"
```

## 🏃‍♂️ Lancer l'application

### Développement

```bash
python app.py
```

L'application sera disponible sur `http://localhost:5000`

## 📱 Utilisation

1. **Connectez-vous** à l'application SOS Thomas
2. Allez dans la page **Musique**
3. Cliquez sur **"Se connecter à Spotify"**
4. Autorisez l'application sur la page Spotify
5. Vous serez redirigé vers l'application avec le lecteur fonctionnel

## 🎛️ Fonctionnalités disponibles

- **Play/Pause**: Contrôler la lecture
- **Piste suivante**: Passer à la musique suivante
- **Piste précédente**: Revenir à la musique précédente
- **Informations en temps réel**: Titre, artiste, album, pochette
- **Barre de progression**: Suivi de la lecture
- **Mise à jour automatique**: Toutes les 5 secondes

## ⚠️ Limites techniques et légales

### Limites techniques

1. **Spotify Premium requis**: Le contrôle de lecture nécessite un abonnement Premium
2. **Appareil actif**: Spotify doit être ouvert sur au moins un appareil
3. **Rate limits**: L'API Spotify limite le nombre de requêtes
4. **Token expiration**: Les tokens expirent après 1 heure (rafraîchissement automatique)

### Limites légales

1. **Respect des CGU**: L'application respecte les conditions d'utilisation de Spotify
2. **Pas de scraping**: Utilisation uniquement des API officielles
3. **Pas de téléchargement**: L'application ne permet pas de télécharger de musique
4. **Usage personnel**: Destiné à un usage personnel et non commercial

## 🔧 Configuration avancée

### Modifier le port

```python
if __name__ == '__main__':
    app.run(debug=True, port=8080)  # Changez le port ici
```

### Modifier les scopes OAuth

Dans `app.py`, modifiez la fonction `get_spotify_auth_url()`:

```python
'scope': 'user-read-playback-state user-modify-playback-state user-read-currently-playing user-read-email'
```

### Personnaliser l'interface

Modifiez le template `templates/musique.html` pour changer l'apparence du lecteur.

## 🐛 Dépannage

### Problèmes courants

1. **"Aucune lecture en cours"**
   - Vérifiez que Spotify est ouvert sur un appareil
   - Lancez une lecture sur Spotify

2. **"Session expirée"**
   - Reconnectez-vous à Spotify
   - Vérifiez votre connexion internet

3. **"Token expiré"**
   - L'application essaie de rafraîchir automatiquement
   - Si ça échoue, reconnectez-vous

4. **Erreur de callback**
   - Vérifiez que le redirect URI correspond exactement
   - Assurez-vous que `http://localhost:5000/callback` est ajouté dans votre app Spotify

### Logs

Pour activer les logs détaillés :

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📊 Structure du projet

```
sos-thomas-python/
├── app.py                    # Application Flask principale
├── templates/
│   ├── base.html             # Template de base
│   ├── musique.html          # Page Spotify
│   └── ...                  # Autres templates
├── static/
│   └── uploads/             # Fichiers uploadés
├── data/
│   ├── users.json           # Utilisateurs
│   └── profiles.json        # Profils
├── .env                     # Variables d'environnement
└── README_SPOTIFY.md        # Ce fichier
```

## 🔐 Sécurité

- Les tokens sont stockés en session Flask
- Les clés API ne sont jamais exposées côté client
- Utilisation de HTTPS recommandé en production

## 📞 Support

Pour toute question ou problème :

1. Vérifiez les logs de l'application
2. Consultez la [documentation Spotify Web API](https://developer.spotify.com/documentation/web-api/)
3. Vérifiez votre configuration dans le dashboard Spotify Developer

---

**Note importante**: Cette application est à but éducatif et personnel. Respectez toujours les conditions d'utilisation de Spotify et les droits d'auteur.
