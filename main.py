import os
from pathlib import Path
from flask import Flask, request, render_template, redirect, flash, url_for,abort,send_from_directory,send_file
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from backend import *  # Importation des fonctions backend

app = Flask(__name__)
app.secret_key = "azerty"

# SQLAlchemy (module de Flask) + configuration nécessaire
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://admin:azerty@localhost/website'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class UserSQLTable(db.Model):  # Représentation de la table 'user' de MySQL
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    last_login = db.Column(db.DateTime, nullable=True)
    role = db.Column(db.Enum('user', 'admin', 'dev'), default='user')
    profile_picture = db.Column(db.String(255))  # Assurez-vous que la longueur correspond
    bio = db.Column(db.Text)  # Ajout du champ bio pour correspondre à votre table MySQL
    is_active = db.Column(db.Boolean, default=True)  # Ajout de is_active si nécessaire
    nom = db.Column(db.String(50))
    prenom = db.Column(db.String(50))

    def __repr__(self):
        return f'<User {self.username}>'

    def __str__(self):
        return str([self.id, self.username, self.email, self.password, self.created_at])

class GameSQLTable(db.Model):  # Représentation de la table 'games' de MySQL
    __tablename__ = 'games'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    tags = db.Column(db.String(255), nullable=True)
    image_url = db.Column(db.String(255), nullable=True)
    file_url = db.Column(db.String(255), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Clé étrangère vers la table 'user'

    user = db.relationship('UserSQLTable', backref='games', lazy=True)

    def __repr__(self):
        return f'<Game {self.title}>'

    def __str__(self):
        """Affichage des données du jeu avec émojis pour un debug visuel."""
        separator = "\n" + "=" * 40 + "\n"
        game_info = (
            f"🎮 Nom du jeu : {self.title}\n"
            f"📝 Description : {self.description[:50]}{'...' if len(self.description) > 50 else ''}\n"
            f"🏷️ Tags : {self.tags if self.tags else 'Aucun'}\n"
            f"🖼️ Image URL : {self.image_url if self.image_url else 'Pas d\'image'}\n"
            f"📂 Fichier URL : {self.file_url}\n"
            f"👤 Développeur (ID) : {self.user_id}\n"
        )
        return separator + game_info + separator

class WebsiteUser:
    """Classe représentant l'utilisateur du site web."""

    def __init__(self):
        """Initialisation des données de l'utilisateur avec des valeurs par défaut."""
        self.isLogged = False
        self.data = {  # Dictionnaire contenant les données utilisateur
            'id': None,
            'username': None,
            'email': None,
            'password': None,
            'created_at': None,
            'last_login': None,
            'nom': None,
            'prenom': None,
            'profile_picture': None,
            'bio': None,
            'is_active': None,
            'role': None
        }

    def userLogged(self):
        """Retourne le statut de connexion de l'utilisateur."""
        return self.isLogged

    def returnUserDatas(self):
        """Retourne le statut de connexion et les données de l'utilisateur."""
        return {'isLogged': self.isLogged, 'data': self.data}

    def updateUserData(self, datas: dict, logged: bool):
        """Met à jour les données utilisateur à partir d'un dictionnaire."""
        print(datas)
        self.isLogged = logged
        self.data.update(datas)

    def __str__(self):
        """Affichage des données de l'utilisateur."""
        if self.isLogged == False:
            return  f" {"="*40} \n 🔒 Status: {'Connected' if self.isLogged else 'Disconnected'}\n {"="*40}"
        else :
            separator = "\n" + "=" * 40 + "\n"
            user_info = (
                    f"🔒 Status: {'Connected' if self.isLogged else 'Disconnected'}\n"
                    f"🆔 ID: {self.data["id"]}\n"
                    f"👤 Username: {self.data["username"]}\n"
                    f"📧 Email: {self.data["email"]}\n"
                    f"🔑 Password: {self.data["password"]}\n"
                    f"📅 Created At: {self.data["created_at"]}\n"
                    f"Last loggin: {self.data["last_login"]}\n"
                    f"👨‍💼 Name: {self.data["nom"]} | {self.data["prenom"]}\n"
                    f"🖼️ Profile Picture: {self.data["profile_picture"]}\n"
                    f"📝 Bio: {self.data["bio"]}\n"
                    f"🟢 Active: {'Yes' if self.data["is_active"] else 'No'}\n"
                    f"🛠️ Role: {self.data["role"]}\n"
                )
            
            return separator + user_info + separator

# Création de la base de données (si elle n'existe pas déjà)
with app.app_context():
    db.create_all()

websiteClient = WebsiteUser()
print(websiteClient)

@app.route('/protected', methods=['GET', 'POST'])
def protectedPage():
    """Page protégée accessible uniquement si l'utilisateur est connecté."""
    if websiteClient.userLogged():
        print('user logged')
        return "user logged"
    else:
        print('user not logged !')
        return "user not logged"

@app.route('/profile', methods=['GET', 'POST'])
def profilePage():
    """Page de profil de l'utilisateur."""
    print(websiteClient)
    if websiteClient.userLogged():
        print('user logged')
        return render_template('profile.html', data=websiteClient.returnUserDatas())
    else:
        print('user not logged !')
        return render_template('profile.html', data=websiteClient.returnUserDatas())

def dicoTags(tags: str):
    """Sépare une chaîne de tags en une liste."""
    tagsdico = tags.split(',')  # Utilise split pour découper la chaîne par les virgules
    tagsdico = [tag.strip() for tag in tagsdico]  # Enlève les espaces superflus autour des tags
    return tagsdico

@app.route('/games', methods=['GET','POST'])
def games():
    games_query = GameSQLTable.query.all()
    
    # Convertir SQLAlchemy en dictionnaires pour l'affichage
    games_list = [
        {
            'id': game.id,
            'title': game.title,
            'description': game.description,
            'tags': dicoTags(game.tags),
            'image_url':game.image_url,
            'file_url': game.file_url
        }
        for game in games_query
    ]
    
    return render_template('games.html', games=games_list)

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Page d'inscription d'un utilisateur."""
    if request.method == 'POST':
        Username = request.form.get('username')
        Role = request.form.get('role')
        Email = request.form.get('email')
        Pwd = request.form.get('password')
        Nom = request.form.get('nom')
        Prenom = request.form.get('prenom')
        Bio = request.form.get('bio')
        Profile_picture = request.files.get('profile_picture')
        Profile_picture.filename = cleanFilePath(Profile_picture.filename)

        # Vérifier si le fichier est bien reçu
        if Profile_picture:
            profile_picture_path = f"static/uploads/profil_pics/{Profile_picture.filename}"
            Profile_picture.save(profile_picture_path)
        else:
            profile_picture_path = None

        try:
            # Ajouter l'utilisateur dans la base de données
            new_user = UserSQLTable(
                username=Username,
                email=Email,
                password=Pwd,
                nom=Nom,
                prenom=Prenom,
                bio=Bio,
                profile_picture=profile_picture_path,
                role=Role
            )
            db.session.add(new_user)
            db.session.commit()
            flash("Compte créé avec succès !", "success")
            
        except SQLAlchemyError as e:
            db.session.rollback()
            flash("Un compte utilisant ce nom ou cette adresse mail existe déjà", "danger")
            return render_template("register.html") 

    return render_template("register.html")
    
@app.route('/login', methods=['GET', 'POST'])
def login():
    """Page de connexion de l'utilisateur."""
    if request.method == 'POST':
        login = request.form.get('login')
        pwd = request.form.get('pwd')
        message = f"Formulaire soumis avec : Nom = {login}, Email = {pwd}"
        print(message)
        try:
            query = text("SELECT * FROM user WHERE username = :username")
            user = db.session.execute(query, {"username": login}).mappings().first()  # Retourne un dict
            if user and user['password'] == pwd:  # Vérifie que le mot de passe est correct
                flash("Login réussi !", "success")
                websiteClient.updateUserData(user, logged=True)
                print(websiteClient)
                return render_template('login.html')  
            else:
                flash("Nom d'utilisateur ou mot de passe incorrect.", "danger")
        except SQLAlchemyError as e:
            print(e)
            flash("Erreur lors de la connexion à la base de données.", "danger")
        
        return render_template('login.html')
    
    return render_template('login.html')

@app.route('/', methods=['GET', 'POST'])
def index():
    """Page d'accueil."""
    return render_template("index.html")

# Chemin du dossier où les fichiers seront stockés
UPLOAD_FOLDER = os.path.join(os.getcwd(), "Games")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route("/upload", methods=["GET", "POST"])
def upload_game():
    """Page pour télécharger un jeu."""
    if request.method == "POST":
        if 'file' not in request.files:
            flash("Aucun fichier sélectionné.", "danger")
            return redirect(request.url)

        if websiteClient.isLogged == False:
            flash("Vous devez être connecté pour publier votre jeu ! .", "danger")
            return redirect(request.url)

        # Récupération des données du formulaire
        file = request.files['file']
        name = request.form.get('nom')
        descript = request.form.get('descript')
        tags = request.form.get('tags')
        image_url = request.form.get('image_url')

        if file.filename == '':
            flash("Aucun fichier sélectionné.", "danger")
            return redirect(request.url)

        # Sauvegarde du fichier en local
        if file:
            clean_name = cleanFilePath(name)
            clean_local_path = cleanFilePath(f"{UPLOAD_FOLDER}/{clean_name}")
            os.makedirs(clean_local_path, exist_ok=True)

            file_path = os.path.join(clean_local_path, file.filename)
            file.save(file_path)

            # Insérer les données dans la table 'games'
            new_game = GameSQLTable(
                title=name,
                description=descript,
                tags=tags,
                image_url=image_url,
                file_url=file_path,
                user_id=websiteClient.data["id"]
            )
            db.session.add(new_game)
            db.session.commit()

            flash(f"Jeu '{name}' téléchargé et ajouté à la base de données avec succès !", "success")
            return redirect(request.url)

    return render_template("upload.html")

DOWNLOAD_FOLDER = 'files'
app.config['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER

@app.route('/download/<int:game_id>', methods=['GET'])
def download_file(game_id):
    """Génère le fichier d'un fichier spécifique."""
    game = GameSQLTable.query.get(game_id)
    if game is None:
        return "Jeu non trouvé", 404
    
    file_path = game.file_url  
    print(file_path)
    try:
        return send_file(file_path, as_attachment=True)
    except FileNotFoundError:
        return "Fichier non trouvé", 404

@app.route('/game/<int:game_id>', methods=['GET'])
def game_detail(game_id):
    """Affiche les détails d'un jeu spécifique."""
    game = GameSQLTable.query.get(game_id)  # Requête pour récupérer le jeu par son ID
    
    if not game:
        return render_template('gameError.html')

    return render_template('game_detail.html', game=game)

if __name__ == "__main__":
    app.run(debug=True)

#http://172.23.252.12/
# IP Barrois : 172.23.252.144