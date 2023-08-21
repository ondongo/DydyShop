from application.models.EnumColorAndSize import *
from application.models.EnumCategorie import *
from config import *
annonces = [
    {
        "id": 1,
        "title": "Mercedes",
        "img_url": None,
        "prix":1500,
        "etat":EnumEtatArticle.Reconditione.name,
        "categorie":EnumCategorie.Vehicules.name,
        "description": "Voici  le contenu de l'Item 1",
        "datePub": "15/03/2023",
        "lieuPub":"medina"
    },
    {
       "id": 2,
        "title": "Peugeot",
        "img_url": NO_PHOTO,
        "prix":25000,
        "etat":EnumEtatArticle.Neuf.name,
        "categorie":EnumCategorie.Vehicules.name,
        "description": "Voici  le contenu de l'Item 2",
        "datePub": "12/03/2023",
         "lieuPub":"medina"
    },
   
]

# Afficher tous les articles
def getAllArticles():
    return annonces

# Afficher l'article qui a cet id
def findArticleById(id_annonce):
    for a in annonces:
        if a["id"] == id_annonce:
            return a
    return None
    

