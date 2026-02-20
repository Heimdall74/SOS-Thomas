# SOS Thomas - Application Web Python/Flask

Une application web complète pour la gestion personnelle développée avec Python Flask, proposant toutes les fonctionnalités demandées.

## 🚀 Fonctionnalités

### 📋 Dashboard général
- Vue d'ensemble avec icônes cliquables pour chaque fonctionnalité
- Statistiques rapides et dernières activités
- Timer intégré en temps réel
- Navigation intuitive

### 📅 Agenda
- Gestion des événements avec dates et titres
- Affichage chronologique
- Suppression des événements

### 📊 Suivi de projets
- Création de projets avec statuts (en cours, terminé, en attente)
- Affichage en grille avec badges de statut
- Gestion complète du cycle de vie des projets

### ✅ Suivi de tâches
- Tâches avec priorités (basse, moyenne, haute)
- Système de cases à cocher pour marquer les tâches comme terminées
- Indicateurs visuels des priorités

### 📝 Bloc notes
- Notes avec titre et contenu détaillé
- Affichage en grille avec aperçu
- Visualisation complète des notes

### 👥 Suivi des comptes
- Gestion des comptes avec nom et email
- Liens hypertextes vers les détails
- Intégration complète avec le système de mails

### 📧 Mail inter compte
- Envoi de mails entre les comptes enregistrés
- Sélection des expéditeurs et destinataires
- Historique complet des communications

### 📸 Gestion de médias
- **Photos** : Upload et affichage avec aperçu
- **Appels** : Suivi des appels avec contacts et timestamps
- **Messages** : Gestion des messages personnels

### 🤝 Mode réunion
- Prise de notes structurées pendant les réunions
- Gestion des dates et heures
- Historique détaillé des réunions

### 🎵 Système musical Spotify
- Interface simulée de connexion Spotify
- Contrôles de lecture complets
- Barre de progression et gestion des pistes

### 🔗 Liens web
- Gestion des liens favoris
- Ouverture dans un nouvel onglet
- Organisation par titre et URL

### 🎨 Personnalisation
- Système de thèmes avec plusieurs palettes de couleurs
- Changement dynamique des couleurs de l'interface

### ⏱️ Timer
- Timer permanent en format HH:MM:SS
- Affichage dans la barre de navigation

## 🛠️ Installation

### Prérequis
- Python 3.7 ou supérieur
- pip (gestionnaire de paquets Python)

### Étapes d'installation

1. **Cloner ou télécharger le projet**
   ```bash
   cd Z:/TC2/Dev/sos-thomas-python
   ```

2. **Créer un environnement virtuel (recommandé)**
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Installer les dépendances**
   ```bash
   pip install -r requirements.txt
   ```

4. **Lancer l'application**
   ```bash
   python app.py
   ```

5. **Accéder à l'application**
   Ouvrez votre navigateur et allez sur : `http://localhost:5000`

## 📁 Structure du projet

```
sos-thomas-python/
├── app.py                 # Application Flask principale
├── requirements.txt        # Dépendances Python
├── data.json             # Base de données JSON (créé automatiquement)
├── templates/            # Templates HTML
│   ├── base.html         # Template de base
│   ├── dashboard.html    # Page dashboard
│   ├── agenda.html       # Page agenda
│   ├── projets.html      # Page projets
│   ├── taches.html       # Page tâches
│   ├── notes.html        # Page notes
│   ├── comptes.html      # Page comptes
│   ├── mails.html        # Page mails
│   ├── medias.html       # Page médias
│   ├── reunion.html      # Page réunion
│   ├── musique.html      # Page musique
│   └── liens.html        # Page liens
├── static/
│   └── uploads/          # Dossier pour les photos uploadées
└── README.md            # Documentation
```

## 🔧 Technologies utilisées

- **Backend** : Python 3.7+, Flask 2.3.3
- **Frontend** : HTML5, Tailwind CSS, JavaScript Vanilla
- **Formulaires** : Flask-WTF, WTForms
- **Base de données** : JSON (stockage local)
- **Upload de fichiers** : Gestion native de Flask
- **Icônes** : Font Awesome 6.4.0

## 💾 Gestion des données

L'application utilise un fichier `data.json` pour stocker toutes les informations :

- Les données sont sauvegardées automatiquement
- Format JSON lisible et modifiable
- Sauvegarde locale (pas de base de données externe nécessaire)
- Les photos sont stockées dans le dossier `static/uploads/`

## 🔒 Sécurité

- Protection CSRF avec Flask-WTF
- Validation des formulaires
- Upload sécurisé des fichiers
- Pas de stockage de données sensibles externes

## 🎯 Points forts de l'architecture

- **Code organisé** : Séparation claire entre routes, templates et logique
- **Formulaires validés** : Utilisation de WTForms pour la validation
- **Interface responsive** : Adaptation à tous les écrans
- **Navigation fluide** : Routes claires et intuitives
- **Gestion d'état** : Messages flash pour le retour utilisateur
- **Extensibilité** : Architecture modulaire facile à étendre

## 🔄 Personnalisation

### Ajouter de nouvelles fonctionnalités

1. **Créer une nouvelle route** dans `app.py`
2. **Créer le template** correspondant dans `templates/`
3. **Ajouter le formulaire** WTForms si nécessaire
4. **Mettre à jour le dashboard** avec le nouvel icône

### Modifier les thèmes

Les couleurs sont définies dans `templates/base.html` dans la section CSS :

```css
:root {
    --primary-color: #3b82f6;
    --secondary-color: #10b981;
    --accent-color: #f59e0b;
}
```

## 🐛 Dépannage

### Problèmes courants

1. **Port déjà utilisé**
   ```bash
   # Changer le port dans app.py
   app.run(debug=True, host='0.0.0.0', port=5001)
   ```

2. **Erreur d'installation**
   ```bash
   # Mettre à jour pip
   pip install --upgrade pip
   # Réinstaller les dépendances
   pip install -r requirements.txt --force-reinstall
   ```

3. **Fichiers statiques non accessibles**
   - Vérifiez que le dossier `static` existe
   - Vérifiez les permissions du dossier `uploads`

## 📝 Notes de développement

- L'application utilise Flask en mode développement (debug=True)
- Pour la production, utilisez un serveur WSGI comme Gunicorn
- Les données sont persistantes grâce au fichier JSON
- Le système de fichiers gère automatiquement les uploads

## 🤝 Contribuer

Pour ajouter des fonctionnalités ou corriger des bugs :

1. Fork le projet
2. Créer une branche pour votre modification
3. Tester vos changements
4. Soumettre une pull request

## 📄 Licence

Ce projet est open-source et disponible sous licence MIT.
