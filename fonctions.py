from flask import *
import psycopg2
from macros import *
import hashlib

#Constantes de connexion à la base de donnees
# CREMI
str_conn = "dbname=bande001 user=bande001 host=dbserver"
# LOCAL LINUX PC (rallyx's PC)
#str_conn = "dbname=rallyx user=rallyx password="

def chiffrage_password(password):
    password = password.encode()
    return str(hashlib.sha1(password).hexdigest())

""" BLOC FONCTIONS DE LA PAGE GUEST """
#INSCRIPTION
def register(username, password, password2):
    #Gestion des erreur d'inscription possible
    if len(username) < 3 or len(username) > 15:
        flash("Votre nom d'utilisateur doit contenir au moins 3 et au plus 15 caractères.")
        return redirect(url_for('guest'))
    elif password != password2:
        flash("Les deux mots de passe doivent être identiques.")
        return redirect(url_for('guest'))
    #Pas de taille max du password
    #La probabilité de colisions en SHA1 son faibles.
    elif len(password) < 6 :
        flash("Votre mot de passe doit contenir au moins 6 caractères.")
        return redirect(url_for('guest'))

    #si tout est bon, on inscrit le bonhomme.
    else:
        try:
            conn = psycopg2.connect(str_conn)
            cur = conn.cursor()
        except Exception as e:
            return str(e)
        selUser = "select * from users where username = '" + username + "';"
        rows = execute_request(cur, selUser)
        #si l'utilisateur n'est pas déjà dans la bd, on inscrit.
        if rows == []:
            password_crypt = chiffrage_password(password)
            insert = "insert into users(username, password) values ('"+ username +"','"+ password_crypt +"');"

            cur.execute(insert)
            conn.commit()

            disconnect_db(cur, conn)
            #on connecte l'utilisateur (pour les sessions)
            return connect(username, password)

    flash("Sorry, vous avez déjà un compte chez nous.")
    disconnect_db(cur, conn)
    return redirect(url_for('guest'))


#CONNEXION
def connect(username, password):
    #évite de faire une requête dans la base de données pour rien...
    if len(username) < 3 or len(password) < 6:
        flash("Nom d'utilisateur ou mot de passe erroné.")
        return redirect(url_for('guest'))

    #on connecte le bonhomme.
    else:
        try:
            conn = psycopg2.connect(str_conn)
            cur = conn.cursor()

            password_crypt = chiffrage_password(password)
            selUser = "select * from users where username = '" + username + "' and password= '" + password_crypt + "';"

            rows = execute_request(cur, selUser)
            disconnect_db(cur, conn)
            #si l'utilisateur apparait dans la bd, on connecte
            if rows != []:
                #variables de session (évite d'aller chercher les infos de l'utilisateur tout le temps)
                session["user_id"] = rows[0][0]
                session["username"] = rows[0][1]
                session["nb_messages"] = rows[0][3]
                session["txt_color"] = rows[0][4]
                session["grade"] = rows[0][5]

                return redirect(url_for('index', action="/"))
            flash("Nom d'utilisateur ou mot de passe erroné.")
            return redirect(url_for('guest'))

        except Exception as e:
            return str(e)

#DECONNEXION
def disconnect():
    #supprime toutes les sessions
    session.pop('user_id', None)
    session.pop('username', None)
    session.pop('nb_messages', None)
    session.pop('txt_color', None)
    session.pop('grade', None)
    return redirect(url_for('guest'))

""" BLOC FONCTIONS RELATIVES AUX MESSAGES """
#ENVOI D'UN MESSAGE
def sendMessage(message):
    if len(message) < 1:
        flash("Impossible d'envoyer un message vide.")
        return redirect(url_for('index', action='/'))

    #on envoie le message
    else:
        conn = psycopg2.connect(str_conn)
        cur = conn.cursor()
        #évite les injections sql
        message = message.replace("\\", "\\\\")

        #on utilise les variables de session
        insert = "insert into messages(user_id, message) \
        values (" + str(session['user_id']) + ", \'" + message.replace("'","\\'") + "\');"

        try:
            cur.execute(insert)
            conn.commit()
            disconnect_db(cur, conn)

            return redirect(url_for('index', action="/"))

        except Exception as e:
            return str(e)

#AFFICHAGE DES MESSAGES
def display_messages():
    conn = psycopg2.connect(str_conn)
    cur = conn.cursor()

    #selectionne l'id du dernier message
    select_val = "select last_value from messages_id_seq;"
    cur.execute(select_val)
    row = cur.fetchall()

    if session["nb_messages"] > 0:
        nb_messages = session["nb_messages"]-1
    else :
        nb_messages = row[0][0]-1

    #on prend la table messages, et les username, la couleur des textes, et le grade des utilisateurs.
    request = "SELECT messages.*, users.username, users.txt_color, users.grade FROM messages inner join users on users.id = messages.user_id WHERE messages.id between \'" + str(row[0][0]-nb_messages) + "' and '"+ str(row[0][0]) + "' order by messages.id asc;"
    cur.execute(request)
    rows_messages = cur.fetchall()
    disconnect_db(cur, conn)

    length = len(rows_messages)
    rows_messages = list(rows_messages)

    # Convert timestamp to str(%HOUR:%MINUTES) format
    # Waste of ressources, is it worth ? Ask B. Pinaud
    # Maybe change the nb_max of displayed message
    for i in range(length):
        rows_messages[i] = list(rows_messages[i])
        date = rows_messages[i][3].strftime('%H:%M')
        rows_messages[i][3] = date

    #redirige l'utilisateur vers l'index, avec les messages à afficher dans un tableau
    return render_template("index.html", messages=rows_messages)

""" BLOC FONCTIONS PAGE PREFERENCES """
def usernameModif(username):
    if len(username) < 3:
        flash("Vous devez choisir un nom d'utilisateur d'au moins 3 caractères.")
        return redirect(url_for('index', action='preferences'))

    try:
        conn = psycopg2.connect(str_conn)
        cur = conn.cursor()

        session["username"] = username

        alter = "update users set username = '" + username + "' where id = " + str(session["user_id"]) + ";"
        cur.execute(alter)
        conn.commit()

        disconnect_db(cur, conn)

    except Exception as e:
        return str(e)
    return redirect(url_for('index', action='preferences'))

def passModif(oldpass, newpass, newpass2):
    if newpass != newpass2:
        flash("Les deux champs de mot de passe doivent être identiques.")
        return redirect(url_for('index', action='preferences'))
    elif oldpass == newpass:
        flash("L'ancien et le nouveau mot de passe sont les mêmes...")
        return redirect(url_for('index', action='preferences'))
    elif len(newpass) < 6:
        flash("Votre nouveau mot de passe doit contenir au moins 6 caractères.")
        return redirect(url_for('index', action='preferences'))

    try:
        conn = psycopg2.connect(str_conn)
        cur = conn.cursor()

        select = "select password from users where id = " + str(session["user_id"]) + ";"
        cur.execute(select)
        row = cur.fetchall()

        if row != []:
            if (row[0][0] == chiffrage_password(oldpass)):
                alter = "update users set password = '" + chiffrage_password(newpass) + "' where id = " + str(session["user_id"]) + ";"
                cur.execute(alter)
                conn.commit()

                disconnect_db(cur, conn)
            else:
                flash("Votre ancien mot de passe n'est pas valide.")

    except Exception as e:
        return str(e)
    return redirect(url_for('index', action='preferences'))

def apparenceModif(nb_mess, color):
    try:
        conn = psycopg2.connect(str_conn)
        cur = conn.cursor()

        #on modifie la session "nb_messages"
        session["nb_messages"] = int(nb_mess)
        session["txt_color"] = color

        #puis on modifie la table users pour l'utilisateur concerné
        alter = "update users set nb_messages = " + nb_mess + ", txt_color = '" + color + "' where id = " + str(session["user_id"]) + ";"
        print(color)
        cur.execute(alter)
        conn.commit()

        disconnect_db(cur, conn)

    except Exception as e:
        return str(e)
    return redirect(url_for('index', action='preferences'))


""" BLOC DES FONCTION DE L'ADMINISTRATEUR """

def is_admin(id_user, cur):
    """ Fonction qui determine si l'utilisateur a le grade administrateur
    ou si c'est un utilisateur lambda """
    try :
        conn = psycopg2.connect(str_conn)
        cur = conn.cursor()

        request = "SELECT grade FROM users WHERE id=" + str(id_user) + ";"
        row = execute_request(cur, request)

        disconnect_db(cur, conn)
        if row[0][0] == 1 :
            return True
        return False
    except Exception as e:
        return str(e)

def supprimer_message(id_message, id_user_admin):
    """ Fonction qui permet d'update la table message en remplacant le
    message dont l'id est id_message par un message predefinie.
    La fonction est executee par l'utilisateur id_user_admin. On verfie d'abord
    s'il a les droit d'administrateur pour plus de securite. """
    conn = psycopg2.connect(str_conn)
    cur = conn.cursor()
    if (is_admin(id_user, cur) == False) :
        flash("Vous n'etes pas administrateur, vous ne pouvez pas faire ça")
    else :
        cur.execute("UPDATE message SET \"Ce message a ete supprime.\" WHERE id=" + str(id_message) + ";")
        conn.commit()
    disconnect_db(cur, conn)
    return redirect(url_for('index'))
