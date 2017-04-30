""" petit fichier pour ne pas encombrer le code webapp.py
Il contient diverses fonctions afin de factoriser le code et de le
simplifier un maximum en cas de modification """
import psycopg2

def disconnect_db(cur, conn):
    """Trop de connection non fermees a la base de donnees surchage
    l'acces a celle ci. Cette fonction ferme le curseur cur et la connection
    conn """
    cur.close()
    conn.close()

def execute_request(cur, request):
    """ Fonction qui execute la requete SQL request et la return"""
    cur.execute(request)
    return cur.fetchall()
