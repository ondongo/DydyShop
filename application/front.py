
from flask import Flask, render_template,redirect,url_for,request
from sqlalchemy import desc
from application.models.EnumColorAndSize import *
from application.models.EnumCategorie import *
from application.models.SousCategorie import *



#from .routes import main 
# from . import fakes_data
# from .fakes_data import getAllArticles, findArticleById


from flask_paginate import Pagination, get_page_parameter

#----------Fichier Principal-------------
app =Flask(__name__)

# Montrer a flask la ou se trouve notre fichier de config Flask
# app.config.from_object("config"))
# Pagination des pages
# pagination = Pagination(app)


# CREATION DE FILTER <<============================================>>

# --------------Creation Route--------------------
# Une fonction et Route en meme temps

app.config.from_object("config")


from application.models.model import (
      findAnnonceById,Item,getAllAnnoncePublier,getAllAnnonceA_La_Une)

categories=list(EnumCategorie)
#listEtats=list(EnumEtatArticle)
sous_categories=[]
listesCatHommes =list(SousCategorieHomme)
listesCatFemmes =list(SousCategorieFemmme)
icons = {
        'Femmes': 'fas fa-utensils',
        'Hommes': 'fas fa-car',
        
        
    } 

rEnum=EnumCategorie

@app.template_filter("full_date")
def dslfsdlfjlsd(date):
    return date.strftime("%d/%m/%Y à %H:%M:%S")





@app.route("/")
def index():
    # app.config['APP_NAME']="gloire"
    # print(app.config)
    return redirect(url_for("Article"))

# def recuperationTel(id_annonce):
#      # Récupérer l'Item correspondante à l'id_annonce fourni
#     Item = Item.query.filter(Item.id==id_annonce).first()
#     # Item = Item.query.get(id_annonce)

#     # Récupérer l'utilisateur correspondant à l'Item
#     user = User.query.get(Item.user_id).first()
#     return user.tel




@app.route("/Article")
def Article():
    items = getAllAnnoncePublier()
    count = len(items)
    page = request.args.get(get_page_parameter(), type=int, default=1)
    NbreElementParPage = 2
    offset = (page - 1) * NbreElementParPage
    pagination = Pagination(page=page, per_page=NbreElementParPage, total=count)
    items = items[offset: offset + NbreElementParPage]
    
    # liste pour stocker les numéros de téléphone
    # stocker les numéros de téléphone par utilisateur
    

    # Boucle sur chaque Item pour récupérer le numéro de téléphone de son auteur    
    #Bof Mon many to one m a gere ca   
            
    return render_template("/pages/index.html",
                           items=items,
                           categories=categories,
                           icons=icons,
                           count=count,
                           pagination=pagination,
                           sous_categories=sous_categories,
                           listesCatFemmes=listesCatFemmes,listesCatHommes=listesCatHommes)


@app.route("/Shop")
def Shop():
    items = getAllAnnoncePublier()
    count = len(items)
    page = request.args.get(get_page_parameter(), type=int, default=1)
    NbreElementParPage = 2
    offset = (page - 1) * NbreElementParPage
    pagination = Pagination(page=page, per_page=NbreElementParPage, total=count)
    items =  items[offset: offset + NbreElementParPage]
    
    return render_template("/pages/shop.html",   items= items,
                           categories=categories,
                           icons=icons,
                           count=count,
                           pagination=pagination,
                           sous_categories=sous_categories, listesCatFemmes=listesCatFemmes,listesCatHommes=listesCatHommes)

# ==================================Search-----Input

@app.route('/recherche-Item')
def recherche_annon():
    query = request.args.get('querygloire')
    items = Item.query.filter(Item.title.ilike(f"%{query}%")).all()
    
    count =len(items)
    if count == 0:
        return redirect(url_for('NoFilterFound'))
    
    page = request.args.get(get_page_parameter(), type=int, default=1)
    NbreElementParPage = 2
    offset = (page - 1) * NbreElementParPage
    pagination = Pagination(page=page, per_page=NbreElementParPage, total=len(items))
    items = items[offset: offset + NbreElementParPage]
    return render_template("/pages/shop.html", categories=categories, items=items,
                           icons=icons,
                           count=count,
                           pagination=pagination,
                           sous_categories=sous_categories, listesCatFemmes=listesCatFemmes,listesCatHommes=listesCatHommes)

@app.route('/no-filter-found')
def NoFilterFound():
    return render_template("errors/no_filter_found.html")



@app.route('/Item/Sacs')
def Sacs_articles():
    items = Item.query.filter_by(sous_categories=SousCategorieFemmme.sac).all()
    count =len(items)
    page = request.args.get(get_page_parameter(), type=int, default=1)
    NbreElementParPage = 2
    offset = (page - 1) * NbreElementParPage
    pagination = Pagination(page=page, per_page=NbreElementParPage, total=len(items))
    items = items[offset: offset + NbreElementParPage]
    sous_categories = SousCategorieFemmme.__members__.values()
    return render_template("/pages/shop.html", categories=categories, items=items,
                           icons=icons,
                           count=count,
                           pagination=pagination,
                           sous_categories=sous_categories, listesCatFemmes=listesCatFemmes,listesCatHommes=listesCatHommes)

@app.route('/Item/Robes')
def Robes_articles():
    items = Item.query.filter_by(sous_categories=SousCategorieFemmme.robe).all()
    count =len(items)
    page = request.args.get(get_page_parameter(), type=int, default=1)
    NbreElementParPage = 2
    offset = (page - 1) * NbreElementParPage
    pagination = Pagination(page=page, per_page=NbreElementParPage, total=len(items))
    items = items[offset: offset + NbreElementParPage]
    sous_categories = SousCategorieFemmme.__members__.values()
    return render_template("/pages/shop.html", categories=categories, items=items,
                           icons=icons,
                           count=count,
                           pagination=pagination,
                           sous_categories=sous_categories, listesCatFemmes=listesCatFemmes,listesCatHommes=listesCatHommes)



# =====================================================================
# =============================Details Annonces===========================
# =====================================================================
# Test
@app.route("/Item/<int:id_item>")
def annonce_Id(id_item):
    item = findAnnonceById(id_item)    
    # nbreEtoiles = Item.query(func.avg(Ratings.rating)).filter_by(annonce_id=id_annonce).scalar()
    if not item:
        return redirect(url_for("/"))
    return render_template("/pages/detailsArticles.html",item=item)



@app.route("/Contact")
def Contact():
    return render_template("/pages/contact.html")



@app.route("/details")
def Details():
    return render_template("/pages/detailsArticles.html")





@app.route("/Annonce_A_La_Une")
def annonceA_la_une():
    annonces = getAllAnnonceA_La_Une()
   
    count =len(annonces)
    page = request.args.get(get_page_parameter(), type=int, default=1)
    NbreElementParPage = 2
    offset = (page - 1) * NbreElementParPage
    pagination = Pagination(page=page, per_page=NbreElementParPage, total=len(annonces))
    annonces = annonces[offset: offset + NbreElementParPage]
    
    return render_template("/pages/accueil.html",annonces=annonces,categories=categories,icons=icons,count=count,pagination=pagination)





# =====================================================================
# =============================Lien Nav Bleu===========================
# =====================================================================



@app.route('/Item/Hommes')
def Vehicules_articles():
    sous_categories = SousCategorieHomme.__members__.values()
    return render_template("/pages/vehicules.html",sous_categories=sous_categories)

#==============04
@app.route('/Item/Femmes')
def Maison_articles():
    annonces = Item.query.filter_by(categorie=EnumCategorie.Maison.name).all()
    count =len(annonces)
    page = request.args.get(get_page_parameter(), type=int, default=1)
    NbreElementParPage = 2
    offset = (page - 1) * NbreElementParPage
    pagination = Pagination(page=page, per_page=NbreElementParPage, total=len(annonces))
    annonces = annonces[offset: offset + NbreElementParPage]
    sous_categories = SousCategorieFemmme.__members__.values()
    return render_template("/pages/index.html",annonces=annonces,categories=categories,icons=icons,count=count,rEnum=rEnum.Maison.name,pagination=pagination,sous_categories=sous_categories)


#==============07

#==============08


# =============================Fin Lien Nav Bleu===========================



# =====================================================================
# ============--------------Recherche Annonces-----------==============
# =====================================================================

# =====================Search-----Categorie
@app.route('/Ann')
def articles_par_categorie():
    categorie = request.args.get('categorie')
    
    if categorie is None:
        # Si la catégorie n'est pas spécifiée, afficher toutes les annonces
        annonces = Item.query.all()
        count =len(annonces)
    else:
        # Si la catégorie est spécifiée, filtrer par catégorie
        annonces = Item.query.filter_by(categorie=categorie).all()
        # count =Item.query.filter_by(categorie=categorie).count()
        count=len(annonces) 
    page = request.args.get(get_page_parameter(), type=int, default=1)
    NbreElementParPage = 2
    offset = (page - 1) * NbreElementParPage
    pagination = Pagination(page=page, per_page=NbreElementParPage, total=len(annonces))
    annonces = annonces[offset: offset + NbreElementParPage]
        
    
  
    return render_template("/pages/index.html",annonces=annonces,categories=categories,icons=icons,count=count,rEnum=categorie,pagination=pagination)




@app.route('/AnnSousCategorie')
def articles_par_sous_categorie():
    categor = request.args.get('categor')
    souscategor = request.args.get('souscategor')
    
    if categor is None:
        # =====================Si la catégorie n'est pas spécifiée, afficher toutes les annonces
        annonces = Item.query.all()
        count =len(annonces)
    else:
        # =================Si la catégorie est spécifiée, filtrer par catégorie
        annonces = Item.query.filter_by(categorie=categor,sousCategorie=souscategor).all()
        # count =Item.query.filter_by(categorie=categorie).count()
        count=len(annonces) 
    page = request.args.get(get_page_parameter(), type=int, default=1)
    NbreElementParPage = 2
    offset = (page - 1) * NbreElementParPage
    pagination = Pagination(page=page, per_page=NbreElementParPage, total=len(annonces))
    annonces = annonces[offset: offset + NbreElementParPage]
        
    
    return render_template("/pages/index.html",annonces=annonces,categories=categories,icons=icons,count=count,pagination=pagination)



# =====================Search-----Lieu
@app.route('/Ann_lieu')
def articles_par_lieu():
    lieu = request.args.get('lieu')
    
    if lieu is None:
        # Si la catégorie n'est pas spécifiée, afficher toutes les annonces
        annonces = Item.query.all()
        count =len(annonces)
    else:
        # Si la catégorie est spécifiée, filtrer par catégorie
        annonces = Item.query.filter_by(lieuPub=lieu).all()
        count_lieu =Item.query.filter_by(lieuPub=lieu).count()
    page = request.args.get(get_page_parameter(), type=int, default=1)
    NbreElementParPage = 2
    offset = (page - 1) * NbreElementParPage
    pagination = Pagination(page=page, per_page=NbreElementParPage, total=len(annonces))
    annonces = annonces[offset: offset + NbreElementParPage]
        
    
    return render_template("/pages/index.html",annonces=annonces,categories=categories,icons=icons,count_lieu=count_lieu,pagination=pagination)


# =====================Search-----Lieu
@app.route('/Ann_Prix')
def annonces_par_Prix():
    prixmaxRecup=request.args.get('max-priceIndex')
    prixminRecup=request.args.get('min-priceIndex')

    if prixmaxRecup is not None and prixminRecup is not None:
        annonces=Item.query.filter(Item.prix.between(prixminRecup,prixmaxRecup)).all()

    else:
        # Si la catégorie est spécifiée, filtrer par catégorie
        annonces = Item.query.all()
    page = request.args.get(get_page_parameter(), type=int, default=1)
    NbreElementParPage = 2
    offset = (page - 1) * NbreElementParPage
    pagination = Pagination(page=page, per_page=NbreElementParPage, total=len(annonces))
    annonces = annonces[offset: offset + NbreElementParPage]
        
    
    return render_template("/pages/index.html",annonces=annonces,categories=categories,icons=icons,pagination=pagination)



# afficher les annonces filtrées
@app.route('/annoncesTri', methods=['GET', 'POST'])
def afficher_annoncesTri():
    if request.method == 'POST':
        tri = request.form['tri']
        if tri == 'croissant':
            annonces = Item.query.order_by(Item.prix.asc()).all()
        elif tri == 'decroissant':
            annonces = Item.query.order_by(Item.prix.desc()).all()
        elif tri == 'recents':
            annonces = Item.query.order_by(Item.datePub.desc()).all()
        else:
            return 'Tri invalide'
    else:
        annonces = Item.query.all()

    count =len(annonces)
    page = request.args.get(get_page_parameter(), type=int, default=1)
    NbreElementParPage = 2
    offset = (page - 1) * NbreElementParPage
    pagination = Pagination(page=page, per_page=NbreElementParPage, total=len(annonces))
    annonces = annonces[offset: offset + NbreElementParPage]
    return render_template("/pages/index.html",annonces=annonces,categories=categories,icons=icons,count=count,pagination=pagination)


# =====================================================================
# =============================Voiture===========================
# =====================================================================
@app.route('/Filtre_desNeuf_Voitures')
def Filtre_desNeuf_Voitures():
    recolte = request.args.get('recolteMarque')
    annonces = Item.query.filter(Item.description.ilike(f"%{recolte}%")).all()
    
    count =len(annonces)
    page = request.args.get(get_page_parameter(), type=int, default=1)
    NbreElementParPage = 2
    offset = (page - 1) * NbreElementParPage
    pagination = Pagination(page=page, per_page=NbreElementParPage, total=len(annonces))
    annonces = annonces[offset: offset + NbreElementParPage]
    return render_template("/pages/index.html",annonces=annonces,categories=categories,icons=icons,count=count,pagination=pagination)



@app.route('/Filtre_All')
def Filtre_Voitures_All():
    
    annonces = (Item.query.filter(Item.published == 1, Item.deleted == 0,Item.categorie==EnumCategorie.Vehicules.name)
        .order_by(desc(Item.datePub))
        .all())
    count =len(annonces)
    page = request.args.get(get_page_parameter(), type=int, default=1)
    NbreElementParPage = 2
    offset = (page - 1) * NbreElementParPage
    pagination = Pagination(page=page, per_page=NbreElementParPage, total=len(annonces))
    annonces = annonces[offset: offset + NbreElementParPage]
    return render_template("/pages/index.html",annonces=annonces,categories=categories,icons=icons,count=count,pagination=pagination)




@app.route("/FiltreVehicules")
def vehicules():
    #sousCategorieRecup=request.args.get('sousCategorie')
    CategoryRecup=request.args.get('Categories')
    #lieuxRecup=request.args.get('region')
    prixmaxRecup=request.args.get('max-price')
    prixminRecup=request.args.get('min-price')
    sousCategorieRecup=request.args.get('sousCategorie')
    if prixmaxRecup is not None and prixminRecup is not None and sousCategorieRecup is None :
        annonces=Item.query.filter(Item.prix.between(prixminRecup,prixmaxRecup)).all()
        
        
    if sousCategorieRecup is not None and prixmaxRecup is None and prixminRecup is None:
        annonces=Item.query.filter(Item.sousCategorie==sousCategorieRecup).all()
    annonces=Item.query.filter(Item.prix.between(prixminRecup,prixmaxRecup),Item.categorie==CategoryRecup).all()
    count =len(annonces)
    
    
    page = request.args.get(get_page_parameter(), type=int, default=1)
    NbreElementParPage = 2
    offset = (page - 1) * NbreElementParPage
    pagination = Pagination(page=page, per_page=NbreElementParPage, total=len(annonces))
    annonces = annonces[offset: offset + NbreElementParPage]
    
    return render_template("/pages/index.html",annonces=annonces,categories=categories,icons=icons,count=count,pagination=pagination)




# ===================================================================
# =============================Chat Envoye Recevoir Avec Socketio  =========================================
# =====================================================================

#====================je vais dans mon fichier special.py

# messages = []  # Liste pour stocker les messages

# @app.route('/chat/<int:article_id>')
# def chat(article_id):
#     Item = Item.query.get(article_id)
#     if Item:
#         article_author = Item.users.nom
#         return render_template("/pages/chat.html", article_author=article_author)
#     else:
#         return "Article not found"

# @socketio.on('connect')
# def handle_connect():
#     print('Client connected!')

# @socketio.on('user_join')
# def handle_user_join(username):
#     print(f'User {username} joined!')

# @socketio.on('new_message')
# def handle_new_message(data):
#     message = data['message']
#     recipient = data['recipient']
#     sender = None

#     for sid, user in socketio.server.manager.rooms[''].items():
#         if user == request.sid:
#             sender = sid
#             break

#     if recipient == article_author:
#         emit('chat', {'message': message, 'sender': sender, 'recipient': recipient}, room=recipient)
#     else:
#         emit('chat', {'message': message, 'sender': sender}, broadcast=True)

#         # Ajouter le message à la liste
#         messages.append({'sender': sender, 'message': message})



# @app.route('/Item/Recent', methods=['POST'])
# def process_form():
#     selected_value = request.form['select_field']
#     annonces = getAnnoncesByDate('2023-03-28 03:37:35.970126')
#     # Do something with the selected value
#     return render_template("/pages/index.html",annonces=annonces,categories=categories,icons=icons)
    








# @app.route('/')
# def index():
#     # Accessing Enum members:
#     my_etat =EnumEtatArticle.Reconditione.name

#     # return 'my_etat is {}'.format(my_etat.value)
#     return 'my_etat is {}'.format(my_etat)


# articles = Article.query.order_by(Article.prix.asc()).all()
# articles = Article.query.order_by(Article.prix.desc()).all()
# # récupère les 10 articles les plus récents
# articles = Article.query.order_by(Article.date.desc()).limit(10).all()


