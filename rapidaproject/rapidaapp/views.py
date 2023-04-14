from ast import For
from operator import index
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from rapidaapp.models import Envoi, TblBureau
from rapidaapp.forms import UserForm, EditUserForm
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth  import authenticate, login, logout
from django.urls import reverse
from django.contrib.auth.models import User 
from django.db import connections, transaction
from django.db.utils import DatabaseError
from datetime import datetime, date
import requests
import json

from django.views.decorators.http import require_http_methods
#add this line if want to make methode Post: @require_http_methods(["POST"])


# Create your views here.
def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]

def remove_duplicates(lst):
    return list(set(lst))

def remove_duplicates_of_list_of_dict(lst):
    unique_dicts = []
    seen = set()
    for d in lst:
        t = tuple(d.items())
        if t not in seen:
            unique_dicts.append(d)
            seen.add(t)
    return unique_dicts


def dict_to_sqlInsert(dict):
    fields_txt = "("
    values_txt = "("
    for  key in dict:
        '''
        if key in ['dateHistorique', 'dateHistoriqueFull']:
            date_string = dict[key]  # string in 'yyyy-mm-dd' format
            date_object = datetime.strptime(date_string, '%Y-%m-%d').date()
            valeur = date_object.strftime('%Y-%m-%d')
        else:
        '''
        valeur = dict[key]
        fields_txt = fields_txt + "'"+ key + "', "
        values_txt = values_txt + "'"+ valeur + "', "
    return fields_txt[:-2] + ") values " + values_txt[:-2] +")"

def connect_and_insertquery(db_connection_name, query, param_list = None):#db_connection_name = 'envoi'
    print(query)
    try:
        with connections[db_connection_name].cursor() as cursor: 
            cursor.execute(query, param_list)
            transaction.commit()
            pass
    except DatabaseError as e:
        print(e)
        transaction.rollback()
    except Exception as e:
        # If an error occurs, roll back the transaction and log the error
        print(e)
        transaction.rollback()
        print('Error: transaction rolled back')

def insert_data_into_database (connection_name, table, dict=None):#dict = {'statut': 'B', 'numEnvoi': 'AO 101122101073'}  
    query = "Insert into " + table + dict_to_sqlInsert(dict)
    return connect_and_insertquery('connection_name', query)

def update_table(request, numEnvoi):
    query = "UPDATE dbo.Historique SET dbo.Historique.isActive=1 WHERE numEnvoi='numEnvoi'"
    return render(request, 'books_updated.html')

def search(request, default=None):
    #print(request.POST)
    field = ''
    where_clause = ''
    copy_where_clause = ''
    isPeriode = False
    for q in request.POST:
        if(len(request.POST[q])>0 and str(q) not in 'csrfmiddlewaretoken, btn-search'):
            field = q  +': '+ request.POST[q] + ', ' + str(field)
            if(str(q) in 'periode'):
                isPeriode =  True
                where_clause = copy_where_clause + "dbo.Envoi.dateEnvoi BETWEEN '" + request.POST['dateEnvoi'] + "'  AND '" + request.POST[q] + "' AND "
            elif(str(q) in 'dateEnvoi'):
                if(isPeriode == False):
                    copy_where_clause = where_clause
                    where_clause = where_clause + "dbo.Envoi.dateEnvoi BETWEEN '" + request.POST[q] + "'  AND '" + request.POST[q] + "' AND "
            elif(str(q) in 'statut'):
                where_clause = where_clause + "dbo.Historique." +str(q) + " LIKE '" + request.POST[q] + "' AND "
            elif(str(q) in 'idPersExp, idPersDest'):
                where_clause = where_clause + "dbo.Facture." +str(q) + " LIKE '" + request.POST[q] + "' AND "
            else:    
                where_clause = where_clause + "dbo.Envoi." +str(q) + " LIKE '" + request.POST[q] + "' AND "
    where_clause = where_clause[:-4]
    #print(field)
    #print(where_clause)
    query = ""
    query2 = ""
    if(len(request.POST['numEnvoi'])>0 and 'isEvent' in request.POST):
        field = str(request.POST['numEnvoi'])
        query = "SELECT distinct  dbo.Envoi.codeBarre as Numero_d_envoi, dbo.Historique.dateHistoriqueFull as Date, TblBureau_3.Nombureau AS Localisation, dbo.Historique.Statut, TblBureau_4.Nombureau AS Prochain_bureau, dbo.TblBureau.Nombureau AS Bureau_d_origine, TblBureau_1.Nombureau AS Bureau_de_destination, Personne.nom AS Expediteur,  Personne_1.nom + ' '+ Personne_1.adresse AS Destinataire, dbo.Envoi.poids, dbo.Envoi.codeBarre as Action FROM dbo.Envoi INNER JOIN dbo.Historique ON dbo.Envoi.numEnvoi = dbo.Historique.numEnvoi INNER JOIN dbo.TblBureau ON dbo.Envoi.bureauOri = dbo.TblBureau.NCODIQUE INNER JOIN dbo.TblBureau AS TblBureau_2 ON dbo.Envoi.bureauPass = TblBureau_2.NCODIQUE INNER JOIN dbo.TblBureau AS TblBureau_1 ON dbo.Envoi.bureauDest = TblBureau_1.NCODIQUE INNER JOIN dbo.Facture ON dbo.Historique.numEnvoi = dbo.Facture.numEnvoi INNER JOIN dbo.Personne AS Personne_1 ON dbo.Facture.idPersDest = Personne_1.idPers INNER JOIN dbo.Personne ON dbo.Facture.idPersExp = dbo.Personne.idPers INNER JOIN dbo.TblBureau AS TblBureau_3 ON dbo.Historique.parcours = TblBureau_3.NCODIQUE FULL JOIN dbo.TblBureau AS TblBureau_4 ON dbo.Historique.burSuiv = TblBureau_4.NCODIQUE "+" WHERE dbo.Envoi.codeBarre LIKE '"+  request.POST['numEnvoi'] + "'" + " AND dbo.Historique.isActive=1 ORDER BY dbo.Envoi.codeBarre ASC, dbo.Historique.dateHistoriqueFull DESC"
    
    elif(len(request.POST['numEnvoi'])>0):
        field = str(request.POST['numEnvoi'])
        query = "SELECT distinct  dbo.Envoi.codeBarre as Numero_d_envoi, dbo.Historique.dateHistoriqueFull as Date, TblBureau_3.Nombureau AS Localisation, dbo.Historique.Statut, TblBureau_4.Nombureau AS Prochain_bureau, dbo.TblBureau.Nombureau AS Bureau_d_origine, TblBureau_1.Nombureau AS Bureau_de_destination, Personne.nom AS Expediteur,  Personne_1.nom + ' '+ Personne_1.adresse AS Destinataire, dbo.Envoi.poids FROM dbo.Envoi INNER JOIN dbo.Historique ON dbo.Envoi.numEnvoi = dbo.Historique.numEnvoi INNER JOIN dbo.TblBureau ON dbo.Envoi.bureauOri = dbo.TblBureau.NCODIQUE INNER JOIN dbo.TblBureau AS TblBureau_2 ON dbo.Envoi.bureauPass = TblBureau_2.NCODIQUE INNER JOIN dbo.TblBureau AS TblBureau_1 ON dbo.Envoi.bureauDest = TblBureau_1.NCODIQUE INNER JOIN dbo.Facture ON dbo.Historique.numEnvoi = dbo.Facture.numEnvoi INNER JOIN dbo.Personne AS Personne_1 ON dbo.Facture.idPersDest = Personne_1.idPers INNER JOIN dbo.Personne ON dbo.Facture.idPersExp = dbo.Personne.idPers INNER JOIN dbo.TblBureau AS TblBureau_3 ON dbo.Historique.parcours = TblBureau_3.NCODIQUE FULL JOIN dbo.TblBureau AS TblBureau_4 ON dbo.Historique.burSuiv = TblBureau_4.NCODIQUE "+" WHERE dbo.Envoi.codeBarre LIKE '"+  request.POST['numEnvoi'] + "'" + " ORDER BY dbo.Envoi.codeBarre ASC, dbo.Historique.dateHistoriqueFull DESC"

        #if with Envoi.dateEnvoi
        #query = "SELECT distinct  dbo.Envoi.codeBarre as Numero_d_envoi, dbo.Envoi.dateEnvoi as Date_, dbo.Historique.dateHistoriqueFull as Date, TblBureau_3.Nombureau AS Localisation, dbo.Historique.Statut, TblBureau_4.Nombureau AS Prochain_bureau, dbo.TblBureau.Nombureau AS Bureau_d_origine, TblBureau_1.Nombureau AS Bureau_de_destination, Personne.nom AS Expediteur,  Personne_1.nom + ' '+ Personne_1.adresse AS Destinataire FROM dbo.Envoi INNER JOIN dbo.Historique ON dbo.Envoi.numEnvoi = dbo.Historique.numEnvoi INNER JOIN dbo.TblBureau ON dbo.Envoi.bureauOri = dbo.TblBureau.NCODIQUE INNER JOIN dbo.TblBureau AS TblBureau_2 ON dbo.Envoi.bureauPass = TblBureau_2.NCODIQUE INNER JOIN dbo.TblBureau AS TblBureau_1 ON dbo.Envoi.bureauDest = TblBureau_1.NCODIQUE INNER JOIN dbo.Facture ON dbo.Historique.numEnvoi = dbo.Facture.numEnvoi INNER JOIN dbo.Personne AS Personne_1 ON dbo.Facture.idPersDest = Personne_1.idPers INNER JOIN dbo.Personne ON dbo.Facture.idPersExp = dbo.Personne.idPers INNER JOIN dbo.TblBureau AS TblBureau_3 ON dbo.Historique.parcours = TblBureau_3.NCODIQUE FULL JOIN dbo.TblBureau AS TblBureau_4 ON dbo.Historique.burSuiv = TblBureau_4.NCODIQUE "+" WHERE dbo.Envoi.codeBarre LIKE '"+  request.POST['numEnvoi'] + "'" + " ORDER BY dbo.Envoi.codeBarre ASC, dbo.Historique.dateHistoriqueFull "
        #query = "SELECT  Envoi.*, Envoi.numenvoi as Numero_d_envoi, Envoi.bureauOri as Bureau_d_origine, bureau_exp.*,  bureau_exp.Nombureau as bureau, bureau_dest.*,  bureau_dest.Nombureau as bureau_dest, Personne.nom  FROM Envoi INNER JOIN TblBureau bureau_exp ON Envoi.bureauOri = bureau_exp.NCODIQUE INNER JOIN TblBureau bureau_dest ON Envoi.bureauDest = bureau_dest.NCODIQUE INNER JOIN Personne ON Envoi.idPersDest = Personne.idPers WHERE Envoi.numenvoi = '" + request.POST["numEnvoi"] + "';"

    elif(len(request.POST['numBordereau'])>0):
        field = str(request.POST['numBordereau'])
        query = "SELECT distinct dbo.Envoi.numEnvoi Numero_d_envoi, PersonneDest.nom AS Destinataire, PersonneDest.adresse AS Adresse_du_destinataire, TblBureau_1.Nombureau AS Bureau_d_origine, dbo.Envoi.poids, dbo.Envoi.prixRapida as Taxe, p1.vehicle as Voiture  FROM dbo.Envoi INNER JOIN  dbo.Facture ON dbo.Envoi.numEnvoi = dbo.Facture.numEnvoi INNER JOIN  dbo.TblBureau AS TblBureau_1 ON dbo.Envoi.bureauOri = TblBureau_1.NCODIQUE INNER JOIN  dbo.TblBureau AS TblBureau_2 ON dbo.Envoi.bureauPass = TblBureau_2.NCODIQUE INNER JOIN  dbo.TblBureau AS TblBureau_3 ON dbo.Envoi.bureauOri = TblBureau_3.NCODIQUE INNER JOIN  dbo.TblBureau AS TblBureau_4 ON dbo.Envoi.bureauDest = TblBureau_4.NCODIQUE INNER JOIN  dbo.Personne AS PersonneExp ON PersonneExp.idPers = dbo.Facture.idPersExp INNER JOIN  dbo.Personne AS PersonneDest ON PersonneDest.idPers = dbo.Facture.idPersDest INNER JOIN  dbo.Historique ON dbo.Envoi.numEnvoi = dbo.Historique.numEnvoi LEFT  JOIN dbo.PartColis p1 ON (dbo.Envoi.codeBarre = p1.idColis and p1.idPartColis=(select Max(p2.idPartColis) FROM PartColis p2 WHERE dbo.Envoi.codeBarre=p2.idColis) ) WHERE Facture.numBordereau = '" + request.POST["numBordereau"] + "';"

        #query = "SELECT  Envoi.*, Envoi.numenvoi as Numero_d_envoi, Envoi.bureauOri as Bureau_d_origine, bureau_exp.*,  bureau_exp.Nombureau as bureau, bureau_dest.*,  bureau_dest.Nombureau as bureau_dest  FROM Envoi INNER JOIN TblBureau bureau_exp ON Envoi.bureauOri = bureau_exp.NCODIQUE INNER JOIN TblBureau bureau_dest ON Envoi.bureauDest = bureau_dest.NCODIQUE INNER JOIN Facture ON Envoi.numEnvoi=Facture.numEnvoi WHERE Facture.numBordereau = '" + request.POST["numBordereau"] + "';"
    elif(len(request.POST['numFacture'])>0):
        field = str(request.POST['numFacture'])
        query = "SELECT distinct dbo.Envoi.numEnvoi Numero_d_envoi, PersonneExp.nom as Expediteur, PersonneDest.nom AS Destinataire, PersonneDest.adresse AS Adresse_du_destinataire, TblBureau_1.Nombureau AS Bureau_d_origine, dbo.Envoi.poids, dbo.Envoi.prixRapida as Taxe, p1.vehicle as Voiture  FROM dbo.Envoi INNER JOIN  dbo.Facture ON dbo.Envoi.numEnvoi = dbo.Facture.numEnvoi INNER JOIN  dbo.TblBureau AS TblBureau_1 ON dbo.Envoi.bureauOri = TblBureau_1.NCODIQUE INNER JOIN  dbo.TblBureau AS TblBureau_2 ON dbo.Envoi.bureauPass = TblBureau_2.NCODIQUE INNER JOIN  dbo.TblBureau AS TblBureau_3 ON dbo.Envoi.bureauOri = TblBureau_3.NCODIQUE INNER JOIN  dbo.TblBureau AS TblBureau_4 ON dbo.Envoi.bureauDest = TblBureau_4.NCODIQUE INNER JOIN  dbo.Personne AS PersonneExp ON PersonneExp.idPers = dbo.Facture.idPersExp INNER JOIN  dbo.Personne AS PersonneDest ON PersonneDest.idPers = dbo.Facture.idPersDest INNER JOIN  dbo.Historique ON dbo.Envoi.numEnvoi = dbo.Historique.numEnvoi LEFT  JOIN dbo.PartColis p1 ON (dbo.Envoi.codeBarre = p1.idColis and p1.idPartColis=(select Max(p2.idPartColis) FROM PartColis p2 WHERE dbo.Envoi.codeBarre=p2.idColis) ) WHERE Facture.numFacture = '" + request.POST["numFacture"] + "';"
    elif(len(request.POST['typeEnvoi'])>0):
        if(len(where_clause)>0):#dbo.Historique.isActive
            query = "SELECT distinct dbo.Envoi.codeBarre as Numero_d_envoi, dbo.Historique.dateHistoriqueFull as Date, TblBureau_3.Nombureau AS Localisation, dbo.Historique.Statut, TblBureau_4.Nombureau AS Prochain_bureau, dbo.TblBureau.Nombureau AS Bureau_d_origine, TblBureau_1.Nombureau AS Bureau_de_destination, Personne.nom AS Expediteur,  Personne_1.nom + ' '+ Personne_1.adresse AS Destinataire, dbo.Envoi.poids, p1.vehicle as Voiture  FROM dbo.Envoi INNER JOIN dbo.Historique ON dbo.Envoi.numEnvoi = dbo.Historique.numEnvoi INNER JOIN dbo.TblBureau ON dbo.Envoi.bureauOri = dbo.TblBureau.NCODIQUE INNER JOIN dbo.TblBureau AS TblBureau_2 ON dbo.Envoi.bureauPass = TblBureau_2.NCODIQUE INNER JOIN dbo.TblBureau AS TblBureau_1 ON dbo.Envoi.bureauDest = TblBureau_1.NCODIQUE INNER JOIN dbo.Facture ON dbo.Historique.numEnvoi = dbo.Facture.numEnvoi INNER JOIN dbo.Personne AS Personne_1 ON dbo.Facture.idPersDest = Personne_1.idPers INNER JOIN dbo.Personne ON dbo.Facture.idPersExp = dbo.Personne.idPers INNER JOIN dbo.TblBureau AS TblBureau_3 ON dbo.Historique.parcours = TblBureau_3.NCODIQUE FULL JOIN dbo.TblBureau AS TblBureau_4 ON dbo.Historique.burSuiv = TblBureau_4.NCODIQUE "+" LEFT  JOIN dbo.PartColis p1 ON (dbo.Envoi.codeBarre = p1.idColis and p1.idPartColis=(select Max(p2.idPartColis) FROM PartColis p2 WHERE dbo.Envoi.codeBarre=p2.idColis) ) WHERE "+  where_clause + " AND dbo.Historique.isActive=1 ORDER BY dbo.Envoi.codeBarre DESC, dbo.Historique.dateHistoriqueFull DESC"
        else:
            field = str(request.POST['typeEnvoi'])
            query = "SELECT distinct  dbo.Envoi.codeBarre as Numero_d_envoi, dbo.Historique.dateHistoriqueFull as Date, TblBureau_3.Nombureau AS Localisation, dbo.Historique.Statut, TblBureau_4.Nombureau AS Prochain_bureau, dbo.TblBureau.Nombureau AS Bureau_d_origine, TblBureau_1.Nombureau AS Bureau_de_destination, Personne.nom AS Expediteur,  Personne_1.nom + ' '+ Personne_1.adresse AS Destinataire, dbo.Envoi.poids, p1.vehicle as Voiture  FROM dbo.Envoi INNER JOIN dbo.Historique ON dbo.Envoi.numEnvoi = dbo.Historique.numEnvoi INNER JOIN dbo.TblBureau ON dbo.Envoi.bureauOri = dbo.TblBureau.NCODIQUE INNER JOIN dbo.TblBureau AS TblBureau_2 ON dbo.Envoi.bureauPass = TblBureau_2.NCODIQUE INNER JOIN dbo.TblBureau AS TblBureau_1 ON dbo.Envoi.bureauDest = TblBureau_1.NCODIQUE INNER JOIN dbo.Facture ON dbo.Historique.numEnvoi = dbo.Facture.numEnvoi INNER JOIN dbo.Personne AS Personne_1 ON dbo.Facture.idPersDest = Personne_1.idPers INNER JOIN dbo.Personne ON dbo.Facture.idPersExp = dbo.Personne.idPers INNER JOIN dbo.TblBureau AS TblBureau_3 ON dbo.Historique.parcours = TblBureau_3.NCODIQUE FULL JOIN dbo.TblBureau AS TblBureau_4 ON dbo.Historique.burSuiv = TblBureau_4.NCODIQUE "+" LEFT  JOIN dbo.PartColis p1 ON (dbo.Envoi.codeBarre = p1.idColis and p1.idPartColis=(select Max(p2.idPartColis) FROM PartColis p2 WHERE dbo.Envoi.codeBarre=p2.idColis) ) WHERE dbo.Envoi.typeEnvoi LIKE '"+  request.POST['typeEnvoi'] + "'" + " AND dbo.Historique.isActive=1 ORDER BY dbo.Envoi.codeBarre DESC, dbo.Historique.dateHistoriqueFull DESC"
    elif(len(request.POST['poids'])>0):
        if "," in request.POST['poids']:
            poids = request.POST['poids'].replace(',','.')
        else:
            poids = request.POST['poids']
        if(len(where_clause)>0):#dbo.Historique.isActive
            query = "SELECT distinct dbo.Envoi.codeBarre as Numero_d_envoi, dbo.Historique.dateHistoriqueFull as Date, TblBureau_3.Nombureau AS Localisation, dbo.Historique.Statut, TblBureau_4.Nombureau AS Prochain_bureau, dbo.TblBureau.Nombureau AS Bureau_d_origine, TblBureau_1.Nombureau AS Bureau_de_destination, Personne.nom AS Expediteur,  Personne_1.nom + ' '+ Personne_1.adresse AS Destinataire, dbo.Envoi.poids, p1.vehicle as Voiture  FROM dbo.Envoi INNER JOIN dbo.Historique ON dbo.Envoi.numEnvoi = dbo.Historique.numEnvoi INNER JOIN dbo.TblBureau ON dbo.Envoi.bureauOri = dbo.TblBureau.NCODIQUE INNER JOIN dbo.TblBureau AS TblBureau_2 ON dbo.Envoi.bureauPass = TblBureau_2.NCODIQUE INNER JOIN dbo.TblBureau AS TblBureau_1 ON dbo.Envoi.bureauDest = TblBureau_1.NCODIQUE INNER JOIN dbo.Facture ON dbo.Historique.numEnvoi = dbo.Facture.numEnvoi INNER JOIN dbo.Personne AS Personne_1 ON dbo.Facture.idPersDest = Personne_1.idPers INNER JOIN dbo.Personne ON dbo.Facture.idPersExp = dbo.Personne.idPers INNER JOIN dbo.TblBureau AS TblBureau_3 ON dbo.Historique.parcours = TblBureau_3.NCODIQUE FULL JOIN dbo.TblBureau AS TblBureau_4 ON dbo.Historique.burSuiv = TblBureau_4.NCODIQUE "+" LEFT  JOIN dbo.PartColis p1 ON (dbo.Envoi.codeBarre = p1.idColis and p1.idPartColis=(select Max(p2.idPartColis) FROM PartColis p2 WHERE dbo.Envoi.codeBarre=p2.idColis) ) WHERE "+ where_clause + " AND dbo.Historique.isActive=1 ORDER BY dbo.Envoi.codeBarre ASC, dbo.Historique.dateHistoriqueFull DESC;"
        else:
            field = str(request.POST['poids'])
            query = "SELECT distinct dbo.Envoi.codeBarre as Numero_d_envoi, dbo.Historique.dateHistoriqueFull as Date, TblBureau_3.Nombureau AS Localisation, dbo.Historique.Statut, TblBureau_4.Nombureau AS Prochain_bureau, dbo.TblBureau.Nombureau AS Bureau_d_origine, TblBureau_1.Nombureau AS Bureau_de_destination, Personne.nom AS Expediteur,  Personne_1.nom + ' '+ Personne_1.adresse AS Destinataire, dbo.Envoi.poids, p1.vehicle as Voiture  FROM dbo.Envoi INNER JOIN dbo.Historique ON dbo.Envoi.numEnvoi = dbo.Historique.numEnvoi INNER JOIN dbo.TblBureau ON dbo.Envoi.bureauOri = dbo.TblBureau.NCODIQUE INNER JOIN dbo.TblBureau AS TblBureau_2 ON dbo.Envoi.bureauPass = TblBureau_2.NCODIQUE INNER JOIN dbo.TblBureau AS TblBureau_1 ON dbo.Envoi.bureauDest = TblBureau_1.NCODIQUE INNER JOIN dbo.Facture ON dbo.Historique.numEnvoi = dbo.Facture.numEnvoi INNER JOIN dbo.Personne AS Personne_1 ON dbo.Facture.idPersDest = Personne_1.idPers INNER JOIN dbo.Personne ON dbo.Facture.idPersExp = dbo.Personne.idPers INNER JOIN dbo.TblBureau AS TblBureau_3 ON dbo.Historique.parcours = TblBureau_3.NCODIQUE FULL JOIN dbo.TblBureau AS TblBureau_4 ON dbo.Historique.burSuiv = TblBureau_4.NCODIQUE "+" LEFT  JOIN dbo.PartColis p1 ON (dbo.Envoi.codeBarre = p1.idColis and p1.idPartColis=(select Max(p2.idPartColis) FROM PartColis p2 WHERE dbo.Envoi.codeBarre=p2.idColis) ) WHERE dbo.Envoi.poids = "+ poids + " AND dbo.Historique.isActive=1 ORDER BY dbo.Envoi.codeBarre ASC, dbo.Historique.dateHistoriqueFull DESC;"
    elif(len(request.POST['bureauOri'])>0):
        if(len(where_clause)>0):#dbo.Historique.isActive
            query = "SELECT distinct dbo.Envoi.codeBarre as Numero_d_envoi, dbo.Historique.dateHistoriqueFull as Date, TblBureau_3.Nombureau AS Localisation, dbo.Historique.Statut, TblBureau_4.Nombureau AS Prochain_bureau, dbo.TblBureau.Nombureau AS Bureau_d_origine, TblBureau_1.Nombureau AS Bureau_de_destination, Personne.nom AS Expediteur,  Personne_1.nom + ' '+ Personne_1.adresse AS Destinataire, dbo.Envoi.poids, p1.vehicle as Voiture  FROM dbo.Envoi INNER JOIN dbo.Historique ON dbo.Envoi.numEnvoi = dbo.Historique.numEnvoi INNER JOIN dbo.TblBureau ON dbo.Envoi.bureauOri = dbo.TblBureau.NCODIQUE INNER JOIN dbo.TblBureau AS TblBureau_2 ON dbo.Envoi.bureauPass = TblBureau_2.NCODIQUE INNER JOIN dbo.TblBureau AS TblBureau_1 ON dbo.Envoi.bureauDest = TblBureau_1.NCODIQUE INNER JOIN dbo.Facture ON dbo.Historique.numEnvoi = dbo.Facture.numEnvoi INNER JOIN dbo.Personne AS Personne_1 ON dbo.Facture.idPersDest = Personne_1.idPers INNER JOIN dbo.Personne ON dbo.Facture.idPersExp = dbo.Personne.idPers INNER JOIN dbo.TblBureau AS TblBureau_3 ON dbo.Historique.parcours = TblBureau_3.NCODIQUE FULL JOIN dbo.TblBureau AS TblBureau_4 ON dbo.Historique.burSuiv = TblBureau_4.NCODIQUE "+" LEFT  JOIN dbo.PartColis p1 ON (dbo.Envoi.codeBarre = p1.idColis and p1.idPartColis=(select Max(p2.idPartColis) FROM PartColis p2 WHERE dbo.Envoi.codeBarre=p2.idColis) ) WHERE "+  where_clause + " AND dbo.Historique.isActive=1 ORDER BY dbo.Envoi.codeBarre ASC, dbo.Historique.dateHistoriqueFull DESC;"
        else:
            field = str(request.POST['bureauOri'])
            query = "SELECT distinct  dbo.Envoi.codeBarre as Numero_d_envoi, dbo.Historique.dateHistoriqueFull as Date, TblBureau_3.Nombureau AS Localisation, dbo.Historique.Statut, TblBureau_4.Nombureau AS Prochain_bureau, dbo.TblBureau.Nombureau AS Bureau_d_origine, TblBureau_1.Nombureau AS Bureau_de_destination, Personne.nom AS Expediteur,  Personne_1.nom + ' '+ Personne_1.adresse AS Destinataire, dbo.Envoi.poids, p1.vehicle as Voiture  FROM dbo.Envoi INNER JOIN dbo.Historique ON dbo.Envoi.numEnvoi = dbo.Historique.numEnvoi INNER JOIN dbo.TblBureau ON dbo.Envoi.bureauOri = dbo.TblBureau.NCODIQUE INNER JOIN dbo.TblBureau AS TblBureau_2 ON dbo.Envoi.bureauPass = TblBureau_2.NCODIQUE INNER JOIN dbo.TblBureau AS TblBureau_1 ON dbo.Envoi.bureauDest = TblBureau_1.NCODIQUE INNER JOIN dbo.Facture ON dbo.Historique.numEnvoi = dbo.Facture.numEnvoi INNER JOIN dbo.Personne AS Personne_1 ON dbo.Facture.idPersDest = Personne_1.idPers INNER JOIN dbo.Personne ON dbo.Facture.idPersExp = dbo.Personne.idPers INNER JOIN dbo.TblBureau AS TblBureau_3 ON dbo.Historique.parcours = TblBureau_3.NCODIQUE FULL JOIN dbo.TblBureau AS TblBureau_4 ON dbo.Historique.burSuiv = TblBureau_4.NCODIQUE "+" LEFT  JOIN dbo.PartColis p1 ON (dbo.Envoi.codeBarre = p1.idColis and p1.idPartColis=(select Max(p2.idPartColis) FROM PartColis p2 WHERE dbo.Envoi.codeBarre=p2.idColis) ) WHERE dbo.Envoi.bureauDest LIKE '"+  request.POST['bureauOri'] + "'" + "AND dbo.Historique.isActive=1 ORDER BY dbo.Envoi.codeBarre ASC, dbo.Historique.dateHistoriqueFull DESC;"
    elif(len(request.POST['bureauDest'])>0):
        if(len(where_clause)>0):#dbo.Historique.isActive
            query = "SELECT distinct dbo.Envoi.codeBarre as Numero_d_envoi, dbo.Historique.dateHistoriqueFull as Date, TblBureau_3.Nombureau AS Localisation, dbo.Historique.Statut, TblBureau_4.Nombureau AS Prochain_bureau, dbo.TblBureau.Nombureau AS Bureau_d_origine, TblBureau_1.Nombureau AS Bureau_de_destination, Personne.nom AS Expediteur,  Personne_1.nom + ' '+ Personne_1.adresse AS Destinataire, dbo.Envoi.poids, p1.vehicle as Voiture  FROM dbo.Envoi INNER JOIN dbo.Historique ON dbo.Envoi.numEnvoi = dbo.Historique.numEnvoi INNER JOIN dbo.TblBureau ON dbo.Envoi.bureauOri = dbo.TblBureau.NCODIQUE INNER JOIN dbo.TblBureau AS TblBureau_2 ON dbo.Envoi.bureauPass = TblBureau_2.NCODIQUE INNER JOIN dbo.TblBureau AS TblBureau_1 ON dbo.Envoi.bureauDest = TblBureau_1.NCODIQUE INNER JOIN dbo.Facture ON dbo.Historique.numEnvoi = dbo.Facture.numEnvoi INNER JOIN dbo.Personne AS Personne_1 ON dbo.Facture.idPersDest = Personne_1.idPers INNER JOIN dbo.Personne ON dbo.Facture.idPersExp = dbo.Personne.idPers INNER JOIN dbo.TblBureau AS TblBureau_3 ON dbo.Historique.parcours = TblBureau_3.NCODIQUE FULL JOIN dbo.TblBureau AS TblBureau_4 ON dbo.Historique.burSuiv = TblBureau_4.NCODIQUE "+" LEFT  JOIN dbo.PartColis p1 ON (dbo.Envoi.codeBarre = p1.idColis and p1.idPartColis=(select Max(p2.idPartColis) FROM PartColis p2 WHERE dbo.Envoi.codeBarre=p2.idColis) ) WHERE "+  where_clause + " AND dbo.Historique.isActive=1 ORDER BY dbo.Envoi.codeBarre ASC, dbo.Historique.dateHistoriqueFull DESC;"
        else:
            field = str(request.POST['bureauDest'])
            query = "SELECT distinct  dbo.Envoi.codeBarre as Numero_d_envoi, dbo.Historique.dateHistoriqueFull as Date, TblBureau_3.Nombureau AS Localisation, dbo.Historique.Statut, TblBureau_4.Nombureau AS Prochain_bureau, dbo.TblBureau.Nombureau AS Bureau_d_origine, TblBureau_1.Nombureau AS Bureau_de_destination, Personne.nom AS Expediteur,  Personne_1.nom + ' '+ Personne_1.adresse AS Destinataire, dbo.Envoi.poids, p1.vehicle as Voiture  FROM dbo.Envoi INNER JOIN dbo.Historique ON dbo.Envoi.numEnvoi = dbo.Historique.numEnvoi INNER JOIN dbo.TblBureau ON dbo.Envoi.bureauOri = dbo.TblBureau.NCODIQUE INNER JOIN dbo.TblBureau AS TblBureau_2 ON dbo.Envoi.bureauPass = TblBureau_2.NCODIQUE INNER JOIN dbo.TblBureau AS TblBureau_1 ON dbo.Envoi.bureauDest = TblBureau_1.NCODIQUE INNER JOIN dbo.Facture ON dbo.Historique.numEnvoi = dbo.Facture.numEnvoi INNER JOIN dbo.Personne AS Personne_1 ON dbo.Facture.idPersDest = Personne_1.idPers INNER JOIN dbo.Personne ON dbo.Facture.idPersExp = dbo.Personne.idPers INNER JOIN dbo.TblBureau AS TblBureau_3 ON dbo.Historique.parcours = TblBureau_3.NCODIQUE FULL JOIN dbo.TblBureau AS TblBureau_4 ON dbo.Historique.burSuiv = TblBureau_4.NCODIQUE "+" LEFT  JOIN dbo.PartColis p1 ON (dbo.Envoi.codeBarre = p1.idColis and p1.idPartColis=(select Max(p2.idPartColis) FROM PartColis p2 WHERE dbo.Envoi.codeBarre=p2.idColis) ) WHERE dbo.Envoi.bureauDest LIKE '"+  request.POST['bureauDest'] + "'" + "AND dbo.Historique.isActive=1 ORDER BY dbo.Envoi.codeBarre ASC, dbo.Historique.dateHistoriqueFull DESC;"
    elif(len(request.POST['idPersExp'])>0):
        if(len(where_clause)>0):#dbo.Historique.isActive
            query = "SELECT distinct dbo.Envoi.codeBarre as Numero_d_envoi, dbo.Historique.dateHistoriqueFull as Date, TblBureau_3.Nombureau AS Localisation, dbo.Historique.Statut, TblBureau_4.Nombureau AS Prochain_bureau, dbo.TblBureau.Nombureau AS Bureau_d_origine, TblBureau_1.Nombureau AS Bureau_de_destination, Personne.nom AS Expediteur,  Personne_1.nom + ' '+ Personne_1.adresse AS Destinataire, dbo.Envoi.poids, p1.vehicle as Voiture  FROM dbo.Envoi INNER JOIN dbo.Historique ON dbo.Envoi.numEnvoi = dbo.Historique.numEnvoi INNER JOIN dbo.TblBureau ON dbo.Envoi.bureauOri = dbo.TblBureau.NCODIQUE INNER JOIN dbo.TblBureau AS TblBureau_2 ON dbo.Envoi.bureauPass = TblBureau_2.NCODIQUE INNER JOIN dbo.TblBureau AS TblBureau_1 ON dbo.Envoi.bureauDest = TblBureau_1.NCODIQUE INNER JOIN dbo.Facture ON dbo.Historique.numEnvoi = dbo.Facture.numEnvoi INNER JOIN dbo.Personne AS Personne_1 ON dbo.Facture.idPersDest = Personne_1.idPers INNER JOIN dbo.Personne ON dbo.Facture.idPersExp = dbo.Personne.idPers INNER JOIN dbo.TblBureau AS TblBureau_3 ON dbo.Historique.parcours = TblBureau_3.NCODIQUE FULL JOIN dbo.TblBureau AS TblBureau_4 ON dbo.Historique.burSuiv = TblBureau_4.NCODIQUE "+" LEFT  JOIN dbo.PartColis p1 ON (dbo.Envoi.codeBarre = p1.idColis and p1.idPartColis=(select Max(p2.idPartColis) FROM PartColis p2 WHERE dbo.Envoi.codeBarre=p2.idColis) ) WHERE "+  where_clause + " AND dbo.Historique.isActive=1 ORDER BY dbo.Envoi.codeBarre ASC, dbo.Historique.dateHistoriqueFull DESC;"
        else:
            field = str(request.POST['idPersExp'])
            query = "SELECT distinct  dbo.Envoi.codeBarre as Numero_d_envoi, dbo.Historique.dateHistoriqueFull as Date, TblBureau_3.Nombureau AS Localisation, dbo.Historique.Statut, TblBureau_4.Nombureau AS Prochain_bureau, dbo.TblBureau.Nombureau AS Bureau_d_origine, TblBureau_1.Nombureau AS Bureau_de_destination, Personne.nom AS Expediteur,  Personne_1.nom + ' '+ Personne_1.adresse AS Destinataire, dbo.Envoi.poids, p1.vehicle as Voiture  FROM dbo.Envoi INNER JOIN dbo.Historique ON dbo.Envoi.numEnvoi = dbo.Historique.numEnvoi INNER JOIN dbo.TblBureau ON dbo.Envoi.bureauOri = dbo.TblBureau.NCODIQUE INNER JOIN dbo.TblBureau AS TblBureau_2 ON dbo.Envoi.bureauPass = TblBureau_2.NCODIQUE INNER JOIN dbo.TblBureau AS TblBureau_1 ON dbo.Envoi.bureauDest = TblBureau_1.NCODIQUE INNER JOIN dbo.Facture ON dbo.Historique.numEnvoi = dbo.Facture.numEnvoi INNER JOIN dbo.Personne AS Personne_1 ON dbo.Facture.idPersDest = Personne_1.idPers INNER JOIN dbo.Personne ON dbo.Facture.idPersExp = dbo.Personne.idPers INNER JOIN dbo.TblBureau AS TblBureau_3 ON dbo.Historique.parcours = TblBureau_3.NCODIQUE FULL JOIN dbo.TblBureau AS TblBureau_4 ON dbo.Historique.burSuiv = TblBureau_4.NCODIQUE "+" LEFT  JOIN dbo.PartColis p1 ON (dbo.Envoi.codeBarre = p1.idColis and p1.idPartColis=(select Max(p2.idPartColis) FROM PartColis p2 WHERE dbo.Envoi.codeBarre=p2.idColis) ) WHERE dbo.Facture.idPersExp LIKE '"+  request.POST['idPersExp'] + "'" + "AND dbo.Historique.isActive=1 ORDER BY dbo.Envoi.codeBarre ASC, dbo.Historique.dateHistoriqueFull DESC;"            
    elif(len(request.POST['idPersDest'])>0):
        if(len(where_clause)>0):#dbo.Historique.isActive
            query = "SELECT distinct dbo.Envoi.codeBarre as Numero_d_envoi, dbo.Historique.dateHistoriqueFull as Date, TblBureau_3.Nombureau AS Localisation, dbo.Historique.Statut, TblBureau_4.Nombureau AS Prochain_bureau, dbo.TblBureau.Nombureau AS Bureau_d_origine, TblBureau_1.Nombureau AS Bureau_de_destination, Personne.nom AS Expediteur,  Personne_1.nom + ' '+ Personne_1.adresse AS Destinataire, dbo.Envoi.poids, p1.vehicle as Voiture  FROM dbo.Envoi INNER JOIN dbo.Historique ON dbo.Envoi.numEnvoi = dbo.Historique.numEnvoi INNER JOIN dbo.TblBureau ON dbo.Envoi.bureauOri = dbo.TblBureau.NCODIQUE INNER JOIN dbo.TblBureau AS TblBureau_2 ON dbo.Envoi.bureauPass = TblBureau_2.NCODIQUE INNER JOIN dbo.TblBureau AS TblBureau_1 ON dbo.Envoi.bureauDest = TblBureau_1.NCODIQUE INNER JOIN dbo.Facture ON dbo.Historique.numEnvoi = dbo.Facture.numEnvoi INNER JOIN dbo.Personne AS Personne_1 ON dbo.Facture.idPersDest = Personne_1.idPers INNER JOIN dbo.Personne ON dbo.Facture.idPersExp = dbo.Personne.idPers INNER JOIN dbo.TblBureau AS TblBureau_3 ON dbo.Historique.parcours = TblBureau_3.NCODIQUE FULL JOIN dbo.TblBureau AS TblBureau_4 ON dbo.Historique.burSuiv = TblBureau_4.NCODIQUE "+" LEFT  JOIN dbo.PartColis p1 ON (dbo.Envoi.codeBarre = p1.idColis and p1.idPartColis=(select Max(p2.idPartColis) FROM PartColis p2 WHERE dbo.Envoi.codeBarre=p2.idColis) ) WHERE "+  where_clause + " AND dbo.Historique.isActive=1 ORDER BY dbo.Envoi.codeBarre ASC, dbo.Historique.dateHistoriqueFull DESC;"
        else:
            field = str(request.POST['idPersDest'])
            query = "SELECT distinct  dbo.Envoi.codeBarre as Numero_d_envoi, dbo.Historique.dateHistoriqueFull as Date, TblBureau_3.Nombureau AS Localisation, dbo.Historique.Statut, TblBureau_4.Nombureau AS Prochain_bureau, dbo.TblBureau.Nombureau AS Bureau_d_origine, TblBureau_1.Nombureau AS Bureau_de_destination, Personne.nom AS Expediteur,  Personne_1.nom + ' '+ Personne_1.adresse AS Destinataire, dbo.Envoi.poids, p1.vehicle as Voiture  FROM dbo.Envoi INNER JOIN dbo.Historique ON dbo.Envoi.numEnvoi = dbo.Historique.numEnvoi INNER JOIN dbo.TblBureau ON dbo.Envoi.bureauOri = dbo.TblBureau.NCODIQUE INNER JOIN dbo.TblBureau AS TblBureau_2 ON dbo.Envoi.bureauPass = TblBureau_2.NCODIQUE INNER JOIN dbo.TblBureau AS TblBureau_1 ON dbo.Envoi.bureauDest = TblBureau_1.NCODIQUE INNER JOIN dbo.Facture ON dbo.Historique.numEnvoi = dbo.Facture.numEnvoi INNER JOIN dbo.Personne AS Personne_1 ON dbo.Facture.idPersDest = Personne_1.idPers INNER JOIN dbo.Personne ON dbo.Facture.idPersExp = dbo.Personne.idPers INNER JOIN dbo.TblBureau AS TblBureau_3 ON dbo.Historique.parcours = TblBureau_3.NCODIQUE FULL JOIN dbo.TblBureau AS TblBureau_4 ON dbo.Historique.burSuiv = TblBureau_4.NCODIQUE "+" LEFT  JOIN dbo.PartColis p1 ON (dbo.Envoi.codeBarre = p1.idColis and p1.idPartColis=(select Max(p2.idPartColis) FROM PartColis p2 WHERE dbo.Envoi.codeBarre=p2.idColis) ) WHERE dbo.Facture.idPersDest LIKE '"+  request.POST['idPersDest'] + "'" + "AND dbo.Historique.isActive=1 ORDER BY dbo.Envoi.codeBarre ASC, dbo.Historique.dateHistoriqueFull DESC;"            
    elif(len(request.POST['periode'])>0):
        if(request.POST.get('statut', False)):
            field = "Entre " + request.POST['dateEnvoi'] + " et " + request.POST['periode'] + " avec statut: " + request.POST['statut']
            query = "SELECT distinct dbo.Envoi.codeBarre as Numero_d_envoi, dbo.Historique.dateHistoriqueFull as Date, TblBureau_3.Nombureau AS Localisation, dbo.Historique.Statut, TblBureau_4.Nombureau AS Prochain_bureau, dbo.TblBureau.Nombureau AS Bureau_d_origine, TblBureau_1.Nombureau AS Bureau_de_destination, Personne.nom AS Expediteur,  Personne_1.nom + ' '+ Personne_1.adresse AS Destinataire, dbo.Envoi.poids, Facture.numBordereau as N_Bordereau, p1.vehicle as Voiture  FROM dbo.Envoi INNER JOIN dbo.Historique ON dbo.Envoi.numEnvoi = dbo.Historique.numEnvoi INNER JOIN dbo.TblBureau ON dbo.Envoi.bureauOri = dbo.TblBureau.NCODIQUE INNER JOIN dbo.TblBureau AS TblBureau_2 ON dbo.Envoi.bureauPass = TblBureau_2.NCODIQUE INNER JOIN dbo.TblBureau AS TblBureau_1 ON dbo.Envoi.bureauDest = TblBureau_1.NCODIQUE INNER JOIN dbo.Facture ON dbo.Historique.numEnvoi = dbo.Facture.numEnvoi INNER JOIN dbo.Personne AS Personne_1 ON dbo.Facture.idPersDest = Personne_1.idPers INNER JOIN dbo.Personne ON dbo.Facture.idPersExp = dbo.Personne.idPers INNER JOIN dbo.TblBureau AS TblBureau_3 ON dbo.Historique.parcours = TblBureau_3.NCODIQUE FULL JOIN dbo.TblBureau AS TblBureau_4 ON dbo.Historique.burSuiv = TblBureau_4.NCODIQUE "+" LEFT  JOIN dbo.PartColis p1 ON (dbo.Envoi.codeBarre = p1.idColis and p1.idPartColis=(select Max(p2.idPartColis) FROM PartColis p2 WHERE dbo.Envoi.codeBarre=p2.idColis) ) WHERE dbo.Envoi.dateEnvoi BETWEEN '" + request.POST['dateEnvoi'] + "'  AND '" + request.POST['periode'] + "' AND dbo.Historique.statut='" + request.POST['statut']+ "' AND dbo.Historique.isActive=1 ORDER BY dbo.Envoi.codeBarre ASC, dbo.Historique.dateHistoriqueFull DESC;"
        else:
            field = "Entre " + request.POST['dateEnvoi'] + " et " + request.POST['periode']
            query = "SELECT distinct dbo.Envoi.codeBarre as Numero_d_envoi, dbo.Historique.dateHistoriqueFull as Date, TblBureau_3.Nombureau AS Localisation, dbo.Historique.Statut, TblBureau_4.Nombureau AS Prochain_bureau, dbo.TblBureau.Nombureau AS Bureau_d_origine, TblBureau_1.Nombureau AS Bureau_de_destination, Personne.nom AS Expediteur,  Personne_1.nom + ' '+ Personne_1.adresse AS Destinataire, dbo.Envoi.poids, Facture.numBordereau as N_Bordereau, p1.vehicle as Voiture  FROM dbo.Envoi INNER JOIN dbo.Historique ON dbo.Envoi.numEnvoi = dbo.Historique.numEnvoi INNER JOIN dbo.TblBureau ON dbo.Envoi.bureauOri = dbo.TblBureau.NCODIQUE INNER JOIN dbo.TblBureau AS TblBureau_2 ON dbo.Envoi.bureauPass = TblBureau_2.NCODIQUE INNER JOIN dbo.TblBureau AS TblBureau_1 ON dbo.Envoi.bureauDest = TblBureau_1.NCODIQUE INNER JOIN dbo.Facture ON dbo.Historique.numEnvoi = dbo.Facture.numEnvoi INNER JOIN dbo.Personne AS Personne_1 ON dbo.Facture.idPersDest = Personne_1.idPers INNER JOIN dbo.Personne ON dbo.Facture.idPersExp = dbo.Personne.idPers INNER JOIN dbo.TblBureau AS TblBureau_3 ON dbo.Historique.parcours = TblBureau_3.NCODIQUE FULL JOIN dbo.TblBureau AS TblBureau_4 ON dbo.Historique.burSuiv = TblBureau_4.NCODIQUE "+" LEFT  JOIN dbo.PartColis p1 ON (dbo.Envoi.codeBarre = p1.idColis and p1.idPartColis=(select Max(p2.idPartColis) FROM PartColis p2 WHERE dbo.Envoi.codeBarre=p2.idColis) ) WHERE dbo.Envoi.dateEnvoi BETWEEN '" + request.POST['dateEnvoi'] + "'  AND '" + request.POST['periode'] + "' AND dbo.Historique.isActive=1 ORDER BY dbo.Envoi.codeBarre ASC, dbo.Historique.dateHistoriqueFull DESC;"

        query2 = "SELECT distinct dbo.Envoi.codeBarre as Numero_d_envoi, dbo.Historique.dateHistoriqueFull as Date, TblBureau_3.Nombureau AS Localisation, dbo.Historique.Statut, TblBureau_4.Nombureau AS Prochain_bureau, dbo.TblBureau.Nombureau AS Bureau_d_origine, TblBureau_1.Nombureau AS Bureau_de_destination, Personne.nom AS Expediteur,  Personne_1.nom + ' '+ Personne_1.adresse AS Destinataire, dbo.Envoi.poids, Facture.numBordereau as N_Bordereau, p1.vehicle as Voiture  FROM dbo.Envoi INNER JOIN dbo.Historique ON dbo.Envoi.numEnvoi = dbo.Historique.numEnvoi INNER JOIN dbo.TblBureau ON dbo.Envoi.bureauOri = dbo.TblBureau.NCODIQUE INNER JOIN dbo.TblBureau AS TblBureau_2 ON dbo.Envoi.bureauPass = TblBureau_2.NCODIQUE INNER JOIN dbo.TblBureau AS TblBureau_1 ON dbo.Envoi.bureauDest = TblBureau_1.NCODIQUE INNER JOIN dbo.Facture ON dbo.Historique.numEnvoi = dbo.Facture.numEnvoi INNER JOIN dbo.Personne AS Personne_1 ON dbo.Facture.idPersDest = Personne_1.idPers INNER JOIN dbo.Personne ON dbo.Facture.idPersExp = dbo.Personne.idPers INNER JOIN dbo.TblBureau AS TblBureau_3 ON dbo.Historique.parcours = TblBureau_3.NCODIQUE FULL JOIN dbo.TblBureau AS TblBureau_4 ON dbo.Historique.burSuiv = TblBureau_4.NCODIQUE "+" LEFT  JOIN dbo.PartColis p1 ON (dbo.Envoi.codeBarre = p1.idColis and p1.idPartColis=(select Max(p2.idPartColis) FROM PartColis p2 WHERE dbo.Envoi.codeBarre=p2.idColis) ) WHERE dbo.Envoi.dateEnvoi BETWEEN '" + request.POST['dateEnvoi'] + "'  AND '" + request.POST['periode'] + "' AND dbo.Historique.isActive=1 ORDER BY dbo.Envoi.codeBarre ASC, dbo.Historique.dateHistoriqueFull DESC;"

    elif(len(request.POST['dateEnvoi'])>0):
        if(request.POST.get('statut', False)):
            field = request.POST['dateEnvoi'] + " avec statut: " + request.POST['statut']
            query = "SELECT distinct dbo.Envoi.codeBarre as Numero_d_envoi, dbo.Historique.dateHistoriqueFull as Date, TblBureau_3.Nombureau AS Localisation, dbo.Historique.Statut, TblBureau_4.Nombureau AS Prochain_bureau, dbo.TblBureau.Nombureau AS Bureau_d_origine, TblBureau_1.Nombureau AS Bureau_de_destination, Personne.nom AS Expediteur,  Personne_1.nom + ' '+ Personne_1.adresse AS Destinataire, dbo.Envoi.poids, Facture.numBordereau as N_Bordereau, p1.vehicle as Voiture  FROM dbo.Envoi INNER JOIN dbo.Historique ON dbo.Envoi.numEnvoi = dbo.Historique.numEnvoi INNER JOIN dbo.TblBureau ON dbo.Envoi.bureauOri = dbo.TblBureau.NCODIQUE INNER JOIN dbo.TblBureau AS TblBureau_2 ON dbo.Envoi.bureauPass = TblBureau_2.NCODIQUE INNER JOIN dbo.TblBureau AS TblBureau_1 ON dbo.Envoi.bureauDest = TblBureau_1.NCODIQUE INNER JOIN dbo.Facture ON dbo.Historique.numEnvoi = dbo.Facture.numEnvoi INNER JOIN dbo.Personne AS Personne_1 ON dbo.Facture.idPersDest = Personne_1.idPers INNER JOIN dbo.Personne ON dbo.Facture.idPersExp = dbo.Personne.idPers INNER JOIN dbo.TblBureau AS TblBureau_3 ON dbo.Historique.parcours = TblBureau_3.NCODIQUE FULL JOIN dbo.TblBureau AS TblBureau_4 ON dbo.Historique.burSuiv = TblBureau_4.NCODIQUE "+" LEFT  JOIN dbo.PartColis p1 ON (dbo.Envoi.codeBarre = p1.idColis and p1.idPartColis=(select Max(p2.idPartColis) FROM PartColis p2 WHERE dbo.Envoi.codeBarre=p2.idColis) ) WHERE dbo.Envoi.dateEnvoi BETWEEN '" + request.POST['dateEnvoi'] + "'  AND '" + request.POST['dateEnvoi'] + "' AND dbo.Historique.statut='" + request.POST['statut']+ "' AND dbo.Historique.isActive=1  ORDER BY dbo.Envoi.codeBarre ASC, dbo.Historique.dateHistoriqueFull DESC;"
        else:
            field = str(request.POST['dateEnvoi'])
            query = "SELECT distinct dbo.Envoi.codeBarre as Numero_d_envoi, dbo.Historique.dateHistoriqueFull as Date, TblBureau_3.Nombureau AS Localisation, dbo.Historique.Statut, TblBureau_4.Nombureau AS Prochain_bureau, dbo.TblBureau.Nombureau AS Bureau_d_origine, TblBureau_1.Nombureau AS Bureau_de_destination, Personne.nom AS Expediteur,  Personne_1.nom + ' '+ Personne_1.adresse AS Destinataire, dbo.Envoi.poids, Facture.numBordereau as N_Bordereau, p1.vehicle as Voiture  FROM dbo.Envoi INNER JOIN dbo.Historique ON dbo.Envoi.numEnvoi = dbo.Historique.numEnvoi INNER JOIN dbo.TblBureau ON dbo.Envoi.bureauOri = dbo.TblBureau.NCODIQUE INNER JOIN dbo.TblBureau AS TblBureau_2 ON dbo.Envoi.bureauPass = TblBureau_2.NCODIQUE INNER JOIN dbo.TblBureau AS TblBureau_1 ON dbo.Envoi.bureauDest = TblBureau_1.NCODIQUE INNER JOIN dbo.Facture ON dbo.Historique.numEnvoi = dbo.Facture.numEnvoi INNER JOIN dbo.Personne AS Personne_1 ON dbo.Facture.idPersDest = Personne_1.idPers INNER JOIN dbo.Personne ON dbo.Facture.idPersExp = dbo.Personne.idPers INNER JOIN dbo.TblBureau AS TblBureau_3 ON dbo.Historique.parcours = TblBureau_3.NCODIQUE FULL JOIN dbo.TblBureau AS TblBureau_4 ON dbo.Historique.burSuiv = TblBureau_4.NCODIQUE "+" LEFT  JOIN dbo.PartColis p1 ON (dbo.Envoi.codeBarre = p1.idColis and p1.idPartColis=(select Max(p2.idPartColis) FROM PartColis p2 WHERE dbo.Envoi.codeBarre=p2.idColis) ) WHERE dbo.Envoi.dateEnvoi BETWEEN '" + request.POST['dateEnvoi'] + "'  AND '" + request.POST['dateEnvoi'] + "' AND dbo.Historique.isActive=1  ORDER BY dbo.Envoi.codeBarre ASC, dbo.Historique.dateHistoriqueFull DESC;"
    else:
        field = "Par défaut (25 dérnières insertions)"
        query = "SELECT distinct TOP(25) dbo.Envoi.codeBarre as Numero_d_envoi, dbo.Historique.dateHistoriqueFull as Date, TblBureau_3.Nombureau AS Localisation, dbo.Historique.Statut, TblBureau_4.Nombureau AS Prochain_bureau, dbo.TblBureau.Nombureau AS Bureau_d_origine, TblBureau_1.Nombureau AS Bureau_de_destination, Personne.nom AS Expediteur,  Personne_1.nom + ' '+ Personne_1.adresse AS Destinataire, dbo.Envoi.poids, p1.vehicle as Voiture  FROM dbo.Envoi INNER JOIN dbo.Historique ON dbo.Envoi.numEnvoi = dbo.Historique.numEnvoi INNER JOIN dbo.TblBureau ON dbo.Envoi.bureauOri = dbo.TblBureau.NCODIQUE INNER JOIN dbo.TblBureau AS TblBureau_2 ON dbo.Envoi.bureauPass = TblBureau_2.NCODIQUE INNER JOIN dbo.TblBureau AS TblBureau_1 ON dbo.Envoi.bureauDest = TblBureau_1.NCODIQUE INNER JOIN dbo.Facture ON dbo.Historique.numEnvoi = dbo.Facture.numEnvoi INNER JOIN dbo.Personne AS Personne_1 ON dbo.Facture.idPersDest = Personne_1.idPers INNER JOIN dbo.Personne ON dbo.Facture.idPersExp = dbo.Personne.idPers INNER JOIN dbo.TblBureau AS TblBureau_3 ON dbo.Historique.parcours = TblBureau_3.NCODIQUE FULL JOIN dbo.TblBureau AS TblBureau_4 ON dbo.Historique.burSuiv = TblBureau_4.NCODIQUE "+" LEFT  JOIN dbo.PartColis p1 ON (dbo.Envoi.codeBarre = p1.idColis and p1.idPartColis=(select Max(p2.idPartColis) FROM PartColis p2 WHERE dbo.Envoi.codeBarre=p2.idColis) ) WHERE dbo.Historique.statut LIKE 'A' AND dbo.Historique.isActive=1 ORDER BY dbo.Envoi.codeBarre ASC, dbo.Historique.dateHistoriqueFull DESC;"

    dataListDict = []
    dataListTuple = []
    dataListDict2 = []
    with connections['envois'].cursor() as cursor: 
        #cursor.execute("SELECT  Envoi.numenvoi as Numero_d_envoi FROM Envoi WHERE Envoi.numEnvoi= %s", [request.POST['numEnvoi']])
        #print(query)
        cursor.execute(query)
        #row = cursor.fetchone()
        #dataListTuple = cursor.fetchall()
        dataListDict = dictfetchall(cursor)
        if query2 != "":
            cursor.execute(query2)
            dataListDict2 = dictfetchall(cursor)
            #pass

    for dict in dataListDict:
        list = [(k, v) for k, v in dict.items()]
        dataListTuple.append(list)

    data_strings = [
        #{'Numero_d_envoi': item['Numero_d_envoi'], 'Date': item['Date'].strftime('%Y-%m-%d %H:%M:%S')}
        {'Numero_d_envoi': item['Numero_d_envoi']}
        for item in dataListDict
    ]
    if request.session.get('temp_data') is None:
        request.session['temp_data']=[]
    my_old_session_data = request.session.get('temp_data', [])
    print(data_strings)
    my_old_session_data.append(data_strings[0]) 
    print('session temp_data: ', my_old_session_data)
    # Store the list of dictionaries with strings in the session
    request.session['temp_data'] = my_old_session_data
    #request.session['temp_data'] =  remove_duplicates_of_list_of_dict(temp_data)
    #print(type(data))
    #print(len(data))
    #print(type(data[0]))
    #print(dataListDict)
    #print(dataListDict2)
    #print(dataListTuple)
    #data = Envoi.objects.raw(query).using('envois')
    #keysList = list(data[0].keys())
    #print(keysList)
    #request.session['temp_data'].append(dataListTuple)
    print(data_strings)
    #print(request.session.get('temp_data'))
    return {"dataListDict": dataListDict, "dataListTuple": dataListTuple, "field": field}

def index(request):
    if request.user.is_authenticated:
        return redirect(reverse("search_form"))   
    else:
        return redirect(reverse("login"))   


def find(request):
    if request.user.is_authenticated:
        current_user = request.user
        if request.method == "POST":
            searchRres = search(request)
            dataListDict = searchRres["dataListDict"]
            dataListTuple = searchRres["dataListTuple"]
            field = searchRres["field"]

            if len(dataListDict)>0:
                titre = dataListDict[0]
            else:
                titre = []
            context = {
                'author': 'Destinataire',
                'data': dataListTuple,
                'titre': titre,
                'field': field,
                'dataListDict':dataListDict,
            }
            if(len(request.POST['numEnvoi'])>0):
                if('isEvent' in request.POST):
                    return render(request, 'event.html', context)
                else:
                    return render(request, 'index_oneRes.html', context)
            return render(request, 'index.html', context)
        else:#default
            if current_user.groups.filter(name__in=['CTPR']).exists():
                field = "Aujourd'hui " + datetime.today().strftime('%d-%m-%Y')
                query = "SELECT distinct dbo.Envoi.codeBarre as Numero_d_envoi, dbo.Historique.dateHistoriqueFull as Date, TblBureau_3.Nombureau AS Localisation, dbo.Historique.Statut, TblBureau_4.Nombureau AS Prochain_bureau, dbo.TblBureau.Nombureau AS Bureau_d_origine, TblBureau_1.Nombureau AS Bureau_de_destination, Personne.nom AS Expediteur,  Personne_1.nom + ' '+ Personne_1.adresse AS Destinataire, dbo.Envoi.poids, Facture.numBordereau as N_Bordereau, p1.vehicle as Voiture  FROM dbo.Envoi INNER JOIN dbo.Historique ON dbo.Envoi.numEnvoi = dbo.Historique.numEnvoi INNER JOIN dbo.TblBureau ON dbo.Envoi.bureauOri = dbo.TblBureau.NCODIQUE INNER JOIN dbo.TblBureau AS TblBureau_2 ON dbo.Envoi.bureauPass = TblBureau_2.NCODIQUE INNER JOIN dbo.TblBureau AS TblBureau_1 ON dbo.Envoi.bureauDest = TblBureau_1.NCODIQUE INNER JOIN dbo.Facture ON dbo.Historique.numEnvoi = dbo.Facture.numEnvoi INNER JOIN dbo.Personne AS Personne_1 ON dbo.Facture.idPersDest = Personne_1.idPers INNER JOIN dbo.Personne ON dbo.Facture.idPersExp = dbo.Personne.idPers INNER JOIN dbo.TblBureau AS TblBureau_3 ON dbo.Historique.parcours = TblBureau_3.NCODIQUE FULL JOIN dbo.TblBureau AS TblBureau_4 ON dbo.Historique.burSuiv = TblBureau_4.NCODIQUE "+" LEFT  JOIN dbo.PartColis p1 ON (dbo.Envoi.codeBarre = p1.idColis and p1.idPartColis=(select Max(p2.idPartColis) FROM PartColis p2 WHERE dbo.Envoi.codeBarre=p2.idColis) ) WHERE dbo.Envoi.dateEnvoi BETWEEN '" + datetime.today().strftime('%Y/%m/%d') + "'  AND '" + datetime.today().strftime('%Y/%m/%d')+ "' AND dbo.Historique.isActive=1  ORDER BY dbo.Envoi.codeBarre ASC, dbo.Historique.dateHistoriqueFull DESC;"
                dataListDict = []
                dataListTuple = []
                with connections['envois'].cursor() as cursor: 
                    print(query)
                    cursor.execute(query)
                    dataListDict = dictfetchall(cursor)
                for dict in dataListDict:
                    list = [(k, v) for k, v in dict.items()]
                    dataListTuple.append(list)
                if len(dataListDict)>0:
                    titre = dataListDict[0]
                else:
                    titre = []
                context = {
                    'author': 'Destinataire',
                    'data': dataListTuple,
                    'titre': titre,
                    'field': field,
                    'dataListDict':dataListDict,
                }
                return render(request, 'index.html', context)
            else:
                return redirect(reverse("search_form")) 
    else:
        return redirect(reverse("login"))   

def home(request):
    context = {
        'author': 'fetra',
    }
    return render(request, 'homepage.html', context)


def login_form(request):
    if request.user.is_authenticated:
        query = 'SELECT TblBureau.*, TblBureau.ncodique, TblBureau.Nombureau FROM TblBureau ORDER BY TblBureau.Nombureau ASC;'
        data = TblBureau.objects.raw(query).using('envois')
        #print(data)
        #for x in data:
        #    print(x)
        context = {
            'author': 'fetra',
            'data': data,
        }
        return render(request, 'search_form.html', context)
    else:
        context = {
            'author': 'fetra',
        }
        return render(request, 'login.html', context)

def search_form(request):
    if request.user.is_authenticated:
        query = 'SELECT TblBureau.*, TblBureau.ncodique, TblBureau.Nombureau FROM TblBureau ORDER BY TblBureau.Nombureau ASC;'
        data = TblBureau.objects.raw(query).using('envois')
        current_user = request.user
        #current_user.values_list('name',flat = True)
        #if current_user.groups.filter(name__in=['CTPR']).exists():
        dataListDict = []
        dataListTuple = []
        with connections['envois'].cursor() as cursor: 
            print(query)
            cursor.execute(query)
            dataListDict = dictfetchall(cursor)
        print(dataListDict)
        context = {
            'author': 'fetra',
            'data': data,
        }
        return render(request, 'search_form.html', context)
    else:
        return redirect(reverse("login"))  

def logout_view(request):
    logout(request)
    return render(request, "login.html", {"messages": "Vous êtes déconnectés."})

def check_auth(request):
    if request.method == "POST":
        user = None
        if("username" in request.POST):
            username = request.POST["username"]
            password = request.POST["password"]
            #user_obj = User.objects.filter(username = username).first()
            
            #print(f"----{user_obj.username}-----")
            if User.objects.filter(username = username).first() is None:
                context = {
                    'message' : "Ce login n' existe pas!"
                }
                return render(request, "login.html", context)
   
            user = authenticate(request, username=username,  password=password)
            #user = authenticate(request, username=username,  password=make_password(password))
            #user = authenticate(request, username=username,  password=check_password(password))
            print(user)
            print(" ---------- ending")
                    
            if user is not None:
                login(request, user)
                return redirect(reverse("search_form"))
            else:
                return render(request, "login.html", {"message": "Aucun utilisateur ne correspond pas !"})

def list_users(request):
    if request.method == "GET":#read
        users = User.objects.all()  
        context = {
            'data': users
        }
        return render(request, "users.html", context)
    elif request.method == "POST":#create
        if 'edit' in request.POST:#mikitika db
            username    = request.POST.get('username')
            password    = request.POST.get('password')
            roles   = request.POST.get('roles')
            email       = request.POST.get('email')
            id       = request.POST.get('id')

            user = User.objects.get(pk=id)
            user.username =  username
            user.email = email
            #user.password = make_password(password)
            user.roles = roles
            user.set_password(password)
            user.save()

            users = User.objects.all()  
            context = {
                'data': users
            }
            return render(request, "users.html", context)          
        elif 'delete' in request.POST:
            id = request.POST.get('id')
            user = User.objects.get(pk=id)
            user.delete()

            users = User.objects.all()  
            context = {
                'data': users
            }
            return render(request, "users.html", context) 
        else:
            username    = request.POST.get('username')
            password    = request.POST.get('password')
            roles   = request.POST.get('roles')
            email       = request.POST.get('email')

            user = User()
            user.email = email
            user.username = username
            #user.roles = roles
            user.set_password(password)
            user.save()
            #user_obj = User.objects.create(username = username, email = email, password = make_password(password), roles = roles )
            users = User.objects.all()  
            context = {
                'data': users
            }
            return render(request, "users.html", context)    

def new_users(request):
    form = UserForm()
    return render(request, 'new_users.html', {'form': form})

def edit_form_users(request, id):#form + data
    user = User.objects.get(pk=id)
    #form = EditUserForm(initial={'email': user.email, 'username': user.username, 'password': user.password, 'roles': user.roles})
    form = EditUserForm(initial={'email': user.email, 'username': user.username, 'password': user.password})
    return render(request, 'edit_users.html', {'form': form, 'id': id})

def delete_users(request, id):
    user = User.objects.get(pk=id)
    user.delete()

    users = User.objects.all()  
    context = {
        'data': users
    }
    if request.method == "PUT":
        return HttpResponse('update')
    elif request.method == "DELETE":
        return render(request, "users.html", context)     

def register(request):
    current__date = datetime.datetime.now()
    print(current__date)
    if request.method == "POST":
        if 'register' in request.POST:
            username    = request.POST.get('username')
            password    = request.POST.get('password')
            firstname   = request.POST.get('firstname')
            birthday    = request.POST.get('birthday')
            gender      = request.POST.get('gender')
            email       = request.POST.get('email')
            contact     = request.POST.get('contact')
            codepostal  = request.POST.get('city')
            print(password)
            Confirm_password =  request.POST.get('confirm_password')
            # print(confirm_password)
            #Logement = request.POST.get('Logement')
            #city = request.POST.get('city')
            #arrondissement = request.POST.get('arrondissement')
            #country =  request.POST.get('country')
            print(password)
            print(firstname)
            try:
                if (password != Confirm_password):
                    message =  'Les mots de passe entrés ne se correspondent pas!'
                    return render( request , 'djangoapp/register.html' , {'message': message})
                else :
                    if  len(password) < 8 :
                        message =  'le mot de passse doit avoir  au moins 8 caracteres!'
                        return render( request , 'djangoapp/register.html' , {'message': message})
                    else:
                        if User.objects.filter(email = email).first():
                            message = "Email déja utilisé."
                            return render( request , 'djangoapp/register.html' , {'message': message})
                        else :
                            user_obj = User.objects.create(username = username, email = email )
                            user_obj.set_password(password)
                            user_cart = Cart.objects.create(user = user_obj)
                            user_cart.save()
                            auth_token = str(uuid.uuid4()) 
                            user_obj.save()
                            Profile_obj = Profile.objects.create(user = user_obj,auth_token=auth_token,firstname= firstname,birthday=birthday,Contact=contact,genre=gender )
                            Profile_obj.save()
                            adresseCustomer = AdresseCustomer.objects.create( profile = Profile_obj,Codepostal = codepostal)
                            adresseCustomer.save()
                            send_mail_after_registration(email , auth_token,  request.build_absolute_uri())
                            return redirect('/token')
                               
            except Exception as e:
                print(e)
    return render(request, "djangoapp/register.html")


def add_event(request):
    if request.user.is_authenticated:
        query = 'SELECT TblBureau.*, TblBureau.ncodique, TblBureau.Nombureau FROM TblBureau ORDER BY TblBureau.Nombureau ASC;'
        data = TblBureau.objects.raw(query).using('envois')#rawquery
        # Convert the RawQuerySet object to a list of dictionaries
        data_list = []
        dict = {}
        for d in data:
            dict[d.ncodique] = d.bureau
        #print(data_list)
        # Serialize data to JSON
        json_data = json.dumps(dict)
        context = {
            'dataBureau': data,
            'json_data': json_data,
        }
        return render( request , 'event.html' , context)
    else:
        return redirect(reverse("login"))

def ajax_find(request):
    searchRres = search(request)
    return JsonResponse(searchRres)

def ajax_add(request):
    numEnvois = []
    today = date.today()
    d1 = today.strftime("%Y-%m-%d")
    now = datetime.now()
    dt_string = now.strftime("%Y-%m-%d %H:%M:%S")
    numEnvoi = request.POST.get('numEnvoi-1')
    #print(request.POST)

    if request.method == "POST":
        x = ''
        queries = []
        for key, value in request.POST.items():
            #print(f"{key}: {value}")
            if key[:8] in ['numEnvoi']:
                numEnvois.append(value)
                #param_value_txt = "'numfake6', '10101', '10102', 'B', '1', '10103', '10102', CONVERT(date, '2022-12-31', 120), '10103', '10101', CONVERT(datetime, '2022-12-31 23:59:59', 120)"
                #connect_and_insertquery('envois', f"Insert into dbo.Historique(numEnvoi, bureauOrigine, bureauPasse, statut, isActive, chemin, parcours, dateHistorique , burSuiv, burPrec, dateHistoriqueFull) values ({param_list})")
                #param_value_txt = param_value_txt + " ,'"+ value + "'"
                #param_key_txt = param_key_txt + " ,"+ "numEnvoi" + ""
        

        
        for num in numEnvois:
            param_value_txt = ""
            param_key_txt = ""

            for key, value in request.POST.items():
                if key in ['bureauOrigine']:
                    param_value_txt = param_value_txt + " ,'"+ value + "'"
                    param_value_txt = param_value_txt + " ,'"+ value + "'"
                    param_value_txt = param_value_txt + " ,'"+ value + "'"
                    param_key_txt = param_key_txt + " ,"+ key + ""
                    param_key_txt = param_key_txt + " ,"+ "parcours" + ""
                    param_key_txt = param_key_txt + " ,"+ "burPrec" + ""
                elif key in ['bureauPasse']:
                    param_value_txt = param_value_txt + " ,'"+ value + "'"
                    param_value_txt = param_value_txt + " ,'"+ value + "'"
                    param_value_txt = param_value_txt + " ,'"+ value + "'"
                    param_key_txt = param_key_txt + " ,"+ key + ""
                    param_key_txt = param_key_txt + " ,"+ "burSuiv" + ""
                elif key in ['bureauDest']:#chemin
                    param_key_txt = param_key_txt + " ,"+ "chemin" + ""
                elif key in ['statut']:
                    param_value_txt = param_value_txt + " ,'"+ value + "'"
                    param_key_txt = param_key_txt + " ,"+ key + ""

            if len(param_key_txt) > 1:
                param_value_txt = param_value_txt + " ,'"+ "1" + "'"
                param_key_txt = param_key_txt + " ,"+ "isActive" + ""

            param_value_txt = param_value_txt + " ,'"+ num + "'"
            param_key_txt = param_key_txt + " ,"+ "numEnvoi" + ""

            query_param_key = param_key_txt[2:] + " ,dateHistorique "+ ", dateHistoriqueFull"
            query_param_value = param_value_txt[2:] + f",CONVERT(date, '{d1}', 120)" + f",CONVERT(datetime, '{dt_string}', 120)"

            queries.append(f"UPDATE dbo.Historique SET isActive = 0 WHERE numEnvoi = '{num}'; Insert into dbo.Historique({query_param_key}) values ({query_param_value}); DECLARE @last_id INT; SET @last_id =SCOPE_IDENTITY(); INSERT INTO commentHistorique (idHistorique, comments) VALUES (@last_id, 'par ctpr');")
        print(queries)
        for query in queries:
            connect_and_insertquery("envois", query)
            pass
        return JsonResponse({"modification":numEnvois})
    else:
        return render( request , 'event.html' ,context)