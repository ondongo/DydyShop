import dbm
from .front import app

from flask import abort, render_template, request, redirect, url_for, flash, session
from application.models.EnumColorAndSize import *
from application.models.EnumCategorie import *
from application.models.SousCategorie import *
from .front import app
from sqlalchemy import desc
from flask_login import login_required
from flask_paginate import Pagination, get_page_parameter

# from flask_oauthlib.client import OAuth
# Hash password
import hashlib
from flask_login import (
    LoginManager,
    login_user,
    logout_user,
    login_required,
    current_user,
)
from flask_uploads import UploadSet, configure_uploads, IMAGES, UploadNotAllowed

login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message_category = "info"
from functools import wraps
from twilio.rest import Client


# =====================================================================
# =============================Import Model===========================
# =====================================================================

from application.models.model import (
    CartItem,
    Category,
    Item,
    Favorite,
    SubCategory,
    add_favori,
    add_images_to_item,
    create_item,
    getAllAnnonceBrouillon,
    getAllAnnonceDel,
    transfer_session_cart_to_db_cart,
    un_delete,
    un_deleteFavorite,
    un_published,
    editAnnonceModel,
    User,
    saveUser,
    updateSession,
    updatecategory,
    updatesubcategory,
)


listcategories = list(EnumCategorie)


def admin_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if current_user.is_authenticated and "admin" in current_user.roles:
            return func(*args, **kwargs)
        else:
            # Gérer le cas où l'utilisateur n'est pas autorisé (redirection, message d'erreur, etc.)
            abort(403)

    return decorated_view


#
# =======================================================================================================================
# ============================= Gestion Du Crud Dashboard ===================================================================
# =======================================================================================================================
#


@app.route("/add_category", methods=["GET", "POST"])
def add_category():
    categories = Category.query.all()
    if request.method == "POST":
        name = request.form.get("name")
        if name:
            category = Category(name=name)
            updatecategory(category)
            flash("Catégorie ajoutée avec succès.", "success")
            return redirect(url_for("add_category"))

    return render_template("/back/AddCategory.html", categories=categories)


@app.route("/add_subcategory", methods=["GET", "POST"])
def add_subcategory():
    categories = Category.query.all()
    subcategories = SubCategory.query.all()
    if request.method == "POST":
        name = request.form.get("name")
        category_id = request.form.get("category")
        if name and category_id:
            subcategory = SubCategory(name=name, category_id=category_id)
            updatesubcategory(subcategory)
            flash("Sous-catégorie ajoutée avec succès.", "success")
            return redirect(url_for("add_subcategory"))

    return render_template(
        "/back/AddSubcategory.html", categories=categories, subcategories=subcategories
    )


# Configuration Flask-Uploads
photos = UploadSet("photos", IMAGES)
app.config["UPLOADED_PHOTOS_DEST"] = "uploads"
configure_uploads(app, photos)


@app.route("/add_item", methods=["GET", "POST"])
@admin_required
def add_item():
    subcategories = SubCategory.query.all()
    if request.method == "POST":
        # Traitement du formulaire d'ajout d'article ici
        try:
            validate_and_save_annonce(request)
            print("Annonce enregistrée avec succès.")
            flash("Annonce enregistrée avec succès.", "success")
        except UploadNotAllowed as e:
            flash(f"Type de fichier non autorisé : {str(e)}", "danger")
        except Exception as e:
            flash(f"Erreur lors de l'enregistrement de l'annonce : {str(e)}", "danger")
            print(f"Erreur lors de l'enregistrement de l'annonce : {str(e)}")

        return redirect(url_for("gestiondash"))

    # Si la méthode est GET, simplement afficher la page d'ajout d'article
    return render_template("back/AddItem.html", subcategories=subcategories)


def validate_and_save_annonce(request):
    id_annonce = request.form.get("id_annonce")
    title_form = request.form.get("title")
    sous_categorie_form = request.form.get("sous_categorie")
    categorie_form = request.form.get("categorie_hidden")
    description_form = request.form.get("description")
    prix_form = request.form.get("price")
    # publish_form = bool(request.form.get("publish"))
    quantity_form = request.form.get("quantity")
    size1_form = request.form.get("size1")
    size2_form = request.form.get("size2")
    size3_form = request.form.get("size3")

    color1_form = request.form.get("color1")
    color2_form = request.form.get("color2")
    color3_form = request.form.get("color3")
    img_form = request.form.get("img_url")
    if size1_form:
        size1_result = "Petite"

    if size2_form:
        size2_result = "Moyenne"

    if size3_form:
        size3_result = "Grande"
    # Vérifiez chaque image téléchargée
    for image in request.files.getlist("images"):
        if image:
            # Vérifiez le format de l'image
            if not allowed_file(image.filename):
                raise UploadNotAllowed("Format d'image non autorisé.")

            # Vérifiez la taille de l'image
            if len(image.read()) > MAX_IMAGE_SIZE_BYTES:
                raise UploadNotAllowed("L'image dépasse la taille maximale autorisée.")
            image.seek(0)

    new_annonce = Item(
        title=title_form,
        description=description_form,
        prix=prix_form,
        user_id=current_user.id,
        subcategory_id=sous_categorie_form,
        category_id=categorie_form,
        quantity=quantity_form,
        color1=color1_form,
        color2=color2_form,
        color3=color3_form,
        size1=size1_result,
        size2=size2_result,
        size3=size3_result,
        img_url=img_form,
    )

    create_item(new_annonce)
    add_images_to_item(new_annonce, request.files.getlist("images"))

    print(">>>>>>>>>>>>>>>>>>>>>", new_annonce)


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in {
        "png",
        "jpg",
        "jpeg",
        "gif",
    }


MAX_IMAGE_SIZE_BYTES = 5 * 1024 * 1024


@app.route("/admin/edit/<int:id_annonce>", methods=["GET", "POST"])
@login_required
@admin_required
def editAnnonce(id_annonce):
    Item = Item.query.get(id_annonce)
    return render_template(
        "/back/editArticle.html", Item=Item, listcategories=listcategories
    )


@app.route("/edit", methods=["POST"])
def edit():
    id_annonce = request.form.get("id_annonce")
    Item = Item.query.get(id_annonce)
    if Item:
        Item.title = request.form.get("title")
        Item.categorie = request.form.get("categorie")
        Item.sousCategorie = request.form.get("sous_categorie")
        Item.description = request.form.get("description")
        Item.prix = request.form.get("prix")
        Item.published = False if not request.form.get("publish") else True
        Item.img_url = request.form.get("img_url")
        Item.img_title = request.form.get("img_title")
        Item.quantity = request.form.get("quantity")
        editAnnonceModel(Item)
    return redirect(url_for("gestionAnnonce"))


@app.route("/admin/gestion")
@login_required
@admin_required
def gestionArticle():
    annonces = (
        Item.query.filter(
            Item.published == 1, Item.deleted == 0, Item.user_id == current_user.id
        )
        .order_by((Item.date_pub))
        .all()
    )
    count_publier = len(annonces)
    return render_template(
        "/back/gesArticle.html",
        annonces=annonces,
        listcategories=listcategories,
        count_publier=count_publier,
    )


@app.route("/admin/dashboard")
@login_required
@admin_required
def gestiondash():
    annonces = (
        Item.query.filter(
            Item.published == 1, Item.deleted == 0, Item.user_id == current_user.id
        )
        .order_by((Item.date_pub))
        .all()
    )
    count_publier = len(annonces)
    return render_template(
        "/back/dashboard.html",
        annonces=annonces,
        listcategories=listcategories,
        count_publier=count_publier,
    )


#
# =======================================================================================================================
# ============================= Gestion Mise hors ligne , en ligne et suppression ========================================================================
# =======================================================================================================================
#


# ************************************ListCorbeille***********************************
@app.route("/admin/listings/Corbeille")
@login_required
@admin_required
def gestionAnnonce_Corbeille():
    annonces = getAllAnnonceDel()
    count_corbeille = len(annonces)
    return render_template(
        "/back/gestionAnnonce.html",
        annonces=annonces,
        listcategories=listcategories,
        count_corbeille=count_corbeille,
    )


@app.route("/admin/listings/Brouillon")
@login_required
@admin_required
def gestionAnnonce_Brouillon():
    annonces = getAllAnnonceBrouillon()
    count_brouillon = len(annonces)
    return render_template(
        "/back/gestionAnnonce.html",
        annonces=annonces,
        listcategories=listcategories,
        count_brouillon=count_brouillon,
    )


# ************************************Delete ***********************************
@app.route("/admin/Item/<int:id_annonce>/delete")
@admin_required
def un_deleteAnnonce(id_annonce):
    un_delete(id_annonce)
    return redirect(url_for("gestionAnnonce"))


# ************************************Publish ***********************************
@app.route("/admin/Item/<int:id_annonce>/publish")
@admin_required
def un_publishAnnonce(id_annonce):
    un_published(id_annonce)
    return redirect(url_for("gestionAnnonce"))


#
# =======================================================================================================================
# ============================= Gestion de la recherche dashboard ========================================================================
# =======================================================================================================================
#
# **********************Recherche Avancee ***********************************
@app.route("/recherche-annonceAvancee")
def recherche_annonAvancee():
    query = request.args.get("searchAvance")
    annonces = (
        Item.query.filter(
            Item.user_id == current_user.id, Item.title.ilike(f"%{query}%")
        )
        .order_by(desc(Item.date_pub))
        .all()
    )
    count = len(annonces)
    return render_template("/back/gestionAnnonce.html", annonces=annonces, count=count)


#
# =======================================================================================================================
# ============================= Gestion de la Authentification Simple===================================================================
# =======================================================================================================================
#

import secrets
from flask_mail import Message, Mail


# Ce sont des informations Test
app.config["MAIL_SERVER"] = "sandbox.smtp.mailtrap.io"
app.config["MAIL_PORT"] = 2525
app.config["MAIL_USERNAME"] = "966afbb985ad95"
app.config["MAIL_PASSWORD"] = "1bdae0667ba459"
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USE_SSL"] = False
app.config["MAIL_DEFAULT_SENDER"] = "gloireondongo1205@gmail.com"
mail = Mail(app)


def generate_confirmation_token():
    return secrets.token_urlsafe(30)


def send_confirmation_email(user):
    token = generate_confirmation_token()
    user.confirmation_token = token
    updateSession()

    confirmation_link = url_for("confirm_email", token=token, _external=True)
    msg = Message("Confirmation d'e-mail", recipients=[user.login])
    msg.body = "Cliquez sur le lien suivant pour confirmer votre adresse e-mail sur DyDyShop: {0}".format(
        confirmation_link
    )
    mail.send(msg)


@app.route("/confirm_email/<token>")
def confirm_email(token):
    user = User.query.filter_by(confirmation_token=token).first()

    if user:
        user.confirmed = True
        user.confirmation_token = None
        updateSession()
        flash("Votre adresse e-mail a été confirmée avec succès!", "success")
    else:
        flash("Le lien de confirmation n'est pas valide ou a expiré.", "danger")

    return redirect(url_for("login"))


@app.route("/compte/creation", methods=["POST", "GET"])
def creation_compte():
    if request.method == "POST":
        nom = request.form.get("nom")
        prenom = request.form.get("prenom")
        tel_recup = request.form.get("tel")
        login_recup = request.form.get("login")
        password = request.form.get("pass")
        password_confirmation = request.form.get("PassConfirmation")

        if password != password_confirmation:
            flash(
                "Les mots de passe ne correspondent pas. Veuillez réessayer.", "danger"
            )
            return redirect(url_for("creation_compte"))

        # Hasher le mot de passe dans la base de données
        hashed_password = hashlib.md5(password.encode("utf-8")).hexdigest()

        role = "admin" if login_recup == "eldy@gmail.com" else "user"

        nouvel_utilisateur = User(
            nom=nom,
            prenom=prenom,
            tel=tel_recup,
            login=login_recup,
            password=hashed_password,
            roles=role,
        )

        test_existance = User.query.filter_by(tel=tel_recup, login=login_recup).first()
        if test_existance:
            flash("Ce login ou tel déjà utilisé. Veuillez en choisir un autre.")
            return redirect(url_for("creation_compte"))
        else:
            saveUser(nouvel_utilisateur)
            # identity_changed.send(app, identity=Identity(nouvel_utilisateur.id, role))
            send_confirmation_email(nouvel_utilisateur)
            flash(
                "Votre compte a été créé avec succès!",
                "success",
            )

            flash(
                "Veuillez confirmer votre mail pour vous connecter.",
                "info",
            )
            return redirect(url_for("login"))

    return render_template("/back/creation_compte.html")


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        login = request.form["login"]
        password = request.form["pass"]
        tel = request.form["tel"]
        user = User.query.filter_by(login=login, tel=tel).first()

        if user and user.check_password(password):
            if user.confirmed:
                login_user(user)

                if "panier" in session:
                    transfer_session_cart_to_db_cart(user.id, session["panier"])
                    session.pop("panier")
                    session.pop("total")

                if "admin" in current_user.roles:
                    return redirect(url_for("admin_dashboard"))
                else:
                    return redirect(url_for("index"))
            else:
                flash(
                    "Votre adresse e-mail n'est pas confirmée. Veuillez vérifier votre boîte de réception.",
                    "info",
                )
                return render_template("/back/login.html")
        else:
            flash("Login ou mot de passe incorrect")
            return render_template("/back/login.html")
    else:
        return render_template("/back/login.html")


@app.route("/admin/dashboard")
@admin_required
def admin_dashboard():
    return render_template("/back/dashboard.html")


# Delogin
@app.route("/logout")
@login_required
def logout():
    logout_user()
    # identity_changed.send(app, identity=Identity(None))
    return redirect(url_for("index"))


def generate_reset_token():
    return secrets.token_urlsafe(30)


def send_reset_email(user):
    reset_token = generate_reset_token()
    user.reset_token = reset_token
    updateSession()

    reset_link = url_for("reset_password", token=reset_token, _external=True)
    msg = Message("Réinitialisation de mot de passe", recipients=[user.login])
    msg.body = f"Cliquez sur le lien suivant pour réinitialiser votre mot de passe : {reset_link}"
    mail.send(msg)


@app.route("/reset_password", methods=["POST"])
def reset_password_request():
    login = request.form.get("email")

    if login:
        user = User.query.filter_by(login=login).first()

        if user:
            send_reset_email(user)
            flash(
                "Un e-mail de réinitialisation a été envoyé à votre adresse.", "success"
            )
        else:
            flash("Aucun utilisateur trouvé avec cette adresse e-mail.", "danger")
    else:
        flash("Veuillez fournir une adresse e-mail.", "danger")

    return redirect(url_for("login"))


@app.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_password(token):
    user = User.query.filter_by(reset_token=token).first()

    if user:
        if request.method == "POST":
            new_password = request.form.get("new_password")
            # Mettez à jour le mot de passe dans la base de données et supprimez le token de réinitialisation
            user.password = hashlib.md5(new_password.encode("utf-8")).hexdigest()
            user.reset_token = None
            updateSession()

            flash("Votre mot de passe a été réinitialisé avec succès!", "success")
            return redirect(url_for("login"))
        return render_template("reset_password.html", token=token)
    else:
        flash("Le lien de réinitialisation n'est pas valide ou a expiré.", "danger")
        return redirect(url_for("mot_de_passe_oublie"))


""" def change_user_role(user, new_role):
    try:
        print(
            "==============Current User here ============================:",
            user.id,
            user.roles,
        )
        identity_changed.send(app, identity=Identity(user.id, new_role))
        print("==============identity ============================:", Identity)

    except IdentityChanged as e:
        # Gérer l'exception (par exemple, imprimer un avertissement ou journaliser l'erreur)
        print(f"Erreur lors du changement d'identité : {e}")

 """


#
# =======================================================================================================================
# ============================= Gestion Authentification Google ===================================================================
# =======================================================================================================================
#

""" oauth = OAuth(app)


google = oauth.remote_app(
    'google',
    consumer_key='YOUR_GOOGLE_CLIENT_ID',
    consumer_secret='YOUR_GOOGLE_CLIENT_SECRET',
    request_token_params={
        'scope': 'openid email profile',  # Spécifiez les autorisations nécessaires
    },
    base_url='https://www.googleapis.com/oauth2/v1/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://accounts.google.com/o/oauth2/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
)




@app.route('/google-login')
def google_login():
    return google.authorize(callback=url_for('authorized', _external=True))

@app.route('/google-logout')
def google_logout():
    session.pop('google_token', None)
    return redirect(url_for('index'))

@app.route('/google-login/authorized')
def google_authorized():
    response = google.authorized_response()
    if response is None or response.get('access_token') is None:
        return 'Accès refusé : raison={} erreur={}'.format(
            request.args['error_reason'],
            request.args['error_description']
        )

    session['google_token'] = (response['access_token'], '')
    user_info = google.get('userinfo')
    
    # Vérifiez si l'utilisateur existe déjà dans la base de données par login Google
    existing_user = User.query.filter_by(google_login=user_info.data['login']).first()

    if existing_user:
        # Mettez à jour les informations de l'utilisateur si nécessaire
        existing_user.google_id = user_info.data['id']
        existing_user.full_name = user_info.data['name']
        existing_user.profile_image = user_info.data['picture']
        db.session.commit()
    else:
        # Créez un nouvel utilisateur dans la base de données
        new_user = User(google_id=user_info.data['id'],
                        google_login=user_info.data['login'],
                        nom=user_info.data['name'])
                        #profile_image=user_info.data['picture'])
        SaveUser(new_user)



 """


# =======================================================================================================================
# ============================= Gestion du panier========================================================================
# =======================================================================================================================
#


@app.route("/add_panier/<int:id>")
def add_panier(id):
    if "panier" not in session:
        session["panier"] = []
        session["quantite"] = 0
        session["total"] = 0.0

    product = Item.query.get(id)
    if product:
        if id in session["panier"]:
            session["quantite"] += 1
        else:
            session["panier"].append(id)
            session["quantity"] += 1
        session["total"] += float(product.prix)

    return redirect(url_for("Panier"))


@app.route("/remove_from_cart/<int:id>")
def remove_from_cart(id):
    if "panier" in session:
        if id in session["panier"]:
            index = session["panier"].index(id)

            # Si la clé "quantite" existe et la quantité est supérieure à 0
            if (
                "quantity" in session
                and len(session["quantity"]) > index
                and session["quantity"][index] > 0
            ):
                # Décrémenter la quantité
                session["quantity"][index] -= 1

                # Si la quantité est égale à 0, supprimer le produit du panier
                if session["quantity"][index] == 0:
                    session["panier"].remove(id)
                    session["quantity"].pop(index)

            else:
                # Si la clé "quantite" n'existe pas, supprimer le produit du panier
                session["panier"].remove(id)

            # Mettre à jour le total
            product = Item.query.get(id)
            if product:
                session["total"] -= float(product.prix)

        return redirect(url_for("Panier"))
    return redirect(url_for("index"))


@app.route("/Panier")
def Panier():
    items_in_cart = []
    if "panier" in session:
        items_in_cart = [Item.query.get(item_id) for item_id in session["panier"]]

    print("=========Contenu de la session:=============", session)

    return render_template("/pages/panier.html", items_in_cart=items_in_cart)


#
# =======================================================================================================================
# ============================= Gestion des commandes ===================================================================
# =======================================================================================================================
#
@app.route("/checkout")
@login_required
def checkout():
    # Obtenez les détails des articles dans le panier à partir de votre base de données
    # cart_items = get_cart_items()

    # Créez un message de vérification en convertissant les détails du panier en texte

    # checkout_message = create_checkout_message(cart_items)
    checkout_message = (
        "Une commande de chaussure a été passé sur le site de DydyShop  prix:5000FCFA"
    )

    # Envoyez le message WhatsApp (utilisez vos propres informations Twilio)
    send_whatsapp_message(checkout_message)

    # Réinitialisez le panier après la commande
    # clear_cart()

    flash("Votre commande a été passée avec succès!", "success")
    return redirect(url_for("index"))


# Fonction pour obtenir les détails des articles dans le panier depuis la base de données
def get_cart_items():
    cart_items = CartItem.query.all()
    cart_item_details = []

    for cart_item in cart_items:
        item = Item.query.get(cart_item.annonce_id)
        if item:
            item_details = {
                "name": item.title,
                "price": item.prix,
                "quantity": cart_item.quantity,
            }
            cart_item_details.append(item_details)

    return cart_item_details


# Fonction pour créer un message de vérification en convertissant les détails du panier en texte
def create_checkout_message(cart_items):
    message = "Votre commande :\n"
    total_price = 0
    for item in cart_items:
        item_name = item["name"]
        item_price = item["price"]
        item_quantity = item["quantity"]
        total_price += item_price * item_quantity
        message += f"{item_name} x{item_quantity}: {item_price * item_quantity}€\n"
    message += f"Total : {total_price}€"
    return message


# account_sid = "ACda1a374fc048affd076363ebd0f1bb5d"
# auth_token = "008dda7a6424142308e6c538b44dcdea"


# Fonction pour envoyer un message WhatsApp (utilisez vos propres informations Twilio)
def send_whatsapp_message(message):
    account_sid = "AC133734595c6e3326b9cf8aae0dd5d1dd"
    auth_token = "d285e0f4a064345a8521d4d7f3518207"
    client = Client(account_sid, auth_token)

    message = client.messages.create(
        from_="whatsapp:+14155238886",
        body=message,
        to="whatsapp:+221771592145",
    )

    print(message.sid)


@app.route("/listes-commandes")
def orderListing():
    return render_template("/back/OrderListing.html")


#
# =======================================================================================================================
# ============================= Gestion Errors Handlers =================================================================
# =======================================================================================================================
#


@app.errorhandler(404)
def page404(error):
    return render_template("errors/404.html")


@app.errorhandler(403)
def forbidden(error):
    return render_template("errors/403.html"), 403


#
# =======================================================================================================================
# ============================= Gestion des favoris =====================================================================
# =======================================================================================================================
#


@app.route("/wishlist")
@login_required
def wishlist():
    user = User.query.get(current_user.id)
    annonces_favoris = user.favorites
    annonces_favoris_ids = [fav.annonce_id for fav in user.favorites]
    return render_template("/pages/favori.html", annonces_favoris=annonces_favoris)


class WishlistOperation(Enum):
    ADD = "ajouter"
    REMOVE = "retirer"


def manage_wishlist(item, operation):
    user = User.query.get(current_user.id)

    if item and operation == WishlistOperation.ADD and item not in user.favorites:
        favorite = Favorite(annonce_id=item.id, user_id=current_user.id)
        add_favori(favorite)
        flash("L'article a été ajouté à vos favoris avec succès", "success")
    elif item and operation == WishlistOperation.REMOVE:
        favorite = Favorite.query.filter_by(
            user_id=current_user.id, annonce_id=item.id
        ).first()
        if favorite:
            un_deleteFavorite(favorite)
            flash("L'article a été retiré de vos favoris avec succès", "success")
        else:
            flash("L'article n'est pas dans vos favoris", "error")
    else:
        flash("Opération non autorisée ou l'article n'existe pas en favori", "error")


@app.route("/add_wishlistBack/<int:id_annonce>", methods=["GET", "POST"])
@login_required
def add_wishlistBack(id_annonce):
    item = Item.query.get(id_annonce)
    manage_wishlist(item, operation=WishlistOperation.ADD)

    next_page = request.args.get("next")

    return redirect(next_page or url_for("wishlist"))


@app.route("/retirer_favoriBack/<int:id_annonce>", methods=["GET", "POST"])
@login_required
def remove_wishlistBack(id_annonce):
    item = Item.query.get(id_annonce)
    manage_wishlist(item, operation=WishlistOperation.REMOVE)

    next_page = request.args.get("next")

    return redirect(next_page or url_for("wishlist"))


import requests
import re

