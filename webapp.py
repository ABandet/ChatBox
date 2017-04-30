# Doc psycopg2 : http://initd.org/psycopg/docs/index.html
# Flask : https://openclassrooms.com/courses/creez-vos-applications-web-avec-flask

import time
from flask import *
import sys
import psycopg2
from macros import *
from fonctions import *

#NE PAS MODIFIER LA LIGNE SUIVANTE
app = Flask(__name__)
#SECRET_KEY sert pour les sessions et messages flash
app.secret_key = '5f4FEtt-64+*ùFeiuhz1563§!d2kfr£µ'

##########LIGNES REPETEES#############
#redirect(url_for('guest')) : redirige l'utilisateur non connecté vers l'accueil visiteur (inscription/connexion)
#redirect(url_for('index', action="/")) : redirection vers l'accueil connectés (si pas connecté, vers accueil visiteur)
#   la page vers laquelle on est redirigé appelle display_messages() qui renvoie vers l'accueil avec les messages
#conn.commit() : pour update/insert (remove ?) dans bd
#if request.method="POST" : vérifie si on envoie un formulaire par POST
#######################

#BASE DU SITE
@app.route("/")
def guest():
    #vérifie si l'utilisateur est connecté (si le champ 'username' est dans le dictionnaire session)
    if 'username' in session:
        try :
            #on essaie d'afficher les messages
            return display_messages()
        except Exception as e :
            #Si cela ne marche pas on détruit la session
            return disconnect()
    #sinon, on redirige vers la page d'accueil visiteur
    return render_template("guestIndex.html")

#RESTE DU SITE
@app.route("/<action>", methods=["POST", "GET"])
#INDEX DU SITE
def index(action):
    #SI CONNECTÉ, ACCÈS AU SITE
    if 'username' in session:
        #envoyer un message
        if action == "sendMess":
            message = request.form['message']
            return sendMessage(message)

        #revenir à l'accueil
        elif action == "accueil":
            return redirect(url_for('guest'))
        #se déconnecter
        elif action == "disconnect":
            return disconnect()

        #page preferences
        #A FAIRE
        elif action == "preferences":
            return render_template('preferences.html')

        elif request.method == "POST":
            if action == "usernameModif":
                return usernameModif(request.form["username"])

            elif action == "passModif":
                return passModif(request.form["oldpass"], request.form["newpass"], request.form["newpass2"])

            elif action == "apparenceModif":
                return apparenceModif(request.form["nb_mess"], request.form["color"])
        #SI PAS DE "action", ON REDIRIGE VERS L'ACCUEIL CONNECTÉ
        return display_messages()

    #SINON, TRAITE LES INSCRIPTIONS/CONNEXIONS OU RENVOIE VERS ACCUEIL VISITEUR
    else:
        #traite la connexion et l'inscription
        if request.method == "POST":
            if action == "connexion":
                username = request.form["usernameC"]
                password = request.form["passwordC"]
                #on passe tout à la fct connect
                return connect(username, password)

            elif action == "inscription":
                username = request.form["usernameI"]
                password = request.form["passwordI"]
                password2 = request.form["passwordI2"]
                #on passe tout à la fct register
                return register(username, password, password2)
    return redirect(url_for('guest'))

#NE SURTOUT PAS MODIFIER
if __name__ == "__main__":
   app.run(debug=True)
