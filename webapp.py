# Doc psycopg2 : http://initd.org/psycopg/docs/index.html
# Flask : https://openclassrooms.com/courses/creez-vos-applications-web-avec-flask

from flask import *
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

#ACCUEIL
@app.route("/home/", defaults={'action': ''})
@app.route("/home/<action>", methods=['POST', 'GET'])
def home(action):
    if 'username' in session:
        #envoyer un message
        if action == "sendMess":
            if request.method == "POST":
                message = request.form['message']
                return sendMessage(message)

        elif action == "disconnect":
            return disconnect()

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

#PREFERENCES
@app.route("/preferences/", defaults={'action': ''})
@app.route("/preferences/<action>", methods=["POST", "GET"])
def preferences(action):
    if 'username' in session:
        #preferences modifications by form
        if request.method == "POST":
            if action == "usernameModif":
                return usernameModif(request.form["username"])

            elif action == "passModif":
                return passModif(request.form["oldpass"], request.form["newpass"], request.form["newpass2"])

            elif action == "apparenceModif":
                return apparenceModif(request.form["nb_mess"], request.form["color"])

        return render_template('preferences.html')

    return redirect(url_for('guest'))

#MESSAGERIE PRIVÉE
@app.route("/private/", defaults={'action': ''})
@app.route("/private/<action>", methods=["POST", "GET"])
def private(action):
    if 'username' in session:
        if action == "0":
            flash('L\'utilisateur que vous voulez contacter n\'existe pas.')
            return redirect(url_for('home', action=''))
        elif action == "list":
            return display_users()
        else:
            if request.method == "POST":
                message = request.form["message"]
                return sendPrivate(message, action)

            return display_private(action)

    return redirect(url_for('guest'))

#ADMINISTRATION
@app.route("/admin/", defaults={'action': '', 'action_id': ''})
@app.route("/admin/<action>/<action_id>")
def admin(action, action_id):
    if 'username' in session and session['grade'] == 1:
        if action == 'deleteMess':
             return supprimer_message(action_id)
        elif action == 'bannir':
            return ban(action_id, 1)
        elif action == 'debannir':
            return ban(action_id, 0)
        return get_users_admin()
    return redirect(url_for('home', action=''))

#PAGE 404
@app.errorhandler(404)
def page_404(e):
    return render_template("page404.html"), 404

#NE SURTOUT PAS MODIFIER
if __name__ == "__main__":
   app.run(debug=True)
