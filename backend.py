# ===== IMPORTS =====
import mysql.connector
import time


# ===============================================
#               SQL FUNCTIONS
# ===============================================

# === connect DB ===
conn = mysql.connector.connect(
    host="localhost",
    user="admin",
    password="azerty",
    database="website"
)
conn.autocommit = True
cursor = conn.cursor()
# Créer la table si elle n'existe pas
try:
    cursor.execute("""
CREATE TABLE user (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_login DATETIME DEFAULT NULL,
    role ENUM('user', 'admin') DEFAULT 'user',
    profile_picture VARCHAR(255) DEFAULT NULL,
    bio TEXT DEFAULT NULL,
    is_active BOOLEAN DEFAULT TRUE);
    """)
except mysql.connector.Error as error:
    print(f"Error creating table: {error}")

def RecupDatas(sqlQuerry):
    try:
        cursor = conn.cursor()
        cursor.execute(sqlQuerry)
        result = cursor.fetchall()
        # si pas résultat, renvoyer None
        if not result:
            return None
        return result
    except mysql.connector.Error as error:
        print(f"Error fetching data: {error}")
        return None  # Retourner None en cas d'erreur pour éviter les plantages ailleurs

def GetTime(request: str):
    try:
        cursor.execute(f""" {request}""")
        result = cursor.fetchall()
        return result[0]
    except mysql.connector.Error as error:
        print(f"Error getting time: {error}")

# ==== Fonctions à modifier par rapport au contnu de la BD ==== 
"""
def AddDatas(serie_number, porte_numero, date_entree, date_sortie):
    try:
        sql = "
            INSERT INTO badges (serie_number, porte_numero, date_entree, date_sortie)
            VALUES (%s, %s, %s, %s)"
        # Données à insérer
        date_entree = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        date_sortie = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        user = (serie_number, porte_numero, date_entree, date_sortie)
        cursor.execute(sql, user)
        conn.commit()
        print("Données insérées avec succès.")
    except mysql.connector.Error as error:
        print(f"Error inserting data: {error}")

def ShowTableContent(sqlquerry, params=None):
    try:
        table = Table(title="Contenu de la table badges")

        # Si des paramètres sont fournis, utiliser une requête paramétrée
        if params:
            cursor.execute(sqlquerry, params)
        else:
            cursor.execute(sqlquerry)
        a = cursor.fetchall()

        # Vérification si la table est vide
        if not a:
            console.print("[bold yellow]Aucune donnée trouvée[/bold yellow]")
            return

        # Ajout des colonnes à la table avec le background stylisé en jaune fluo pour l'id
        table.add_column("id", style="bold on bright_yellow", justify="center")
        table.add_column("serie_number")
        table.add_column("porte_numero")
        table.add_column("date_entree")
        table.add_column("date_sortie")

        # Remplissage des lignes de la table avec les données récupérées
        for elt in a:
            id = f"[bold on bright_yellow]{str(elt[0])}[/bold on bright_yellow]"  # Background jaune fluo pour l'ID
            serie_number = str(elt[1])
            porte_numero = str(elt[2])
            date_entree = str(elt[3])
            date_sortie = str(elt[4])
            table.add_row(id, serie_number, porte_numero, date_entree, date_sortie)

        console.print(table)

    except mysql.connector.Error as error:
        # Vérification du code d'erreur pour une colonne inconnue
        if error.errno == 1054:
            console.print("Erreur : Colonne inconnue dans la clause WHERE", style="red")
            console.print("[bold yellow]Aucune donnée trouvée[/bold yellow]")
            time.sleep(3)
        else:
            print(f"Error displaying table content: {error}")

"""

# ===============================================
#               UPLOAD FUNCTIONS
# ===============================================

def cleanFilePath(path:str):
    """Retourne le chemin d'accès avec des "_" à la place des " " pour éviter les platages liés au chemin d'accès"""
    return path.replace(" ", "_")

# ===============================================
#               SQL ALCHEMY NOTES
# ===============================================
"""
ajouter un user : 
new_user = User(username='GalaxyShadow', email='thomas@example.com', password='hashed_password')
db.session.add(new_user)
db.session.commit()

lire des données :
users = User.query.all()  # Récupère tous les utilisateurs
user = User.query.filter_by(username='GalaxyShadow').first()  # Filtre par username

mettre à jour des données 
user = User.query.filter_by(username='GalaxyShadow').first()
user.email = 'new_email@example.com'
db.session.commit()

supprimer un utilisateur :
user = User.query.filter_by(username='GalaxyShadow').first()
db.session.delete(user)
db.session.commit()
"""
