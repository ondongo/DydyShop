import re
from flask import Flask, abort, render_template, redirect, session, url_for, request
from flask_login import current_user
import requests
from sqlalchemy import desc, func
from api.models.EnumColorAndSize import *
from api.models.EnumCategorie import *
from api.models.SousCategorie import *
from flask_paginate import Pagination, get_page_parameter
from sqlalchemy import or_
from flask_babel import Babel
from flask import g, request
from flask_talisman import Talisman

def get_locale():
    # if a user is logged in, use the locale from the user settings
    user = getattr(g, "user", None)
    if user is not None:
        return user.locale
    # otherwise try to guess the language from the user accept
    # header the browser transmits.  We support de/fr/en in this
    # example.  The best match wins.
    return request.accept_languages.best_match(["de", "fr", "en"])


def get_timezone():
    user = getattr(g, "user", None)
    if user is not None:
        return user.timezone


app = Flask(__name__)
Talisman(app, content_security_policy=None, force_https=True)
app.config.from_object("config")
babel = Babel(app, locale_selector=get_locale, timezone_selector=get_timezone)

from api.models.model import (
    CartItem,
    Category,
    Favorite,
    Image,
    Review,
    SubCategory,
    User,
    findAnnonceById,
    Item,
    getAllAnnoncePublier,
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

    total_amount = 0.0
    favoris_count = 0
    carts_count = 0

    if current_user.is_authenticated:
        user_id = current_user.id

        user_cart_items = CartItem.query.filter_by(user_id=user_id).all()

        # Retrieve the count of items in the user's shopping cart
        carts_count = CartItem.query.filter_by(user_id=user_id).count()

        # Retrieve the count of items in the user's favorites
        favoris_count = Favorite.query.filter_by(user_id=user_id).count()

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
        favoris_count=favoris_count,
        carts_count=carts_count,
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

    favoris_count = 0
    carts_count = 0

    if current_user.is_authenticated:
        user_id = current_user.id

        user_cart_items = CartItem.query.filter_by(user_id=user_id).all()

        # Retrieve the count of items in the user's shopping cart
        carts_count = CartItem.query.filter_by(user_id=user_id).count()

        # Retrieve the count of items in the user's favorites
        favoris_count = Favorite.query.filter_by(user_id=user_id).count()

        total_amount = sum(
            cart_item.item.prix * cart_item.quantity
            for cart_item in user_cart_items
            if cart_item.item is not None and cart_item.quantity is not None
        )

    else:
        total_amount = session.get("total", 0.0)

    return render_template(
        "/pages/shop.html",
        items=items,
        categories=categories,
        icons=icons,
        count=count,
        pagination=pagination,
        sous_categories_femmes=sous_categories_femmes,
        sous_categories_hommes=sous_categories_hommes,
        total_amount=total_amount,
        favoris_count=favoris_count,
        carts_count=carts_count,
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

    query = getAllAnnoncePublier()

    if category:
        query = Item.query.filter(Item.category_id == category)

    if subcategory:
        query = Item.query.filter(Item.subcategory_id == subcategory)

    if size:
        query = Item.query.filter(
            or_(Item.size1 == size, Item.size2 == size, Item.size3 == size)
        )

    if color:
        query = Item.query.filter(
            or_(Item.color1 == color, Item.color2 == color, Item.color3 == color)
        )

    if min_price and max_price:
        query = Item.query.filter(Item.prix.between(min_price, max_price))

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

    favoris_count = 0
    carts_count = 0

    if current_user.is_authenticated:
        user_id = current_user.id

        user_cart_items = CartItem.query.filter_by(user_id=user_id).all()

        carts_count = CartItem.query.filter_by(user_id=user_id).count()

        favoris_count = Favorite.query.filter_by(user_id=user_id).count()

        total_amount = sum(
            cart_item.item.prix * cart_item.quantity
            for cart_item in user_cart_items
            if cart_item.item is not None and cart_item.quantity is not None
        )

    else:
        total_amount = session.get("total", 0.0)

    return render_template(
        "/pages/shop.html",
        items=items,
        categories=categories,
        icons=icons,
        pagination=pagination,
        count=count,
        sous_categories_femmes=sous_categories_femmes,
        sous_categories_hommes=sous_categories_hommes,
        total_amount=total_amount,
        favoris_count=favoris_count,
        carts_count=carts_count,
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

    favoris_count = 0
    carts_count = 0

    if current_user.is_authenticated:
        user_id = current_user.id

        user_cart_items = CartItem.query.filter_by(user_id=user_id).all()

        carts_count = CartItem.query.filter_by(user_id=user_id).count()

        favoris_count = Favorite.query.filter_by(user_id=user_id).count()

        total_amount = sum(
            cart_item.item.prix * cart_item.quantity
            for cart_item in user_cart_items
            if cart_item.item is not None and cart_item.quantity is not None
        )

    else:
        total_amount = session.get("total", 0.0)
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
        total_amount=total_amount,
        favoris_count=favoris_count,
        carts_count=carts_count,
    )


@app.route("/no-filter-found")
def NoFilterFound():
    favoris_count = 0
    carts_count = 0
    if current_user.is_authenticated:
        user_id = current_user.id

        user_cart_items = CartItem.query.filter_by(user_id=user_id).all()

        carts_count = CartItem.query.filter_by(user_id=user_id).count()

        favoris_count = Favorite.query.filter_by(user_id=user_id).count()

        total_amount = sum(
            cart_item.item.prix * cart_item.quantity
            for cart_item in user_cart_items
            if cart_item.item is not None and cart_item.quantity is not None
        )
    return render_template(
        "errors/no_filter_found.html",
        favoris_count=favoris_count,
        carts_count=carts_count,
    )


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

    total_amount = 0.0
    favoris_count = 0
    carts_count = 0
    annonces_favoris = []
    annonces_favoris_ids = []

    average_rating = (
        Review.query.with_entities(func.avg(Review.rating))
        .filter_by(item_id=id_item)
        .scalar()
    )

    average_rating = average_rating or 0.0

    if current_user.is_authenticated:
        user_id = current_user.id

        user_cart_items = CartItem.query.filter_by(user_id=user_id).all()

        user = User.query.get(current_user.id)
        annonces_favoris = user.favorites
        annonces_favoris_ids = [fav.annonce_id for fav in user.favorites]

        carts_count = CartItem.query.filter_by(user_id=user_id).count()

        favoris_count = Favorite.query.filter_by(user_id=user_id).count()

        total_amount = sum(
            cart_item.item.prix * cart_item.quantity
            for cart_item in user_cart_items
            if cart_item.item is not None and cart_item.quantity is not None
        )

    else:
        total_amount = session.get("total", 0.0)

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
        carts_count=carts_count,
        favoris_count=favoris_count,
        total_amount=total_amount,
        average_rating=average_rating,
    )


@app.route("/Faqs")
def Faqs():
    return render_template("/pages/faqs.html")


@app.route("/Tracking-order")
def Tracking():
    return render_template("/pages/tracking.html")
