from flask import *
import psycopg2
from macros import *
import hashlib

#Constante de connexion à la base de donnees
str_conn = "dbname=afaugas user=afaugas host=dbserver"
#str_conn = "dbname=rallyx user=rallyx password="



""" BLOC FONCTIONS DE LA PAGE GUEST """
def chiffrage_password(password):
    password = password.encode()
    return str(hashlib.sha512(password).hexdigest())

#INSCRIPTION
def register(username, password, password2):
    #Gestion des erreur d'inscription possible
    if len(username) < 3 and len(username) > 15:
        flash("Votre nom d'utilisateur doit contenir au moins 3 et au plus 15 caractères.")
        return redirect(url_for('guest'))
    elif password != password2:
        flash("Les deux mots de passe doivent être identiques.")
        return redirect(url_for('guest'))
    elif len(password) < 6 :
        flash("Votre mot de passe doit contenir au moins 6 caractères.")
        return redirect(url_for('guest'))

    #si tout est bon, on inscrit le bonhomme.
    else:
        try:
            username = username.replace("\\", "\\\\")

            conn = psycopg2.connect(str_conn)
            cur = conn.cursor()
            selUser = "select * from users where username = '" + username.replace("'","\\'") + "';"

            rows = execute_request(cur, selUser)
            #si l'utilisateur n'est pas déjà dans la bd, on inscrit.
            if rows == []:
                password_crypt = chiffrage_password(password)
                insert = "insert into users(username, password) values ('"+ username.replace("'","\\'") +"','"+ password_crypt +"');"

                cur.execute(insert)
                conn.commit()

                disconnect_db(cur, conn)
                #on connecte l'utilisateur (pour les sessions)
                return connect(username, password)

            flash("Sorry, vous avez déjà un compte chez nous.")
            disconnect_db(cur, conn)
            return redirect(url_for('guest'))

        except Exception as e:
            return str(e)

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
            username = username.replace("\\", "\\\\")

            selUser = "select * from users where username = '" + username.replace("'","\\'") + "' and password= '" + password_crypt + "';"

            rows = execute_request(cur, selUser)
            disconnect_db(cur, conn)
            #si l'utilisateur apparait dans la bd, on connecte
            if rows != []:

                if rows[0][6] == 1:
                    flash("Vous êtes banni !")
                    return redirect(url_for('guest'))

                #variables de session (évite d'aller chercher les infos de l'utilisateur tout le temps)
                session["user_id"] = rows[0][0]
                session["username"] = rows[0][1]
                session["nb_messages"] = rows[0][3]
                session["txt_color"] = rows[0][4]
                session["grade"] = rows[0][5]

                return redirect(url_for('home', action=''))
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
        return redirect(url_for('home', action=''))

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

            return redirect(url_for('home', action=""))

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
    request = "SELECT messages.*, users.username, users.txt_color, users.grade, users.ban FROM messages inner join users on users.id = messages.user_id WHERE messages.id between \'" + str(row[0][0]-nb_messages) + "' and '"+ str(row[0][0]) + "' order by messages.id asc;"
    cur.execute(request)
    rows_messages = cur.fetchall()
    disconnect_db(cur, conn)

    length = len(rows_messages)
    rows_messages = list(rows_messages)
    try :
        for i in range(length):
            rows_messages[i] = list(rows_messages[i])
            date = rows_messages[i][3].strftime('%H:%M')
            rows_messages[i][3] = date
    except Exception as e :
        return str(e)
    #redirige l'utilisateur vers l'index, avec les messages à afficher dans un tableau
    return render_template("index.html", messages=rows_messages)


def sendPrivate(message, receiver_id):
    if len(message) < 1:
        flash("Impossible d'envoyer un message vide.")
        return redirect(url_for('private', action=receiver_id))

    #on envoie le message
    else:
        conn = psycopg2.connect(str_conn)
        cur = conn.cursor()
        #évite les injections sql
        message = message.replace("\\", "\\\\")

        #on utilise les variables de session
        insert = "insert into discussions(sender_id, receiver_id, message) \
        values (" + str(session['user_id']) + ", " + str(receiver_id) + ", \'" + message.replace("'","\\'") + "\');"

        try:
            cur.execute(insert)
            conn.commit()
            disconnect_db(cur, conn)

            return redirect(url_for('private', action=receiver_id))

        except Exception as e:
            return str(e)

def display_private(contact_id):
    try:
        contact_id = int(contact_id)
    except Exception as e:
        return redirect(url_for('private', action='0'))

    conn = psycopg2.connect(str_conn)
    cur = conn.cursor()

    #on prend la table messages, et les username, la couleur des textes, et le grade des utilisateurs.
    #request = "SELECT discussions.*, users.username, users.txt_color, users.grade FROM discussions inner join users on users.id = discussions.sender_id WHERE messages.id between \'" + str(row[0][0]-nb_messages) + "' and '"+ str(row[0][0]) + "' order by messages.id asc;"
    select = "SELECT id, username from users where id = \'" + str(contact_id) + "\';"
    cur.execute(select)
    row = cur.fetchall()

    if row != []:
        request = "SELECT D.*, S.username, S.txt_color, S.grade, R.username, R.txt_color, R.grade FROM discussions D, users S, users R where S.id = " + str(session["user_id"]) + " and R.id = " + str(contact_id) + " and ((D.sender_id = S.id and D.receiver_id = R.id) or (D.sender_id = R.id and D.receiver_id = S.id)) ORDER BY D.id asc;"
        cur.execute(request)
        rows_messages = cur.fetchall()
        disconnect_db(cur, conn)

        length = len(rows_messages)
        rows_messages = list(rows_messages)
        try :
            for i in range(length):
                rows_messages[i] = list(rows_messages[i])
                date = rows_messages[i][4].strftime('%H:%M')
                rows_messages[i][4] = date
        except Exception as e :
            return str(e)
        #redirige l'utilisateur vers la page de messagerie privée, avec les messages à afficher dans un tableau
        return render_template("private.html", messages=rows_messages, receiver=row[0][1], receiver_id=row[0][0])

    return redirect(url_for('private', action=''))

def display_users():
    conn = psycopg2.connect(str_conn)
    cur = conn.cursor()

    select = "SELECT id, username FROM users ORDER BY username asc"
    cur.execute(select)
    rows = cur.fetchall()

    return render_template('users_list.html', users=rows)


""" BLOC FONCTIONS PAGE PREFERENCES """
def usernameModif(username):
    if len(username) < 3:
        flash("Vous devez choisir un nom d'utilisateur d'au moins 3 caractères.")
        return redirect(url_for('preferences', action=''))

    try:
        conn = psycopg2.connect(str_conn)
        cur = conn.cursor()

        username = username.replace("\\", "\\\\")

        session["username"] = username.replace("'","\\'")

        alter = "update users set username = '" + username.replace("'","\\'") + "' where id = " + str(session["user_id"]) + ";"
        cur.execute(alter)
        conn.commit()

        disconnect_db(cur, conn)

    except Exception as e:
        return str(e)
    return redirect(url_for('preferences', action=''))

def passModif(oldpass, newpass, newpass2):
    if newpass != newpass2:
        flash("Les deux champs de mot de passe doivent être identiques.")
        return redirect(url_for('preferences', action=''))
    elif oldpass == newpass:
        flash("L'ancien et le nouveau mot de passe sont les mêmes...")
        return redirect(url_for('preferences', action=''))
    elif len(newpass) < 6:
        flash("Votre nouveau mot de passe doit contenir au moins 6 caractères.")
        return redirect(url_for('preferences', action=''))

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
    return redirect(url_for('preferences', action=''))

def apparenceModif(nb_mess, color):
    try:
        conn = psycopg2.connect(str_conn)
        cur = conn.cursor()

        #on modifie la session "nb_messages"
        session["nb_messages"] = int(nb_mess)
        session["txt_color"] = color

        #puis on modifie la table users pour l'utilisateur concerné
        alter = "update users set nb_messages = " + nb_mess + ", txt_color = '" + color + "' where id = " + str(session["user_id"]) + ";"
        cur.execute(alter)
        conn.commit()

        disconnect_db(cur, conn)

    except Exception as e:
        return str(e)
    return redirect(url_for('preferences', action=''))


""" BLOC DES FONCTION DE L'ADMINISTRATEUR """

def supprimer_message(id_message):
    """ Fonction qui permet d'update la table message en remplacant le
    message dont l'id est id_message par un message predefinie.
    La fonction est executee par l'utilisateur id_user_admin. On verfie d'abord
    s'il a les droit d'administrateur pour plus de securite. """
    conn = psycopg2.connect(str_conn)
    cur = conn.cursor()

    cur.execute("UPDATE messages SET suppr = 1 WHERE id=" + str(id_message) + ";")
    conn.commit()

    disconnect_db(cur, conn)
    return redirect(url_for('home', action=''))

def get_users_admin():
    conn = psycopg2.connect(str_conn)
    cur = conn.cursor()

    cur.execute("SELECT * FROM users ORDER BY username asc;")

    rows = cur.fetchall()

    disconnect_db(cur, conn)
    return render_template('admin.html', users=rows)

def ban(user_id, ban):
    conn = psycopg2.connect(str_conn)
    cur = conn.cursor()

    cur.execute("UPDATE users SET ban = " + str(ban) + " WHERE id = " + str(user_id) + ";")
    conn.commit()

    disconnect_db(cur, conn)
    return redirect(url_for('admin', action=''))
