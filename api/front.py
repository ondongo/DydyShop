import re
from flask import Flask, abort, render_template, redirect, session, url_for, request
from flask_login import current_user
import requests
from sqlalchemy import desc
from api.models.EnumColorAndSize import *
from api.models.EnumCategorie import *
from api.models.SousCategorie import *
from flask_paginate import Pagination, get_page_parameter
from sqlalchemy import or_

# ----------Fichier Principal-------------
app = Flask(__name__)

# Montrer a flask la ou se trouve notre fichier de config Flask
# app.config.from_object("config"))
# Pagination des pages
# pagination = Pagination(app)

app.config.from_object("config")


from api.models.model import (
    CartItem,
    Category,
    Image,
    SubCategory,
    User,
    findAnnonceById,
    Item,
    getAllAnnoncePublier,
    getAllAnnonceA_La_Une,
    getAllAnnonceRecent,
  
)

categories = list(EnumCategorie)
sous_categories = []
listesCatHommes = list(SousCategorieHomme)
listesCatFemmes = list(SousCategorieFemmme)
icons = {
    "Femmes": "fas fa-utensils",
    "Hommes": "fas fa-car",
}

rEnum = EnumCategorie


@app.template_filter("full_date")
def dslfsdlfjlsd(date):
    return date.strftime("%d/%m/%Y à %H:%M:%S")


@app.route("/")
def index():
    return redirect(url_for("Article"))


@app.route("/Article")
def Article():
    items = getAllAnnoncePublier()
    # annoncesTuniques = Item.query.filter_by(
    # categorie=SousCategorieHomme.tunique.name
    # ).all()
    # annoncesSac = Item.query.filter_by(categorie=SousCategorieFemmme.sac.name).all()
    # annoncesEnsemble = Item.query.filter_by(
    # categorie=SousCategorieFemmme.ensemble.name
    # ).all()
    # countTuniques = len(annoncesTuniques)
    # countSac = len(annoncesSac)
    # countEnsemble = len(annoncesEnsemble)

    if current_user.is_authenticated:
        # Utilisateur connecté, récupérez le panier depuis la base de données
        user_id = current_user.id

        user_cart_items = CartItem.query.filter_by(user_id=user_id).all()
        total_amount = sum(
            cart_item.item.prix * cart_item.quantity
            for cart_item in user_cart_items
            if cart_item.item is not None and cart_item.quantity is not None
        )

    else:
        total_amount = session.get("total", 0.0)

    count = len(items)
    page = request.args.get(get_page_parameter(), type=int, default=1)
    NbreElementParPage = 2
    offset = (page - 1) * NbreElementParPage
    pagination = Pagination(page=page, per_page=NbreElementParPage, total=count)
    items = items[offset : offset + NbreElementParPage]

    trending_products = Item.query.order_by(desc(Item.nbre_vues)).limit(3).all()
    three_lowest_price_items = Item.query.order_by(Item.prix.asc()).limit(3).all()
    best_sales = Item.query.order_by(desc(Item.nbre_vues)).limit(3).all()
    # getBestSellingItems()

    # Items Sections
    four_all_items = Item.query.order_by(Item.prix.asc()).limit(4).all()

    return render_template(
        "/pages/index.html",
        items=items,
        categories=categories,
        icons=icons,
        count=count,
        countTuniques=0,
        countSac=0,
        countEnsemble=0,
        three_lowest_price_items=three_lowest_price_items,
        trending_products=trending_products,
        best_sales=best_sales,
        pagination=pagination,
        four_all_items=four_all_items,
        total_amount=total_amount,
    )


@app.route("/Shop")
def Shop():
    items = getAllAnnoncePublier()
    # Récupérez la liste des catégories
    categories = Category.query.all()

    # Récupérez la liste des sous-catégories (vous pouvez ajuster cela en fonction de votre modèle de données)
    sous_categories_femmes = SubCategory.query.filter_by(category_id=1).all()
    sous_categories_hommes = SubCategory.query.filter_by(category_id=2).all()

    count = len(items)
    page = request.args.get(get_page_parameter(), type=int, default=1)
    NbreElementParPage = 10
    offset = (page - 1) * NbreElementParPage
    pagination = Pagination(page=page, per_page=NbreElementParPage, total=count)
    items = items[offset : offset + NbreElementParPage]

    return render_template(
        "/pages/shop.html",
        items=items,
        categories=categories,
        icons=icons,
        count=count,
        pagination=pagination,
        sous_categories_femmes=sous_categories_femmes,
        sous_categories_hommes=sous_categories_hommes,
    )


# ==================================Search-----Input
@app.route("/display_Shop")
def display_Shop():
    # Récupérez la liste des catégories
    categories = Category.query.all()

    # Récupérez la liste des sous-catégories (vous pouvez ajuster cela en fonction de votre modèle de données)
    sous_categories_femmes = SubCategory.query.filter_by(category_id=1).all()
    sous_categories_hommes = SubCategory.query.filter_by(category_id=2).all()

    # Récupérez les paramètres de la requête
    category = request.args.get("category")
    subcategory = request.args.get("subcategory")
    size = request.args.get("size")
    color = request.args.get("color")
    min_price = request.args.get("min_price")
    max_price = request.args.get("max_price")
    sort_by_price = request.args.get("sort_by_price")

    # Construisez la requête de base pour les articles
    query = getAllAnnoncePublier()

    # Ajoutez des filtres en fonction des paramètres de la requête
    if category:
        query = Item.query.filter(Item.category_id == category)

    if subcategory:
        query = Item.query.filter(Item.subcategory_id == subcategory)

    if size:
        # Filtrer par taille (utilisez la table de liaison item_sizes)
        query = Item.query.filter(
            or_(Item.size1 == size, Item.size2 == size, Item.size3 == size)
        )

    if color:
        # Filtrer par couleur (utilisez la table de liaison item_colors)
        query = Item.query.filter(
            or_(Item.color1 == color, Item.color2 == color, Item.color3 == color)
        )

    if min_price and max_price:
        query = Item.query.filter(Item.prix.between(min_price, max_price))

    # Ajoutez le tri par prix
    if sort_by_price == "asc":
        query = Item.query.order_by(Item.prix.asc())
    elif sort_by_price == "desc":
        query = Item.query.order_by(Item.prix.desc())

    # Exécutez la requête
    items = query.all()
    count = len(items)

    # Pagination
    page = request.args.get(get_page_parameter(), type=int, default=1)
    items_per_page = 2
    offset = (page - 1) * items_per_page
    pagination = Pagination(page=page, per_page=items_per_page, total=len(items))
    items = items[offset : offset + items_per_page]

    return render_template(
        "/pages/shop.html",
        items=items,
        categories=categories,
        icons=icons,
        pagination=pagination,
        count=count,
        sous_categories_femmes=sous_categories_femmes,
        sous_categories_hommes=sous_categories_hommes,
    )


@app.route("/recherche-Item")
def recherche_annon():
    query = request.args.get("querygloire")
    items = Item.query.filter(Item.title.ilike(f"%{query}%")).all()
    # Récupérez la liste des sous-catégories (vous pouvez ajuster cela en fonction de votre modèle de données)
    sous_categories_femmes = SubCategory.query.filter_by(category_id=1).all()
    sous_categories_hommes = SubCategory.query.filter_by(category_id=2).all()
    categories = Category.query.all()

    count = len(items)
    if count == 0:
        return redirect(url_for("NoFilterFound"))

    page = request.args.get(get_page_parameter(), type=int, default=1)
    NbreElementParPage = 2
    offset = (page - 1) * NbreElementParPage
    pagination = Pagination(page=page, per_page=NbreElementParPage, total=len(items))
    items = items[offset : offset + NbreElementParPage]
    return render_template(
        "/pages/shop.html",
        categories=categories,
        items=items,
        icons=icons,
        count=count,
        pagination=pagination,
        sous_categories=sous_categories,
        sous_categories_femmes=sous_categories_femmes,
        sous_categories_hommes=sous_categories_hommes,
    )


@app.route("/no-filter-found")
def NoFilterFound():
    return render_template("errors/no_filter_found.html")


# =====================================================================
# =============================Details Annonces===========================
# =====================================================================


def get_color_name_from_hex_api(hex_color):
    hex_color_without_hash = re.sub(r"#", "", hex_color)
    hex_color_upper = hex_color_without_hash.upper()
    url = f"https://www.thecolorapi.com/id?hex={hex_color_upper}"

    try:
        response = requests.get(url)
        data = response.json()

        if response.status_code == 200:
            color_name = data["name"]["value"]
            return color_name
        else:
            print(f"Erreur: {data['error']['message']}")

    except Exception as e:
        print(f"Erreur lors de la requête à l'API : {e}")


""" # Exemple d'utilisation :
hex_color = "7F00FF"
color_name = get_color_name_from_hex_api(hex_color)

if color_name:
    print(f"Le nom de la couleur pour {hex_color} est : {color_name}")

else:
    print(f"Aucune correspondance trouvée pour {hex_color}")
 """


@app.route("/Item/<int:id_item>")
def annonce_Id(id_item):
    item = findAnnonceById(id_item)
    # nbreEtoiles = Item.query(func.avg(Ratings.rating)).filter_by(annonce_id=id_annonce).scalar()
    unique_colors = list(set([item.color1, item.color2, item.color3]))
    color_names = [
        get_color_name_from_hex_api(color) for color in unique_colors if color
    ]

    unique_colors_with_names = list(zip(unique_colors, color_names))
    user = User.query.get(current_user.id)
    annonces_favoris = user.favorites
    annonces_favoris_ids = [fav.annonce_id for fav in user.favorites]
    similar_items = (
        Item.query.filter(
            Item.subcategory_id == item.subcategory_id,
            Item.id != item.id,
            Item.deleted == False,
        )
        .order_by(Item.date_pub.desc())
        .limit(4)
        .all()
    )

    if not item:
        return redirect(url_for("/"))
    return render_template(
        "/pages/detailsArticles.html",
        item=item,
        unique_colors_with_names=unique_colors_with_names,
        similar_items=similar_items,
        annonces_favoris=annonces_favoris,
        annonces_favoris_ids=annonces_favoris_ids,
    )


@app.route("/Contact")
def Contact():
    return render_template("/pages/contact.html")


@app.route("/Faqs")
def Faqs():
    return render_template("/pages/faqs.html")


@app.route("/Tracking-order")
def Tracking():
    return render_template("/pages/checkout.html")


# ===================================================================
# =============================Chat Envoye Recevoir Avec Socketio  =========================================
# =====================================================================

# ====================je vais dans mon fichier special.py

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
