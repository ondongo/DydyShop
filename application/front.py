from flask import Flask, abort, render_template, redirect, url_for, request
from sqlalchemy import desc
from application.models.EnumColorAndSize import *
from application.models.EnumCategorie import *
from application.models.SousCategorie import *
from flask_paginate import Pagination, get_page_parameter
from sqlalchemy import or_

# ----------Fichier Principal-------------
app = Flask(__name__)

# Montrer a flask la ou se trouve notre fichier de config Flask
# app.config.from_object("config"))
# Pagination des pages
# pagination = Pagination(app)

app.config.from_object("config")


from application.models.model import (
    Category,
    SubCategory,
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
    count = len(items)
    page = request.args.get(get_page_parameter(), type=int, default=1)
    NbreElementParPage = 2
    offset = (page - 1) * NbreElementParPage
    pagination = Pagination(page=page, per_page=NbreElementParPage, total=count)
    items = items[offset : offset + NbreElementParPage]

    tendances = getAllAnnonceA_La_Une()
    low_price = getAllAnnonceA_La_Une()
    best_sales = getAllAnnonceA_La_Une()
    recents = getAllAnnonceRecent()

    return render_template(
        "/pages/index.html",
        items=items,
        categories=categories,
        icons=icons,
        count=count,
        countTuniques=0,
        countSac=0,
        countEnsemble=0,
        pagination=pagination,
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
    NbreElementParPage = 2
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
        listesCatFemmes=listesCatFemmes,
        listesCatHommes=listesCatHommes,
    )


@app.route("/no-filter-found")
def NoFilterFound():
    return render_template("errors/no_filter_found.html")


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
    return render_template("/pages/detailsArticles.html", item=item)


@app.route("/Contact")
def Contact():
    return render_template("/pages/contact.html")


@app.route("/details")
def Details():
    return render_template("/pages/detailsArticles.html")


# =====================================================================
# ============--------------Recherche Annonces-----------==============
# =====================================================================


# =====================Search-----Lieu
