from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session, send_file
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, DateField, DateTimeField, FileField, SubmitField, PasswordField, IntegerField
from wtforms.validators import DataRequired, Email, URL, EqualTo, Length, NumberRange
import json
import os
from datetime import datetime, timedelta
import uuid
from pathlib import Path
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import requests
import base64
from urllib.parse import urlencode

# Configuration des chemins
BASE_DIR = Path(__file__).parent

app = Flask(__name__)
app.config['SECRET_KEY'] = '193a2877496f2a1385ef21f1fe4388925852ee5d959a380a64b4fb0195b424c3'
app.config['UPLOAD_FOLDER'] = BASE_DIR / 'static' / 'uploads'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = True
app.config['SESSION_USE_SIGNER'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)

# Créer le dossier uploads s'il n'existe pas
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Configuration Spotify
SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
SPOTIFY_REDIRECT_URI = os.getenv('SPOTIFY_REDIRECT_URI', 'http://localhost:5000/callback')
SPOTIFY_AUTH_URL = 'https://accounts.spotify.com/authorize'
SPOTIFY_TOKEN_URL = 'https://accounts.spotify.com/api/token'
SPOTIFY_API_URL = 'https://api.spotify.com/v1'

# Vérification des identifiants Spotify
if not SPOTIFY_CLIENT_ID or not SPOTIFY_CLIENT_SECRET or SPOTIFY_CLIENT_ID == 'votre_client_id' or SPOTIFY_CLIENT_SECRET == 'votre_client_secret':
    print("ATTENTION: Les identifiants Spotify ne sont pas configures!")
    print("Veuillez creer un compte Spotify Developer et configurer vos identifiants dans le fichier .env")
    print("Consultez README_SPOTIFY.md pour les instructions detaillees")
    SPOTIFY_CONFIGURED = False
else:
    SPOTIFY_CONFIGURED = True
    print("Configuration Spotify chargee avec succes")

class EventForm(FlaskForm):
    date = DateField('Date', validators=[DataRequired()])
    time = StringField('Heure (HH:MM)')  # Champ optionnel pour l'heure
    title = StringField('Titre', validators=[DataRequired()])
    category = SelectField('Catégorie', choices=[
        ('', 'Aucune'),
        ('important', '🔴 Important'),
        ('meeting', '🔵 Réunion'),
        ('personal', '🟢 Personnel'),
        ('work', '🟡 Travail'),
        ('urgent', '🟠 Urgent'),
        ('reminder', '🟣 Rappel'),
        ('birthday', '🎂 Anniversaire'),
        ('medical', '🏥 Médical'),
        ('travel', '✈️ Voyage'),
        ('leisure', '🎮 Loisir')
    ])

class ProjectForm(FlaskForm):
    name = StringField('Nom du projet', validators=[DataRequired()])
    status = SelectField('Statut', choices=[
        ('a-venir', 'À Venir'), 
        ('en-cours', 'En Cours'), 
        ('en-pause', 'En Pause'), 
        ('termine', 'Terminé')
    ])
    priority = SelectField('Priorité', choices=[
        ('basse', 'Basse'), 
        ('moyenne', 'Moyenne'), 
        ('haute', 'Haute')
    ])
    methodology = SelectField('Méthodologie', choices=[
        ('libre', 'Libre'),
        ('agile', 'Agile'),
        ('scrum', 'Scrum'),
        ('waterfall', 'Waterfall'),
        ('kanban', 'Kanban')
    ])
    start_date = DateField('Date de début')
    end_date = DateField('Date de fin prévue')
    description = TextAreaField('Description')
    objectives = TextAreaField('Objectifs')
    progress = IntegerField('Progression (%)', validators=[
        NumberRange(min=0, max=100, message='La progression doit être entre 0 et 100')
    ])

class TaskForm(FlaskForm):
    name = StringField('Description de la tâche', validators=[DataRequired()])
    priority = SelectField('Priorité', choices=[('basse', 'Basse'), ('moyenne', 'Moyenne'), ('haute', 'Haute')])

class ProjectTaskForm(FlaskForm):
    name = StringField('Description de la tâche', validators=[DataRequired()])
    priority = SelectField('Priorité', choices=[('basse', 'Basse'), ('moyenne', 'Moyenne'), ('haute', 'Haute')])
    project_id = SelectField('Projet', coerce=str)

class NoteForm(FlaskForm):
    title = StringField('Titre', validators=[DataRequired()])
    content = TextAreaField('Contenu', validators=[DataRequired()])

class AccountForm(FlaskForm):
    name = StringField('Nom', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])

class MailForm(FlaskForm):
    from_account = SelectField('De', coerce=str)
    to_account = SelectField('À', coerce=str)
    subject = StringField('Sujet', validators=[DataRequired()])
    content = TextAreaField('Message', validators=[DataRequired()])

class MeetingForm(FlaskForm):
    title = StringField('Titre', validators=[DataRequired()])
    date = DateTimeField('Date', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])

# Formulaires d'authentification
class LoginForm(FlaskForm):
    username = StringField('Nom d\'utilisateur ou Email', validators=[DataRequired()])
    password = PasswordField('Mot de passe', validators=[DataRequired()])

class RegisterForm(FlaskForm):
    username = StringField('Nom d\'utilisateur', validators=[DataRequired(), Length(min=3, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Mot de passe', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirmer le mot de passe', validators=[DataRequired(), EqualTo('password')])

# Formulaires pour le profil
class ProfileForm(FlaskForm):
    first_name = StringField('Prénom')
    last_name = StringField('Nom')
    bio = TextAreaField('Bio / Description')
    birth_date = DateField('Date de naissance')
    location = StringField('Localisation')
    phone = StringField('Téléphone')
    address = TextAreaField('Adresse postale')
    spotify_client_id = StringField('Spotify Client ID', description='Votre Client ID depuis Spotify Developer Dashboard')
    spotify_client_secret = StringField('Spotify Client Secret', description='Votre Client Secret depuis Spotify Developer Dashboard')

class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Mot de passe actuel', validators=[DataRequired()])
    new_password = PasswordField('Nouveau mot de passe', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirmer le mot de passe', validators=[DataRequired(), EqualTo('new_password')])

class PreferencesForm(FlaskForm):
    language = SelectField('Langue', choices=[('fr', 'Français'), ('en', 'English'), ('es', 'Español')])
    theme = SelectField('Thème', choices=[('light', 'Clair'), ('dark', 'Sombre'), ('auto', 'Auto')])

class LinkForm(FlaskForm):
    title = StringField('Titre', validators=[DataRequired()])
    url = StringField('URL', validators=[DataRequired(), URL()])

class CallForm(FlaskForm):
    contact = StringField('Contact', validators=[DataRequired()])

class MessageForm(FlaskForm):
    contact = StringField('Contact', validators=[DataRequired()])
    text = TextAreaField('Message', validators=[DataRequired()])

# Gestion des données
DATA_FILE = BASE_DIR / 'data.json'

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # S'assurer que les nouvelles sections existent
            if 'roles' not in data:
                data['roles'] = []
            if 'project_members' not in data:
                data['project_members'] = []
            if 'folders' not in data:
                data['folders'] = []
            if 'project_files' not in data:
                data['project_files'] = []
            return data
    return {
        'events': [],
        'projects': [],
        'tasks': [],
        'project_tasks': [],  # Tasks specific to projects
        'notes': [],
        'accounts': [],
        'mails': [],
        'photos': [],
        'calls': [],
        'messages': [],
        'meetings': [],
        'links': [],
        'roles': [],  # Rôles personnalisables
        'project_members': [],  # Membres des projets
        'folders': [],  # Dossiers de notes
        'project_files': []  # Fichiers des projets
    }

def save_data(data):
    try:
        print(f"Tentative de sauvegarde dans: {DATA_FILE}")
        print(f"Contenu à sauvegarder: {len(data)} clés")
        
        # S'assurer que le répertoire existe
        DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
        
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        # Vérifier que le fichier a bien été écrit
        if DATA_FILE.exists():
            file_size = DATA_FILE.stat().st_size
            print(f"Fichier sauvegardé avec succès - Taille: {file_size} octets")
        else:
            print("ERREUR: Le fichier n'a pas été créé!")
            
    except Exception as e:
        print(f"ERREUR lors de la sauvegarde: {e}")
        raise

# Fonctions de gestion des utilisateurs
def load_users():
    users_file = BASE_DIR / 'data' / 'users.json'
    if not os.path.exists(BASE_DIR / 'data'):
        os.makedirs(BASE_DIR / 'data')
    
    if os.path.exists(users_file):
        with open(users_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_users(users):
    users_file = BASE_DIR / 'data' / 'users.json'
    with open(users_file, 'w', encoding='utf-8') as f:
        json.dump(users, f, indent=2, ensure_ascii=False)

def get_user_by_username_or_email(identifier):
    users = load_users()
    for user in users.values():
        if user['username'] == identifier or user['email'] == identifier:
            return user
    return None

def username_exists(username):
    users = load_users()
    return any(user['username'] == username for user in users.values())

def email_exists(email):
    users = load_users()
    return any(user['email'] == email for user in users.values())

# Fonctions de gestion des profils
def load_profiles():
    profiles_file = BASE_DIR / 'data' / 'profiles.json'
    if not os.path.exists(BASE_DIR / 'data'):
        os.makedirs(BASE_DIR / 'data')
    
    if os.path.exists(profiles_file):
        with open(profiles_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_profiles(profiles):
    profiles_file = BASE_DIR / 'data' / 'profiles.json'
    with open(profiles_file, 'w', encoding='utf-8') as f:
        json.dump(profiles, f, indent=2, ensure_ascii=False)

def get_user_profile(user_id):
    profiles = load_profiles()
    return profiles.get(user_id, {
        'first_name': '',
        'last_name': '',
        'bio': '',
        'birth_date': '',
        'location': '',
        'phone': '',
        'address': '',
        'avatar': '',
        'language': 'fr',
        'theme': 'light',
        'spotify_client_id': '',
        'spotify_client_secret': '',
        'spotify_connected': False,
        'spotify_access_token': '',
        'spotify_refresh_token': '',
        'spotify_expires_at': 0,
        'created_at': datetime.now().isoformat()
    })

def save_user_profile(user_id, profile_data):
    profiles = load_profiles()
    profile_data['updated_at'] = datetime.now().isoformat()
    profiles[user_id] = profile_data
    save_profiles(profiles)

# Fonctions utilitaires Spotify
def get_user_spotify_config(user_id):
    """Récupère la configuration Spotify de l'utilisateur"""
    profile = get_user_profile(user_id)
    return {
        'client_id': profile.get('spotify_client_id'),
        'client_secret': profile.get('spotify_client_secret'),
        'access_token': profile.get('spotify_access_token'),
        'refresh_token': profile.get('spotify_refresh_token'),
        'expires_at': profile.get('spotify_expires_at', 0),
        'connected': profile.get('spotify_connected', False)
    }

def save_user_spotify_tokens(user_id, access_token, refresh_token, expires_in):
    """Sauvegarde les tokens Spotify de l'utilisateur"""
    profile = get_user_profile(user_id)
    profile['spotify_access_token'] = access_token
    profile['spotify_refresh_token'] = refresh_token
    profile['spotify_expires_at'] = datetime.now().timestamp() + expires_in
    profile['spotify_connected'] = True
    save_user_profile(user_id, profile)

def get_spotify_auth_url(user_id):
    """Génère l'URL d'authentification Spotify pour un utilisateur"""
    profile = get_user_profile(user_id)
    client_id = profile.get('spotify_client_id')
    
    if not client_id:
        return None
    
    params = {
        'client_id': client_id,
        'response_type': 'code',
        'redirect_uri': SPOTIFY_REDIRECT_URI,
        'scope': 'user-read-playback-state user-modify-playback-state user-read-currently-playing',
        'state': f"{user_id}:{uuid.uuid4()}"  # Inclure l'user_id dans le state
    }
    return f"{SPOTIFY_AUTH_URL}?{urlencode(params)}"

def get_spotify_token(code, client_id, client_secret):
    """Échange le code d'autorisation contre un token d'accès"""
    auth_header = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
    
    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': SPOTIFY_REDIRECT_URI
    }
    
    headers = {
        'Authorization': f'Basic {auth_header}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    response = requests.post(SPOTIFY_TOKEN_URL, data=data, headers=headers)
    return response.json() if response.status_code == 200 else None

def refresh_spotify_token(refresh_token):
    """Rafraîchit le token d'accès Spotify"""
    auth_header = base64.b64encode(f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}".encode()).decode()
    
    data = {
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token
    }
    
    headers = {
        'Authorization': f'Basic {auth_header}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    response = requests.post(SPOTIFY_TOKEN_URL, data=data, headers=headers)
    return response.json() if response.status_code == 200 else None

def make_spotify_request(endpoint, access_token):
    """Effectue une requête à l'API Spotify"""
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    response = requests.get(f"{SPOTIFY_API_URL}/{endpoint}", headers=headers)
    return response.json() if response.status_code == 200 else None

def get_current_track(access_token):
    """Récupère la piste en cours de lecture"""
    return make_spotify_request('me/player/currently-playing', access_token)

def play_spotify(access_token):
    """Met en lecture la musique"""
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    response = requests.put(f"{SPOTIFY_API_URL}/me/player/play", headers=headers)
    return response.status_code == 204

def pause_spotify(access_token):
    """Met en pause la musique"""
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    response = requests.put(f"{SPOTIFY_API_URL}/me/player/pause", headers=headers)
    return response.status_code == 204

def next_track_spotify(access_token):
    """Piste suivante"""
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    response = requests.post(f"{SPOTIFY_API_URL}/me/player/next", headers=headers)
    return response.status_code == 204

def previous_track_spotify(access_token):
    """Piste précédente"""
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    response = requests.post(f"{SPOTIFY_API_URL}/me/player/previous", headers=headers)
    return response.status_code == 204

# Décorateur pour protéger les routes
def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Routes d'authentification
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        identifier = form.username.data
        password = form.password.data
        
        user = get_user_by_username_or_email(identifier)
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['email'] = user['email']
            session.permanent = True  # Rendre la session permanente
            flash(f'Bon retour {user["username"]} !', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Nom d\'utilisateur/email ou mot de passe incorrect', 'error')
    
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = form.password.data
        
        # Vérifier si le nom d'utilisateur ou l'email existe déjà
        if username_exists(username):
            flash('Ce nom d\'utilisateur est déjà pris', 'error')
        elif email_exists(email):
            flash('Cet email est déjà utilisé', 'error')
        else:
            # Créer le nouvel utilisateur
            users = load_users()
            user_id = str(uuid.uuid4())
            
            users[user_id] = {
                'id': user_id,
                'username': username,
                'email': email,
                'password': generate_password_hash(password),
                'created_at': datetime.now().isoformat()
            }
            
            save_users(users)
            flash('Compte créé avec succès ! Vous pouvez maintenant vous connecter.', 'success')
            return redirect(url_for('login'))
    
    return render_template('register.html', form=form)

@app.route('/logout')
def logout():
    session.clear()
    flash('Vous avez été déconnecté', 'info')
    return redirect(url_for('login'))

@app.route('/first_connection')
def first_connection():
    users = load_users()
    if users:  # Si des utilisateurs existent, rediriger vers login
        return redirect(url_for('login'))
    return render_template('first_connection.html')

# Routes principales
@app.route('/')
@login_required
def dashboard():
    data = load_data()
    current_date = datetime.now().strftime('%d %B %Y')
    return render_template('dashboard.html', data=data, current_date=current_date)

@app.route('/agenda')
@login_required
def agenda():
    data = load_data()
    form = EventForm()
    return render_template('agenda.html', data=data, form=form)

@app.route('/projets')
@login_required
def projets():
    data = load_data()
    form = ProjectForm()
    return render_template('projets.html', data=data, form=form)

@app.route('/taches')
@login_required
def taches():
    data = load_data()
    form = TaskForm()
    project_form = ProjectTaskForm()
    
    # Remplir les options de projets pour le formulaire de tâche de projet
    project_form.project_id.choices = [('', 'Sélectionner un projet...')] + [(p['id'], p['name']) for p in data.get('projects', [])]
    
    # Récupérer les paramètres de tri et d'affichage
    sort_by = request.args.get('sort_by', 'created_at')
    sort_order = request.args.get('sort_order', 'desc')
    show_completed = request.args.get('show_completed', 'false').lower() == 'true'
    
    # Combiner les tâches normales et les tâches de projet
    all_tasks = []
    
    # Ajouter les tâches normales
    for task in data.get('tasks', []):
        # Afficher selon le paramètre et le statut
        task_completed = task.get('completed', False)
        if show_completed or not task_completed:
            task['task_type'] = 'general'
            task['project_name'] = None
            all_tasks.append(task)
    
    # Ajouter les tâches de projet
    project_tasks = data.get('project_tasks', [])
    projects_dict = {p['id']: p for p in data.get('projects', [])}
    
    for task in project_tasks:
        # Vérifier si la tâche est complétée soit par completed=true soit par status terminé/réalisée
        task_completed = task.get('completed', False) or task.get('status', '') in ['terminé', 'termine', 'réalisée', 'fait']
        if show_completed or not task_completed:
            task['task_type'] = 'project'
            task['project_name'] = projects_dict.get(task['project_id'], {}).get('name', 'Projet inconnu')
            all_tasks.append(task)
    
    # Trier les tâches
    if sort_by == 'priority':
        priority_order = {'haute': 0, 'moyenne': 1, 'basse': 2}
        all_tasks.sort(key=lambda x: priority_order.get(x.get('priority', 'basse'), 2))
    elif sort_by == 'name':
        all_tasks.sort(key=lambda x: x.get('name', '').lower())
    elif sort_by == 'status':
        all_tasks.sort(key=lambda x: x.get('completed', False))
    elif sort_by == 'project':
        # Trier par nom de projet, puis par type
        all_tasks.sort(key=lambda x: (x.get('project_name', 'zzz'), x.get('task_type', '')))
    elif sort_by == 'created_at':
        all_tasks.sort(key=lambda x: x.get('created_at', ''))
    
    # Inverser l'ordre si nécessaire
    if sort_order == 'desc':
        all_tasks.reverse()
    
    data['all_tasks'] = all_tasks
    
    return render_template('taches.html', data=data, form=form, project_form=project_form, sort_by=sort_by, sort_order=sort_order, show_completed=show_completed)

@app.route('/notes')
@login_required
def notes():
    data = load_data()
    form = NoteForm()
    return render_template('notes.html', data=data, form=form)

@app.route('/note_editor')
@login_required
def note_editor():
    note_id = request.args.get('note_id')
    return render_template('note_editor.html', note_id=note_id)

@app.route('/api/notes/save', methods=['POST'])
@login_required
def save_note():
    try:
        note_data = request.get_json()
        data = load_data()
        
        if 'id' in note_data and note_data['id']:
            # Mettre à jour une note existante
            for i, note in enumerate(data['notes']):
                if note['id'] == note_data['id']:
                    data['notes'][i].update(note_data)
                    break
        else:
            # Créer une nouvelle note
            new_note = {
                'id': str(uuid.uuid4()),
                'title': note_data.get('title', 'Sans titre'),
                'content': note_data.get('content', ''),
                'folder': note_data.get('folder', 'general'),
                'created_at': note_data.get('created_at', datetime.now().isoformat()),
                'updated_at': datetime.now().isoformat()
            }
            data['notes'].append(new_note)
        
        save_data(data)
        
        return jsonify({
            'success': True,
            'note_id': note_data.get('id') or new_note['id'],
            'message': 'Note sauvegardée avec succès'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erreur lors de la sauvegarde: {str(e)}'
        }), 500

@app.route('/api/notes/<note_id>')
@login_required
def get_note(note_id):
    try:
        data = load_data()
        note = next((note for note in data['notes'] if note['id'] == note_id), None)
        
        if note:
            return jsonify({
                'success': True,
                'note': note
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Note non trouvée'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erreur: {str(e)}'
        }), 500

@app.route('/comptes')
@login_required
def comptes():
    data = load_data()
    form = AccountForm()
    return render_template('comptes.html', data=data, form=form)

@app.route('/mails')
@login_required
def mails():
    data = load_data()
    form = MailForm()
    # Remplir les options pour les comptes
    form.from_account.choices = [('', 'Sélectionner...')] + [(acc['id'], acc['name']) for acc in data['accounts']]
    form.to_account.choices = [('', 'Sélectionner...')] + [(acc['id'], acc['name']) for acc in data['accounts']]
    return render_template('mails.html', data=data, form=form)

@app.route('/medias')
@login_required
def medias():
    data = load_data()
    call_form = CallForm()
    message_form = MessageForm()
    return render_template('medias.html', data=data, call_form=call_form, message_form=message_form)

@app.route('/reunion')
@login_required
def reunion():
    data = load_data()
    form = MeetingForm()
    return render_template('reunion.html', data=data, form=form)

@app.route('/musique')
@login_required
def musique():
    return render_template('musique.html')

# Routes Spotify
@app.route('/spotify/login')
@login_required
def spotify_login():
    """Redirige vers l'authentification Spotify"""
    user_id = session['user_id']
    spotify_config = get_user_spotify_config(user_id)
    
    if not spotify_config['client_id'] or not spotify_config['client_secret']:
        flash('Veuillez configurer vos identifiants Spotify dans votre profil avant de vous connecter.', 'error')
        return redirect(url_for('profile'))
    
    try:
        auth_url = get_spotify_auth_url(user_id)
        if not auth_url:
            flash('Erreur de configuration Spotify. Veuillez vérifier vos identifiants.', 'error')
            return redirect(url_for('musique'))
        return redirect(auth_url)
    except Exception as e:
        flash(f'Erreur lors de la connexion à Spotify: {str(e)}', 'error')
        return redirect(url_for('musique'))

@app.route('/callback')
@login_required
def spotify_callback():
    """Gère le callback OAuth de Spotify"""
    code = request.args.get('code')
    error = request.args.get('error')
    state = request.args.get('state', '')
    
    if error:
        flash('Erreur d\'authentification Spotify: ' + error, 'error')
        return redirect(url_for('musique'))
    
    if not code:
        flash('Code d\'autorisation manquant', 'error')
        return redirect(url_for('musique'))
    
    # Extraire l'user_id du state
    try:
        user_id = state.split(':')[0]
        if user_id != session['user_id']:
            flash('Erreur de sécurité: utilisateur non correspondant', 'error')
            return redirect(url_for('musique'))
    except:
        flash('Erreur de sécurité: state invalide', 'error')
        return redirect(url_for('musique'))
    
    # Récupérer la configuration Spotify de l'utilisateur
    spotify_config = get_user_spotify_config(user_id)
    
    # Échanger le code contre un token
    token_data = get_spotify_token(code, spotify_config['client_id'], spotify_config['client_secret'])
    if not token_data:
        flash('Erreur lors de l\'obtention du token Spotify', 'error')
        return redirect(url_for('musique'))
    
    # Sauvegarder les tokens dans le profil utilisateur
    save_user_spotify_tokens(
        user_id,
        token_data.get('access_token'),
        token_data.get('refresh_token'),
        token_data.get('expires_in', 3600)
    )
    
    flash('Connexion Spotify réussie!', 'success')
    return redirect(url_for('musique'))

@app.route('/api/spotify/current')
@login_required
def spotify_current():
    """API pour obtenir la piste actuelle"""
    user_id = session['user_id']
    spotify_config = get_user_spotify_config(user_id)
    access_token = spotify_config['access_token']
    
    if not access_token or not spotify_config['connected']:
        return jsonify({'error': 'Non connecté à Spotify'}), 401
    
    # Vérifier si le token est expiré
    if datetime.now().timestamp() > spotify_config['expires_at']:
        refresh_token = spotify_config['refresh_token']
        if refresh_token:
            token_data = refresh_spotify_token(refresh_token)
            if token_data:
                save_user_spotify_tokens(
                    user_id,
                    token_data.get('access_token'),
                    token_data.get('refresh_token', refresh_token),
                    token_data.get('expires_in', 3600)
                )
                access_token = token_data.get('access_token')
            else:
                return jsonify({'error': 'Token expiré, veuillez vous reconnecter'}), 401
        else:
            return jsonify({'error': 'Token expiré, veuillez vous reconnecter'}), 401
    
    current_track = get_current_track(access_token)
    if current_track and 'item' in current_track:
        track = current_track['item']
        return jsonify({
            'name': track['name'],
            'artist': ', '.join([artist['name'] for artist in track['artists']]),
            'album': track['album']['name'],
            'image': track['album']['images'][0]['url'] if track['album']['images'] else None,
            'is_playing': current_track['is_playing'],
            'progress_ms': current_track['progress_ms'],
            'duration_ms': track['duration_ms']
        })
    else:
        return jsonify({'error': 'Aucune lecture en cours'}), 404

@app.route('/api/spotify/play', methods=['POST'])
@login_required
def spotify_play():
    """API pour mettre en lecture"""
    user_id = session['user_id']
    spotify_config = get_user_spotify_config(user_id)
    access_token = spotify_config['access_token']
    
    if not access_token or not spotify_config['connected']:
        return jsonify({'error': 'Non connecté à Spotify'}), 401
    
    success = play_spotify(access_token)
    return jsonify({'success': success})

@app.route('/api/spotify/pause', methods=['POST'])
@login_required
def spotify_pause():
    """API pour mettre en pause"""
    user_id = session['user_id']
    spotify_config = get_user_spotify_config(user_id)
    access_token = spotify_config['access_token']
    
    if not access_token or not spotify_config['connected']:
        return jsonify({'error': 'Non connecté à Spotify'}), 401
    
    success = pause_spotify(access_token)
    return jsonify({'success': success})

@app.route('/api/spotify/next', methods=['POST'])
@login_required
def spotify_next():
    """API pour piste suivante"""
    user_id = session['user_id']
    spotify_config = get_user_spotify_config(user_id)
    access_token = spotify_config['access_token']
    
    if not access_token or not spotify_config['connected']:
        return jsonify({'error': 'Non connecté à Spotify'}), 401
    
    success = next_track_spotify(access_token)
    return jsonify({'success': success})

@app.route('/api/spotify/previous', methods=['POST'])
@login_required
def spotify_previous():
    """API pour piste précédente"""
    user_id = session['user_id']
    spotify_config = get_user_spotify_config(user_id)
    access_token = spotify_config['access_token']
    
    if not access_token or not spotify_config['connected']:
        return jsonify({'error': 'Non connecté à Spotify'}), 401
    
    success = previous_track_spotify(access_token)
    return jsonify({'success': success})

@app.route('/liens')
@login_required
def liens():
    data = load_data()
    form = LinkForm()
    return render_template('liens.html', data=data, form=form)

# Routes pour le profil
@app.route('/profile')
@login_required
def profile():
    user_id = session['user_id']
    profile = get_user_profile(user_id)
    users = load_users()
    user = users.get(user_id, {})
    
    profile_form = ProfileForm(data=profile)
    password_form = ChangePasswordForm()
    preferences_form = PreferencesForm(data=profile)
    
    return render_template('profile.html', 
                         profile=profile, 
                         user=user,
                         profile_form=profile_form,
                         password_form=password_form,
                         preferences_form=preferences_form)

@app.route('/profile/update', methods=['POST'])
@login_required
def update_profile():
    user_id = session['user_id']
    form = ProfileForm()
    
    if form.validate_on_submit():
        profile = get_user_profile(user_id)
        profile.update({
            'first_name': form.first_name.data,
            'last_name': form.last_name.data,
            'bio': form.bio.data,
            'birth_date': form.birth_date.data.isoformat() if form.birth_date.data else '',
            'location': form.location.data,
            'phone': form.phone.data,
            'address': form.address.data,
            'spotify_client_id': form.spotify_client_id.data,
            'spotify_client_secret': form.spotify_client_secret.data
        })
        
        # Si les identifiants Spotify changent, réinitialiser la connexion
        old_profile = get_user_profile(user_id)
        if (old_profile.get('spotify_client_id') != form.spotify_client_id.data or 
            old_profile.get('spotify_client_secret') != form.spotify_client_secret.data):
            profile['spotify_connected'] = False
            profile['spotify_access_token'] = ''
            profile['spotify_refresh_token'] = ''
            profile['spotify_expires_at'] = 0
            flash('Identifiants Spotify mis à jour. Veuillez vous reconnecter à Spotify.', 'info')
        
        save_user_profile(user_id, profile)
        flash('Profil mis à jour avec succès !', 'success')
    
    return redirect(url_for('profile'))

@app.route('/profile/change_password', methods=['POST'])
@login_required
def change_password():
    user_id = session['user_id']
    form = ChangePasswordForm()
    
    if form.validate_on_submit():
        users = load_users()
        user = users.get(user_id)
        
        if user and check_password_hash(user['password'], form.current_password.data):
            users[user_id]['password'] = generate_password_hash(form.new_password.data)
            save_users(users)
            flash('Mot de passe changé avec succès !', 'success')
        else:
            flash('Mot de passe actuel incorrect', 'error')
    
    return redirect(url_for('profile'))

@app.route('/profile/preferences', methods=['POST'])
@login_required
def update_preferences():
    user_id = session['user_id']
    form = PreferencesForm()
    
    if form.validate_on_submit():
        profile = get_user_profile(user_id)
        profile.update({
            'language': form.language.data,
            'theme': form.theme.data
        })
        save_user_profile(user_id, profile)
        flash('Préférences mises à jour avec succès !', 'success')
    
    return redirect(url_for('profile'))

@app.route('/profile/upload_avatar', methods=['POST'])
@login_required
def upload_avatar():
    if 'avatar' not in request.files:
        flash('Aucun fichier sélectionné', 'error')
        return redirect(url_for('profile'))
    
    file = request.files['avatar']
    if file.filename == '':
        flash('Aucun fichier sélectionné', 'error')
        return redirect(url_for('profile'))
    
    if file and allowed_file(file.filename, ['jpg', 'jpeg', 'png', 'gif']):
        filename = secure_filename(file.filename)
        avatar_filename = f"avatar_{session['user_id']}_{filename}"
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], avatar_filename))
        
        # Mettre à jour le profil
        user_id = session['user_id']
        profile = get_user_profile(user_id)
        profile['avatar'] = avatar_filename
        save_user_profile(user_id, profile)
        
        flash('Avatar mis à jour avec succès !', 'success')
    else:
        flash('Format de fichier non autorisé', 'error')
    
    return redirect(url_for('profile'))

def allowed_file(filename, allowed_extensions):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

# Routes API pour les actions
@app.route('/api/add_event', methods=['POST'])
def add_event():
    data = load_data()
    form = EventForm()
    if form.validate_on_submit():
        # Combiner date et heure si l'heure est fournie
        datetime_str = form.date.data.isoformat()
        if form.time.data and form.time.data.strip():
            datetime_str = f"{form.date.data.isoformat()}T{form.time.data.strip()}:00"
        
        # Déterminer si l'événement est récurrent (anniversaire)
        is_recurring = form.category.data == 'birthday'
        
        event = {
            'id': str(uuid.uuid4()),
            'date': datetime_str,
            'title': form.title.data,
            'category': form.category.data or '',
            'recurring': is_recurring,
            'created_at': datetime.now().isoformat()
        }
        data['events'].append(event)
        save_data(data)
        flash('Événement ajouté avec succès!')
    return redirect(url_for('agenda'))

@app.route('/api/edit_event/<event_id>', methods=['POST'])
def edit_event(event_id):
    data = load_data()
    event_index = next((i for i, event in enumerate(data['events']) if event['id'] == event_id), None)
    
    if event_index is not None:
        try:
            import json
            update_data = json.loads(request.data)
            
            # Gérer la mise à jour de la date et de l'heure
            current_event = data['events'][event_index]
            new_date = update_data.get('date', current_event['date'])
            new_time = update_data.get('time', '')
            
            if new_time and new_time.strip():
                # Combiner date et heure
                if 'T' in new_date:
                    date_part = new_date.split('T')[0]
                else:
                    date_part = new_date
                datetime_str = f"{date_part}T{new_time.strip()}:00"
            else:
                # Garder seulement la date
                if 'T' in new_date:
                    datetime_str = new_date.split('T')[0]
                else:
                    datetime_str = new_date
            
            # Déterminer si l'événement est récurrent
            is_recurring = update_data.get('category', current_event.get('category', '')) == 'birthday'
            
            data['events'][event_index]['title'] = update_data.get('title', current_event['title'])
            data['events'][event_index]['date'] = datetime_str
            data['events'][event_index]['category'] = update_data.get('category', current_event.get('category', ''))
            data['events'][event_index]['recurring'] = is_recurring
            data['events'][event_index]['updated_at'] = datetime.now().isoformat()
            
            save_data(data)
            return jsonify({'success': True})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})
    
    return jsonify({'success': False, 'error': 'Événement non trouvé'})

@app.route('/api/add_project', methods=['POST'])
@login_required
def add_project():
    try:
        data = load_data()
        project_data = request.get_json()
        
        if not project_data:
            return jsonify({
                'success': False,
                'message': 'Aucune données reçues'
            }), 400
        
        # Validation basique
        if not project_data.get('name'):
            return jsonify({
                'success': False,
                'message': 'Le nom du projet est requis'
            }), 400
        
        project = {
            'id': str(uuid.uuid4()),
            'name': project_data.get('name', ''),
            'status': project_data.get('status', 'en-cours'),
            'priority': project_data.get('priority', 'moyenne'),
            'methodology': project_data.get('methodology', 'libre'),
            'start_date': project_data.get('start_date'),
            'end_date': project_data.get('end_date'),
            'description': project_data.get('description', ''),
            'objectives': project_data.get('objectives', ''),
            'progress': int(project_data.get('progress', 0)),
            'created_at': datetime.now().isoformat()
        }
        
        data['projects'].append(project)
        save_data(data)
        
        return jsonify({
            'success': True,
            'message': 'Projet créé avec succès!',
            'project': project
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erreur lors de la création du projet: {str(e)}'
        }), 500

@app.route('/api/edit_project/<project_id>', methods=['POST'])
@login_required
def edit_project(project_id):
    data = load_data()
    project_index = next((i for i, project in enumerate(data['projects']) if project['id'] == project_id), None)
    
    if project_index is not None:
        try:
            import json
            update_data = json.loads(request.data)
            
            # Mettre à jour le projet avec les nouvelles données
            project = data['projects'][project_index]
            project.update({
                'name': update_data.get('name', project['name']),
                'status': update_data.get('status', project['status']),
                'priority': update_data.get('priority', project['priority']),
                'methodology': update_data.get('methodology', project['methodology']),
                'description': update_data.get('description', project['description']),
                'objectives': update_data.get('objectives', project['objectives']),
                'progress': update_data.get('progress', project['progress']),
                'updated_at': datetime.now().isoformat()
            })
            
            # Gérer les dates si fournies
            if update_data.get('start_date'):
                project['start_date'] = update_data['start_date']
            if update_data.get('end_date'):
                project['end_date'] = update_data['end_date']
            
            save_data(data)
            return jsonify({'success': True})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})
    
    return jsonify({'success': False, 'error': 'Projet non trouvé'})

@app.route('/api/duplicate-project', methods=['POST'])
@login_required
def duplicate_project():
    try:
        project_data = request.get_json()
        data = load_data()
        
        # Créer une copie du projet avec un nouvel ID
        new_project = {
            'id': str(uuid.uuid4()),
            'name': project_data.get('name', 'Projet copié'),
            'status': project_data.get('status', 'en-cours'),
            'priority': project_data.get('priority', 'moyenne'),
            'methodology': project_data.get('methodology', 'libre'),
            'start_date': project_data.get('start_date'),
            'end_date': project_data.get('end_date'),
            'description': project_data.get('description', ''),
            'objectives': project_data.get('objectives', ''),
            'progress': project_data.get('progress', 0),
            'created_at': datetime.now().isoformat()
        }
        
        data['projects'].append(new_project)
        save_data(data)
        
        return jsonify({
            'success': True,
            'project': new_project,
            'message': 'Projet dupliqué avec succès'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erreur lors de la duplication: {str(e)}'
        }), 500

@app.route('/api/delete-project/<project_id>', methods=['DELETE'])
@login_required
def delete_project(project_id):
    try:
        data = load_data()
        
        # Supprimer le projet
        project_index = next((i for i, project in enumerate(data['projects']) if project['id'] == project_id), None)
        
        if project_index is not None:
            # Supprimer aussi les tâches associées au projet
            project_tasks = data.get('project_tasks', [])
            data['project_tasks'] = [task for task in project_tasks if task['project_id'] != project_id]
            
            # Supprimer le projet
            data['projects'].pop(project_index)
            save_data(data)
            
            return jsonify({
                'success': True,
                'message': 'Projet supprimé avec succès'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Projet non trouvé'
            }), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erreur lors de la suppression: {str(e)}'
        }), 500

@app.route('/api/reorder-projects', methods=['POST'])
@login_required
def reorder_projects():
    try:
        data_request = request.get_json()
        project_order = data_request.get('order', [])
        
        if not project_order:
            return jsonify({
                'success': False,
                'message': 'Ordre des projets non fourni'
            }), 400
        
        data = load_data()
        
        # Créer un dictionnaire pour mapper les IDs aux projets
        project_dict = {project['id']: project for project in data['projects']}
        
        # Réorganiser les projets selon le nouvel ordre
        reordered_projects = []
        for project_id in project_order:
            if project_id in project_dict:
                reordered_projects.append(project_dict[project_id])
        
        # Ajouter les projets qui ne sont pas dans la liste (au cas où)
        for project in data['projects']:
            if project['id'] not in project_order:
                reordered_projects.append(project)
        
        # Sauvegarder le nouvel ordre
        data['projects'] = reordered_projects
        save_data(data)
        
        return jsonify({
            'success': True,
            'message': 'Ordre des projets mis à jour avec succès'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erreur lors de la réorganisation: {str(e)}'
        }), 500

def calculate_project_progress(project_id):
    data = load_data()
    project_tasks = data.get('project_tasks', [])
    project_tasks = [task for task in project_tasks if task['project_id'] == project_id]
    
    if not project_tasks:
        return 0
    
    # Compter les tâches terminées (statut 'termine', 'fait', 'terminé', 'réalisée')
    completed_tasks = len([task for task in project_tasks if task.get('status') in ['termine', 'fait', 'terminé', 'réalisée']])
    total_tasks = len(project_tasks)
    
    # Calculer le pourcentage
    progress = round((completed_tasks / total_tasks) * 100)
    
    # Mettre à jour la progression dans les données du projet
    for project in data.get('projects', []):
        if project['id'] == project_id:
            project['progress'] = progress
            break
    
    save_data(data)
    
    return progress

@app.route('/project/<project_id>')
@login_required
def project_details(project_id):
    data = load_data()
    project = next((p for p in data['projects'] if p['id'] == project_id), None)
    
    if project:
        # Debug: Vérifier les données du projet
        print(f"🔍 DEBUG - Project ID: {project_id}")
        print(f"🔍 DEBUG - Project name: {project.get('name', 'N/A')}")
        print(f"🔍 DEBUG - Project description: {project.get('description', 'N/A')}")
        print(f"🔍 DEBUG - Project manager: {project.get('manager', 'N/A')}")
        print(f"🔍 DEBUG - Project email: {project.get('email', 'N/A')}")
        
        # Calculer la progression du projet
        progress = calculate_project_progress(project_id)
        project_tasks = data.get('project_tasks', [])
        project_tasks = [task for task in project_tasks if task['project_id'] == project_id]
        
        # Récupérer les fichiers du projet
        project_files = data.get('project_files', [])
        project_files = [file for file in project_files if file['project_id'] == project_id]
        
        try:
            rendered = render_template('project_details.html', project=project, data=data, progress=progress, project_tasks=project_tasks, project_files=project_files)
            print(f"✅ Template rendu avec succès - Taille: {len(rendered)} caractères")
            return rendered
        except Exception as e:
            print(f"❌ Erreur lors du rendu du template: {e}")
            print(f"❌ Type d'erreur: {type(e)}")
            # Retourner une page d'erreur simple
            return f"<h1>Erreur de template</h1><p>{str(e)}</p><pre>{project}</pre>"
    else:
        flash('Projet non trouvé', 'error')
        return redirect(url_for('projets'))

@app.route('/api/add_task_to_project/<project_id>', methods=['POST'])
@login_required
def add_task_to_project(project_id):
    data = load_data()
    
    try:
        task_data = request.get_json()
        
        # S'assurer que project_tasks existe
        if 'project_tasks' not in data:
            data['project_tasks'] = []
        
        task = {
            'id': str(uuid.uuid4()),
            'project_id': project_id,
            'name': task_data.get('name', ''),
            'description': task_data.get('description', ''),
            'priority': task_data.get('priority', 'moyenne'),
            'status': task_data.get('status', 'a-faire'),
            'assignee': task_data.get('assignee', ''),
            'due_date': task_data.get('dueDate', ''),
            'tags': task_data.get('tags', []),
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        data['project_tasks'].append(task)
        save_data(data)
        
        # Calculer la nouvelle progression du projet
        new_progress = calculate_project_progress(project_id)
        
        return jsonify({'success': True, 'task': task, 'progress': new_progress})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/get_project_tasks/<project_id>')
@login_required
def get_project_tasks(project_id):
    data = load_data()
    project_tasks = data.get('project_tasks', [])
    project_tasks = [task for task in project_tasks if task['project_id'] == project_id]
    
    return jsonify({'success': True, 'tasks': project_tasks})

@app.route('/api/delete_task/<task_id>', methods=['DELETE'])
@login_required
def delete_project_task(task_id):
    data = load_data()
    
    try:
        project_tasks = data.get('project_tasks', [])
        project_tasks = [task for task in project_tasks if task['id'] != task_id]
        data['project_tasks'] = project_tasks
        save_data(data)
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/update_task/<task_id>', methods=['POST'])
@login_required
def update_task_status(task_id):
    data = load_data()
    
    try:
        task_data = request.get_json()
        project_tasks = data.get('project_tasks', [])
        
        for task in project_tasks:
            if task['id'] == task_id:
                old_status = task.get('status', '')
                new_status = task_data.get('status', task['status'])
                
                task.update({
                    'name': task_data.get('name', task['name']),
                    'description': task_data.get('description', task['description']),
                    'priority': task_data.get('priority', task['priority']),
                    'status': new_status,
                    'assignee': task_data.get('assignee', task['assignee']),
                    'due_date': task_data.get('dueDate', task['due_date']),
                    'tags': task_data.get('tags', task.get('tags', [])),
                    'updated_at': datetime.now().isoformat()
                })
                
                # Synchroniser le champ completed avec le statut
                completed_statuses = ['termine', 'fait', 'terminé', 'réalisée']
                task['completed'] = new_status in completed_statuses
                
                # Si la tâche passe au statut "terminé" pour la première fois
                if new_status in completed_statuses and old_status not in completed_statuses:
                    task['completed_at'] = datetime.now().isoformat()
                elif new_status not in completed_statuses:
                    # Si la tâche n'est plus terminée, on retire la date de complétion
                    task.pop('completed_at', None)
                
                project_id = task['project_id']
                break
        
        data['project_tasks'] = project_tasks
        save_data(data)
        
        # Calculer la nouvelle progression du projet
        new_progress = calculate_project_progress(project_id)
        
        return jsonify({'success': True, 'progress': new_progress})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/kanban')
@login_required
def kanban_view():
    data = load_data()
    # Organiser les projets par statut pour la vue Kanban
    kanban_data = {
        'a-venir': [p for p in data['projects'] if p.get('status') == 'a-venir'],
        'en-cours': [p for p in data['projects'] if p.get('status') == 'en-cours'],
        'en-pause': [p for p in data['projects'] if p.get('status') == 'en-pause'],
        'termine': [p for p in data['projects'] if p.get('status') == 'termine']
    }
    return render_template('kanban.html', kanban_data=kanban_data, data=data)

@app.route('/api/update_project_task/<task_id>', methods=['POST'])
@login_required
def update_project_task(task_id):
    try:
        data = load_data()
        task_data = request.get_json()
        project_tasks = data.get('project_tasks', [])
        
        for task in project_tasks:
            if task['id'] == task_id:
                task.update({
                    'name': task_data.get('name', task['name']),
                    'priority': task_data.get('priority', task['priority']),
                    'project_id': task_data.get('project_id', task['project_id']),
                    'updated_at': datetime.now().isoformat()
                })
                
                # Synchroniser le champ completed avec le statut
                completed_statuses = ['termine', 'fait', 'terminé', 'réalisée']
                task['completed'] = task.get('status', '') in completed_statuses
                break
        
        data['project_tasks'] = project_tasks
        save_data(data)
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/update_project_progress/<project_id>', methods=['POST'])
@login_required
def update_project_progress_api(project_id):
    try:
        progress = calculate_project_progress(project_id)
        return jsonify({'success': True, 'progress': progress})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/add_project_task_from_tasks', methods=['POST'])
@login_required
def add_project_task_from_tasks():
    try:
        data = load_data()
        
        # Récupérer les données du FormData
        task_name = request.form.get('name')
        task_priority = request.form.get('priority', 'moyenne')
        project_id = request.form.get('project_id')
        task_status = request.form.get('status', 'a-faire')
        
        if not task_name:
            return jsonify({'success': False, 'error': 'Le nom de la tâche est requis'})
        
        if not project_id:
            return jsonify({'success': False, 'error': 'Le projet est requis'})
        
        # S'assurer que project_tasks existe
        if 'project_tasks' not in data:
            data['project_tasks'] = []
        
        # Synchroniser le champ completed avec le statut
        completed_statuses = ['terminé', 'termine', 'réalisée', 'fait']
        is_completed = task_status in completed_statuses
        
        task = {
            'id': str(uuid.uuid4()),
            'project_id': project_id,
            'name': task_name,
            'priority': task_priority,
            'status': task_status,
            'completed': is_completed,
            'description': '',
            'assignee': '',
            'due_date': '',
            'tags': [],
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        data['project_tasks'].append(task)
        save_data(data)
        
        return jsonify({'success': True, 'task': task})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/add_task', methods=['POST'])
@login_required
def add_task():
    data = load_data()
    
    try:
        # Récupérer les données du FormData
        task_name = request.form.get('name')
        task_priority = request.form.get('priority', 'moyenne')
        
        if not task_name:
            return jsonify({'success': False, 'error': 'Le nom de la tâche est requis'})
        
        task = {
            'id': str(uuid.uuid4()),
            'name': task_name,
            'priority': task_priority,
            'completed': False,
            'status': 'en cours',
            'created_at': datetime.now().isoformat()
        }
        data['tasks'].append(task)
        save_data(data)
        
        return jsonify({'success': True, 'task': task})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/add_note', methods=['POST'])
@login_required
def add_note_form():
    data = load_data()
    form = NoteForm()
    if form.validate_on_submit():
        note = {
            'id': str(uuid.uuid4()),
            'title': form.title.data,
            'content': form.content.data,
            'created_at': datetime.now().isoformat()
        }
        data['notes'].append(note)
        save_data(data)
        flash('Note ajoutée avec succès!')
    return redirect(url_for('notes'))

@app.route('/toggle_task/<task_id>')
@login_required
def toggle_task(task_id):
    data = load_data()
    
    # Chercher dans les tâches générales
    for task in data.get('tasks', []):
        if task['id'] == task_id:
            task['completed'] = not task.get('completed', False)
            task['status'] = 'réalisée' if task['completed'] else 'en cours'
            save_data(data)
            return redirect(url_for('taches'))
    
    # Chercher dans les tâches de projet
    for task in data.get('project_tasks', []):
        if task['id'] == task_id:
            task['completed'] = not task.get('completed', False)
            # Utiliser un statut compatible avec le Kanban
            task['status'] = 'terminé' if task['completed'] else 'a-faire'
            save_data(data)
            return redirect(url_for('taches'))
    
    return redirect(url_for('taches'))

@app.route('/api/toggle-task/<task_id>', methods=['POST'])
@login_required
def toggle_task_api(task_id):
    data = load_data()
    
    # Chercher dans les tâches générales
    for task in data.get('tasks', []):
        if task['id'] == task_id:
            task['completed'] = not task.get('completed', False)
            task['status'] = 'réalisée' if task['completed'] else 'en cours'
            save_data(data)
            return jsonify({'success': True})
    
    # Chercher dans les tâches de projet
    for task in data.get('project_tasks', []):
        if task['id'] == task_id:
            task['completed'] = not task.get('completed', False)
            # Utiliser un statut compatible avec le Kanban
            task['status'] = 'terminé' if task['completed'] else 'a-faire'
            save_data(data)
            return jsonify({'success': True})
    
    return jsonify({'success': False, 'error': 'Tâche non trouvée'})

@app.route('/api/widget-data')
@login_required
def get_widget_data():
    data = load_data()
    
    # Get tasks and sort by most recently updated (created or updated)
    tasks = data.get('tasks', [])
    # Sort by most recently updated (created_at or updated_at)
    sorted_tasks = sorted(tasks, key=lambda x: (
        datetime.fromisoformat(x.get('updated_at', x.get('created_at', '1970-01-01')))
    ), reverse=True)
    
    return jsonify({
        'tasks': sorted_tasks[:5],  # Take 5 most recent
        'events': data.get('events', [])[:10],
        'projects': data.get('projects', [])[:5],
        'mails': data.get('mails', [])[:5]
    })

@app.route('/api/add_note', methods=['POST'])
def add_note():
    data = load_data()
    form = NoteForm()
    if form.validate_on_submit():
        note = {
            'id': str(uuid.uuid4()),
            'title': form.title.data,
            'content': form.content.data,
            'created_at': datetime.now().isoformat()
        }
        data['notes'].append(note)
        save_data(data)
        flash('Note ajoutée avec succès!')
    return redirect(url_for('notes'))

@app.route('/api/add_account', methods=['POST'])
def add_account():
    data = load_data()
    form = AccountForm()
    if form.validate_on_submit():
        account = {
            'id': str(uuid.uuid4()),
            'name': form.name.data,
            'email': form.email.data,
            'created_at': datetime.now().isoformat()
        }
        data['accounts'].append(account)
        save_data(data)
        flash('Compte ajouté avec succès!')
    return redirect(url_for('comptes'))

@app.route('/api/send_mail', methods=['POST'])
def send_mail():
    data = load_data()
    form = MailForm()
    if form.validate_on_submit() and form.from_account.data and form.to_account.data:
        try:
            from_account = next(acc for acc in data['accounts'] if acc['id'] == form.from_account.data)
            to_account = next(acc for acc in data['accounts'] if acc['id'] == form.to_account.data)
            
            mail = {
                'id': str(uuid.uuid4()),
                'from': from_account['name'],
                'to': to_account['name'],
                'subject': form.subject.data,
                'content': form.content.data,
                'date': datetime.now().isoformat()
            }
            data['mails'].append(mail)
            save_data(data)
            flash('Mail envoyé avec succès!')
        except StopIteration:
            flash('Erreur: Compte non trouvé')
    return redirect(url_for('mails'))

@app.route('/api/add_call', methods=['POST'])
def add_call():
    data = load_data()
    form = CallForm()
    if form.validate_on_submit():
        call = {
            'id': str(uuid.uuid4()),
            'contact': form.contact.data,
            'date': datetime.now().isoformat()
        }
        data['calls'].append(call)
        save_data(data)
        flash('Appel ajouté avec succès!')
    return redirect(url_for('medias'))

@app.route('/api/add_message', methods=['POST'])
def add_message():
    data = load_data()
    form = MessageForm()
    if form.validate_on_submit():
        message = {
            'id': str(uuid.uuid4()),
            'contact': form.contact.data,
            'text': form.text.data,
            'date': datetime.now().isoformat()
        }
        data['messages'].append(message)
        save_data(data)
        flash('Message ajouté avec succès!')
    return redirect(url_for('medias'))

@app.route('/api/add_meeting', methods=['POST'])
def add_meeting():
    data = load_data()
    form = MeetingForm()
    if form.validate_on_submit():
        meeting = {
            'id': str(uuid.uuid4()),
            'title': form.title.data,
            'date': form.date.data.isoformat(),
            'notes': form.notes.data,
            'created_at': datetime.now().isoformat()
        }
        data['meetings'].append(meeting)
        save_data(data)
        flash('Réunion ajoutée avec succès!')
    return redirect(url_for('reunion'))

@app.route('/api/add_link', methods=['POST'])
def add_link():
    data = load_data()
    form = LinkForm()
    if form.validate_on_submit():
        link = {
            'id': str(uuid.uuid4()),
            'title': form.title.data,
            'url': form.url.data,
            'created_at': datetime.now().isoformat()
        }
        data['links'].append(link)
        save_data(data)
        flash('Lien ajouté avec succès!')
    return redirect(url_for('liens'))

@app.route('/api/upload_photo', methods=['POST'])
def upload_photo():
    if 'photo' not in request.files:
        flash('Aucun fichier sélectionné')
        return redirect(url_for('medias'))
    
    file = request.files['photo']
    if file.filename != '':
        filename = str(uuid.uuid4()) + '_' + file.filename
        filepath = app.config['UPLOAD_FOLDER'] / filename
        file.save(str(filepath))
        
        data = load_data()
        photo = {
            'id': str(uuid.uuid4()),
            'filename': filename,
            'original_name': file.filename,
            'uploaded_at': datetime.now().isoformat()
        }
        data['photos'].append(photo)
        save_data(data)
        flash('Photo uploadée avec succès!')
    
    return redirect(url_for('medias'))

@app.route('/api/delete/<item_type>/<item_id>')
def delete_item(item_type, item_id):
    data = load_data()
    if item_type in data:
        data[item_type] = [item for item in data[item_type] if item['id'] != item_id]
        save_data(data)
        flash(f'{item_type.capitalize()} supprimé avec succès!')
        
        # Mapping des types de données vers les noms de routes
        route_mapping = {
            'events': 'agenda',
            'projects': 'projets', 
            'tasks': 'taches',
            'notes': 'notes',
            'accounts': 'comptes',
            'mails': 'mails',
            'calls': 'medias',
            'messages': 'medias',
            'photos': 'medias',
            'meetings': 'reunion',
            'links': 'liens'
        }
        
        route_name = route_mapping.get(item_type, 'dashboard')
        return redirect(url_for(route_name))
    
    return redirect(url_for('dashboard'))

# Routes API pour la gestion des rôles
@app.route('/api/roles', methods=['GET'])
@login_required
def get_roles():
    """Récupérer tous les rôles personnalisables"""
    try:
        data = load_data()
        return jsonify({
            'success': True,
            'roles': data.get('roles', [])
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erreur lors de la récupération des rôles: {str(e)}'
        }), 500

@app.route('/api/roles', methods=['POST'])
@login_required
def create_role():
    """Créer un nouveau rôle personnalisé"""
    try:
        data = load_data()
        role_data = request.get_json()
        
        if not role_data or not role_data.get('name'):
            return jsonify({
                'success': False,
                'message': 'Le nom du rôle est requis'
            }), 400
        
        # Vérifier si le rôle existe déjà
        existing_role = next((role for role in data.get('roles', []) 
                            if role['name'].lower() == role_data['name'].lower()), None)
        
        if existing_role:
            return jsonify({
                'success': False,
                'message': 'Un rôle avec ce nom existe déjà'
            }), 400
        
        role = {
            'id': str(uuid.uuid4()),
            'name': role_data.get('name', '').strip(),
            'description': role_data.get('description', ''),
            'color': role_data.get('color', '#6B7280'),  # Couleur par défaut
            'permissions': role_data.get('permissions', []),  # Liste des permissions
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        data['roles'].append(role)
        save_data(data)
        
        return jsonify({
            'success': True,
            'message': 'Rôle créé avec succès!',
            'role': role
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erreur lors de la création du rôle: {str(e)}'
        }), 500

@app.route('/api/roles/<role_id>', methods=['PUT'])
@login_required
def update_role(role_id):
    """Mettre à jour un rôle existant"""
    try:
        data = load_data()
        role_index = next((i for i, role in enumerate(data.get('roles', [])) 
                          if role['id'] == role_id), None)
        
        if role_index is None:
            return jsonify({
                'success': False,
                'message': 'Rôle non trouvé'
            }), 404
        
        update_data = request.get_json()
        role = data['roles'][role_index]
        
        # Mettre à jour les champs
        if 'name' in update_data:
            # Vérifier si un autre rôle a déjà ce nom
            existing_role = next((r for r in data.get('roles', []) 
                                if r['id'] != role_id and r['name'].lower() == update_data['name'].lower()), None)
            if existing_role:
                return jsonify({
                    'success': False,
                    'message': 'Un rôle avec ce nom existe déjà'
                }), 400
            role['name'] = update_data['name'].strip()
        
        if 'description' in update_data:
            role['description'] = update_data['description']
        
        if 'color' in update_data:
            role['color'] = update_data['color']
        
        if 'permissions' in update_data:
            role['permissions'] = update_data['permissions']
        
        role['updated_at'] = datetime.now().isoformat()
        
        save_data(data)
        
        return jsonify({
            'success': True,
            'message': 'Rôle mis à jour avec succès!',
            'role': role
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erreur lors de la mise à jour du rôle: {str(e)}'
        }), 500

@app.route('/api/roles/<role_id>', methods=['DELETE'])
@login_required
def delete_role(role_id):
    """Supprimer un rôle"""
    try:
        data = load_data()
        
        # Vérifier si le rôle est utilisé par des membres
        members_with_role = [member for member in data.get('project_members', []) 
                            if member.get('role_id') == role_id]
        
        if members_with_role:
            return jsonify({
                'success': False,
                'message': 'Ce rôle est utilisé par des membres et ne peut pas être supprimé'
            }), 400
        
        # Supprimer le rôle
        data['roles'] = [role for role in data.get('roles', []) if role['id'] != role_id]
        save_data(data)
        
        return jsonify({
            'success': True,
            'message': 'Rôle supprimé avec succès!'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erreur lors de la suppression du rôle: {str(e)}'
        }), 500

# Routes API pour la gestion des membres de projet
@app.route('/api/projects/<project_id>/members', methods=['GET'])
@login_required
def get_project_members(project_id):
    """Récupérer tous les membres d'un projet"""
    try:
        data = load_data()
        members = [member for member in data.get('project_members', []) 
                  if member.get('project_id') == project_id]
        
        # Ajouter les informations des rôles
        roles = {role['id']: role for role in data.get('roles', [])}
        for member in members:
            role_id = member.get('role_id')
            if role_id and role_id in roles:
                member['role'] = roles[role_id]
            else:
                member['role'] = None
        
        return jsonify({
            'success': True,
            'members': members
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erreur lors de la récupération des membres: {str(e)}'
        }), 500

@app.route('/api/projects/<project_id>/members', methods=['POST'])
@login_required
def add_project_member(project_id):
    """Ajouter un membre à un projet"""
    try:
        data = load_data()
        member_data = request.get_json()
        
        if not member_data or not member_data.get('name'):
            return jsonify({
                'success': False,
                'message': 'Le nom du membre est requis'
            }), 400
        
        # Vérifier si le membre existe déjà dans ce projet
        existing_member = next((member for member in data.get('project_members', []) 
                               if member.get('project_id') == project_id and 
                               member.get('name', '').lower() == member_data['name'].lower()), None)
        
        if existing_member:
            return jsonify({
                'success': False,
                'message': 'Ce membre existe déjà dans le projet'
            }), 400
        
        member = {
            'id': str(uuid.uuid4()),
            'project_id': project_id,
            'name': member_data.get('name', '').strip(),
            'email': member_data.get('email', ''),
            'role_id': member_data.get('role_id'),
            'phone': member_data.get('phone', ''),
            'skills': member_data.get('skills', []),
            'availability': member_data.get('availability', 'disponible'),  # disponible, occupé, indisponible
            'joined_at': datetime.now().isoformat(),
            'notes': member_data.get('notes', '')
        }
        
        data['project_members'].append(member)
        save_data(data)
        
        # Ajouter les informations du rôle
        if member.get('role_id'):
            roles = {role['id']: role for role in data.get('roles', [])}
            if member['role_id'] in roles:
                member['role'] = roles[member['role_id']]
        
        return jsonify({
            'success': True,
            'message': 'Membre ajouté avec succès!',
            'member': member
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erreur lors de l\'ajout du membre: {str(e)}'
        }), 500

@app.route('/api/project_members/<member_id>', methods=['PUT'])
@login_required
def update_project_member(member_id):
    """Mettre à jour un membre de projet"""
    try:
        data = load_data()
        member_index = next((i for i, member in enumerate(data.get('project_members', [])) 
                           if member['id'] == member_id), None)
        
        if member_index is None:
            return jsonify({
                'success': False,
                'message': 'Membre non trouvé'
            }), 404
        
        update_data = request.get_json()
        member = data['project_members'][member_index]
        
        # Mettre à jour les champs
        if 'name' in update_data:
            member['name'] = update_data['name'].strip()
        
        if 'email' in update_data:
            member['email'] = update_data['email']
        
        if 'role_id' in update_data:
            member['role_id'] = update_data['role_id']
        
        if 'phone' in update_data:
            member['phone'] = update_data['phone']
        
        if 'skills' in update_data:
            member['skills'] = update_data['skills']
        
        if 'availability' in update_data:
            member['availability'] = update_data['availability']
        
        if 'notes' in update_data:
            member['notes'] = update_data['notes']
        
        member['updated_at'] = datetime.now().isoformat()
        
        save_data(data)
        
        # Ajouter les informations du rôle
        if member.get('role_id'):
            roles = {role['id']: role for role in data.get('roles', [])}
            if member['role_id'] in roles:
                member['role'] = roles[member['role_id']]
        
        return jsonify({
            'success': True,
            'message': 'Membre mis à jour avec succès!',
            'member': member
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erreur lors de la mise à jour du membre: {str(e)}'
        }), 500

@app.route('/api/project_members/<member_id>', methods=['DELETE'])
@login_required
def delete_project_member(member_id):
    """Supprimer un membre de projet"""
    try:
        data = load_data()
        
        # Supprimer le membre
        data['project_members'] = [member for member in data.get('project_members', []) 
                                  if member['id'] != member_id]
        save_data(data)
        
        return jsonify({
            'success': True,
            'message': 'Membre supprimé avec succès!'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erreur lors de la suppression du membre: {str(e)}'
        }), 500

# Route API pour obtenir les données de dossiers et notes
@app.route('/api/notes_data', methods=['GET'])
@login_required
def get_notes_data():
    """Obtenir les dossiers et notes pour le chargement de la page"""
    try:
        data = load_data()
        
        return jsonify({
            'success': True,
            'folders': data.get('folders', []),
            'notes': data.get('notes', [])
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erreur lors du chargement des données: {str(e)}'
        }), 500

# Route API pour synchroniser les dossiers et notes
@app.route('/api/sync_folders', methods=['POST'])
@login_required
def sync_folders():
    """Synchroniser les dossiers et notes du localStorage avec le serveur"""
    try:
        sync_data = request.get_json()
        folders = sync_data.get('folders', [])
        general_color = sync_data.get('general_color')
        
        data = load_data()
        
        # Mettre à jour les dossiers personnalisés dans data.json (PAS le dossier général)
        data['folders'] = folders
        
        # Gérer la couleur du dossier général séparément
        if general_color:
            # Créer ou mettre à jour le dossier général avec sa couleur
            general_folder = {
                'id': 'general',
                'name': 'Général',
                'color': general_color,
                'created_at': datetime.now().isoformat()
            }
            
            # Vérifier si le dossier général existe déjà et le mettre à jour
            existing_general = next((f for f in data.get('folders', []) if f.get('id') == 'general'), None)
            if existing_general:
                # Mettre à jour la couleur du dossier général existant
                for i, folder in enumerate(data['folders']):
                    if folder.get('id') == 'general':
                        data['folders'][i]['color'] = general_color
                        break
            else:
                # Ajouter le dossier général avec sa couleur
                data['folders'].append(general_folder)
            
            print(f"🎨 Couleur du dossier général mise à jour: {general_color.get('name', 'Inconnue')}")
        
        # Extraire toutes les notes des dossiers et les ajouter aux notes existantes
        existing_notes = data.get('notes', [])
        
        # Créer un set des IDs de notes existantes pour éviter les doublons
        existing_note_ids = {note.get('id') for note in existing_notes}
        
        # Ajouter les nouvelles notes des dossiers
        for folder in folders:
            if folder.get('notes'):
                for note in folder['notes']:
                    if note.get('id') and note['id'] not in existing_note_ids:
                        # S'assurer que la note a un dossier
                        note['folder'] = folder['id']
                        existing_notes.append(note)
                        existing_note_ids.add(note['id'])
        
        data['notes'] = existing_notes
        
        save_data(data)
        
        return jsonify({
            'success': True,
            'message': f'{len(folders)} dossiers personnalisés et {len(existing_notes)} notes synchronisés avec succès'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erreur lors de la synchronisation: {str(e)}'
        }), 500

# Routes pour la gestion des fichiers de projet
@app.route('/api/project/<project_id>/upload_file', methods=['POST'])
@login_required
def upload_project_file(project_id):
    """Téléverser un fichier pour un projet spécifique"""
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'Aucun fichier sélectionné'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'message': 'Aucun fichier sélectionné'}), 400
    
    print(f"Téléversement du fichier: {file.filename} pour le projet {project_id}")
    
    # Vérifier si le projet existe
    data = load_data()
    project = next((p for p in data['projects'] if p['id'] == project_id), None)
    if not project:
        return jsonify({'success': False, 'message': 'Projet non trouvé'}), 404
    
    try:
        # Sécuriser le nom du fichier
        filename = secure_filename(file.filename)
        unique_filename = f"{project_id}_{uuid.uuid4()}_{filename}"
        
        print(f"Fichier sécurisé: {filename} -> {unique_filename}")
        
        # Sauvegarder le fichier physiquement
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(file_path)
        
        print(f"Fichier sauvegardé physiquement: {file_path}")
        
        # Obtenir la taille du fichier
        file_size = os.path.getsize(file_path)
        
        # Ajouter les informations du fichier dans la base de données
        file_info = {
            'id': str(uuid.uuid4()),
            'project_id': project_id,
            'filename': unique_filename,
            'original_name': filename,
            'file_size': file_size,
            'mime_type': file.content_type or 'application/octet-stream',
            'uploaded_at': datetime.now().isoformat()
        }
        
        print(f"Infos du fichier: {file_info}")
        
        # S'assurer que project_files existe
        if 'project_files' not in data:
            data['project_files'] = []
        
        data['project_files'].append(file_info)
        
        # Vérifier avant sauvegarde
        print(f"Avant sauvegarde - Nombre total de fichiers: {len(data['project_files'])}")
        print(f"Fichier à ajouter: {file_info}")
        
        save_data(data)
        
        # Vérifier après sauvegarde
        data_check = load_data()
        project_files_after = data_check.get('project_files', [])
        print(f"Après sauvegarde - Nombre total de fichiers: {len(project_files_after)}")
        
        # Vérifier si notre fichier est bien là
        our_file = next((f for f in project_files_after if f['id'] == file_info['id']), None)
        if our_file:
            print(f"✅ Fichier trouvé dans la base: {our_file['original_name']}")
        else:
            print(f"❌ Fichier NON TROUVÉ dans la base après sauvegarde!")
        
        print(f"Fichier {filename} ajouté à la base de données")
        
        return jsonify({
            'success': True,
            'message': 'Fichier téléversé avec succès',
            'file': file_info
        })
        
    except Exception as e:
        print(f"Erreur lors du téléversement: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Erreur lors du téléversement: {str(e)}'
        }), 500

@app.route('/api/project/<project_id>/files')
@login_required
def get_project_files(project_id):
    """Récupérer la liste des fichiers d'un projet"""
    data = load_data()
    
    # Vérifier si le projet existe
    project = next((p for p in data['projects'] if p['id'] == project_id), None)
    if not project:
        return jsonify({'success': False, 'message': 'Projet non trouvé'}), 404
    
    # Récupérer les fichiers du projet
    project_files = data.get('project_files', [])
    print(f"Tous les fichiers dans la base: {len(project_files)}")
    
    project_files = [file for file in project_files if file['project_id'] == project_id]
    print(f"Fichiers pour le projet {project_id}: {len(project_files)}")
    if project_files:
        print(f"Détails des fichiers: {[f['original_name'] for f in project_files]}")
    
    return jsonify({
        'success': True,
        'files': project_files
    })

@app.route('/api/project/file/<file_id>/download')
@login_required
def download_project_file(file_id):
    """Télécharger un fichier de projet"""
    data = load_data()
    
    # Trouver le fichier
    file_info = next((f for f in data.get('project_files', []) if f['id'] == file_id), None)
    if not file_info:
        return jsonify({'success': False, 'message': 'Fichier non trouvé'}), 404
    
    try:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file_info['filename'])
        if not os.path.exists(file_path):
            return jsonify({'success': False, 'message': 'Fichier physique non trouvé'}), 404
        
        return send_file(file_path, as_attachment=True, download_name=file_info['original_name'])
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erreur lors du téléchargement: {str(e)}'
        }), 500

@app.route('/api/project/file/<file_id>/delete', methods=['DELETE'])
@login_required
def delete_project_file(file_id):
    """Supprimer un fichier de projet"""
    data = load_data()
    
    # Trouver le fichier
    file_info = next((f for f in data.get('project_files', []) if f['id'] == file_id), None)
    if not file_info:
        return jsonify({'success': False, 'message': 'Fichier non trouvé'}), 404
    
    try:
        # Supprimer le fichier physique
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file_info['filename'])
        if os.path.exists(file_path):
            os.remove(file_path)
        
        # Supprimer l'entrée de la base de données
        data['project_files'] = [f for f in data['project_files'] if f['id'] != file_id]
        save_data(data)
        
        return jsonify({
            'success': True,
            'message': 'Fichier supprimé avec succès'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erreur lors de la suppression: {str(e)}'
        }), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
