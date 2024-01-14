from datetime import timedelta
from datetime import datetime
import dbm

from api.forms import CheckoutForm, LoginForm, MessageForm, ProfileForm
from .front import app
from sqlalchemy.orm import joinedload
from flask import (
    abort,
    jsonify,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
)
from flask_babel import Babel
from api.models.EnumColorAndSize import *
from api.models.EnumCategorie import *
from api.models.SousCategorie import *
from .front import app
from sqlalchemy import desc, func
from flask_login import login_required
from flask_paginate import Pagination, get_page_parameter


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
login_manager.login_message = "Veuillez vous connecter pour accéder à cette page "
from flask import g, request


from functools import wraps
from twilio.rest import Client
import os
import pathlib

import requests
from flask import Flask, session, abort, redirect, request
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from pip._vendor import cachecontrol
import google.auth.transport.requests


os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
app.secret_key = "WriteHereYourSecretKey"  # Change this to a secret key
# oauth = OAuth(app)

# =====================================================================
# =============================Import Model===========================
# =====================================================================

from api.models.model import (
    CartItem,
    Category,
    Item,
    Favorite,
    Notification,
    Order,
    OrderItem,
    SubCategory,
    Subscriber,
    add_favori,
    add_images_to_item,
    add_order,
    add_order_item,
    add_subscriber,
    ajouter_cart,
    clear_cart,
    create_item,
    delete_cart,
    get_annonce_by_id,
    getAllAnnonceBrouillon,
    getAllAnnonceDel,
    transfer_session_cart_to_db,
    un_delete,
    un_deleteFavorite,
    un_published,
    editAnnonceModel,
    User,
    saveUser,
    update_annonce_quantity,
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


maintenance_mode = False


@app.before_request
def check_for_maintenance():
    if maintenance_mode and request.endpoint not in ["maintenance"]:
        return redirect(url_for("maintenance"))
    # Si la requête est déjà pour la page "maintenance", ne pas rediriger.
    elif maintenance_mode and request.endpoint == "maintenance":
        return None
    else:
        return None


@app.route("/maintenance")
def maintenance():
    return render_template("/maintenance/maintenance.html")


# ===========================================================================
# ============================= Gestion Du Crud Dashboard ===================
# ===========================================================================
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
    img_form2 = request.form.get("img_url2")
    img_form3 = request.form.get("img_url3")
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
        img_url2=img_form2,
        img_url3=img_form3,
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
    current_date = datetime.utcnow()
    three_months_ago = current_date - timedelta(days=90)

    # Calculate the first day of the current month
    first_day_current_month = current_date.replace(day=1)

    # Calculate the first day of the three previous months
    first_day_three_months_ago = first_day_current_month - timedelta(days=90)

    # Calculate the last day of the three previous months
    last_day_three_months_ago = first_day_current_month - timedelta(days=1)

    # Format the month names in French
    month_names = [
        "Janvier",
        "Février",
        "Mars",
        "Avril",
        "Mai",
        "Juin",
        "Juillet",
        "Août",
        "Septembre",
        "Octobre",
        "Novembre",
        "Décembre",
    ]

    # Retrieve the number of users for the last three months
    users_last_three_months = User.query.filter(
        User.date_created >= three_months_ago
    ).count()

    # Retrieve the number of orders for the last three months
    orders_last_three_months = Order.query.filter(
        Order.date_created >= three_months_ago
    ).count()

    monthly_revenue_last_three_months = (
        Order.query.filter(Order.date_created >= three_months_ago)
        .with_entities(func.sum(Order.total_amount))
        .scalar()
        or 0
    )

    # Trending products
    trending_products = Item.query.order_by(desc(Item.nbre_vues)).limit(5).all()
    return render_template(
        "/back/dashboard.html",
        trending_products=trending_products,
        users_last_three_months=users_last_three_months,
        orders_last_three_months=orders_last_three_months,
        monthly_revenue_last_three_months=monthly_revenue_last_three_months,
        first_day_three_months_ago=first_day_three_months_ago.strftime("%B %Y"),
        last_day_three_months_ago=last_day_three_months_ago.strftime("%B %Y"),
        current_month=current_date.strftime("%B %Y"),
        month_names=month_names,
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
# app.config["MAIL_SERVER"] = "sandbox.smtp.mailtrap.io"
# app.config["MAIL_PORT"] = 2525
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 465
# app.config["MAIL_USERNAME"] = "966afbb985ad95"
# pp.config["MAIL_PASSWORD"] = "1bdae0667ba459"
app.config["MAIL_USERNAME"] = "gloireondongo1205@gmail.com"
app.config["MAIL_PASSWORD"] = "zsnocpmplstortpk"
app.config["MAIL_USE_TLS"] = False
app.config["MAIL_USE_SSL"] = True
# app.config["MAIL_DEFAULT_SENDER"] = "gloireondongo1205@gmail.com"
mail = Mail(app)


def generate_confirmation_token():
    return secrets.token_urlsafe(30)


def send_confirmation_email(user):
    sender = "noreply@gmail.com"
    token = generate_confirmation_token()
    user.confirmation_token = token
    updateSession()

    confirmation_link = url_for("confirm_email", token=token, _external=True)
    msg = Message("Confirmation d'e-mail", sender=sender, recipients=[user.login])
    msg_body = "Cliquez sur le lien suivant pour confirmer votre adresse e-mail sur DyDyShop: {0}".format(
        confirmation_link
    )

    msg.body = ""

    data = {"app_name": "DYDYSHOP", "body": msg_body}
    msg.html = render_template("email/confirmEmail.html", user_name=user.nom, data=data)
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

        hashed_password = hashlib.md5(password.encode("utf-8")).hexdigest()

        # Add another email to the condition
        role = (
            "admin"
            if login_recup in ["eldy@gmail.com", "gloireondongo1205@gmail.com"]
            else "user"
        )
        nouvel_utilisateur = User(
            nom=nom,
            prenom=prenom,
            tel=tel_recup,
            login=login_recup,
            password=hashed_password,
            roles=role,
        )

        test_existance_tel = User.query.filter_by(tel=tel_recup).first()
        if test_existance_tel:
            flash("Ce Numéro déjà utilisé. Veuillez en choisir un autre", "warning")
            return redirect(url_for("creation_compte"))
        test_existance_login = User.query.filter_by(login=login_recup).first()
        if test_existance_login:
            flash("Ce Login . Veuillez en choisir un autre", "warning")
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
    form = LoginForm()

    if form.validate_on_submit():
        login = form.login.data
        password = form.password.data
        tel = form.tel.data

        user = User.query.filter_by(login=login, tel=tel).first()

        if user and user.check_password(password):
            if user.confirmed:
                login_user(user)

                if "panier" in session:
                    transfer_session_cart_to_db(
                        user.id, session["panier"], session["quantite"]
                    )

                    destroy_session()

                if "admin" in current_user.roles:
                    return redirect(url_for("gestiondash"))
                else:
                    return redirect(url_for("index"))
            else:
                flash(
                    "Votre adresse e-mail n'est pas confirmée. Veuillez vérifier votre boîte de réception.",
                    "info",
                )
                return redirect(url_for("login"))

        flash("Login , mot de passe  ou numéro incorrect", "danger")
        return redirect(url_for("login"))

    return render_template("/back/login.html", form=form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    session.pop("google_token", None)
    # identity_changed.send(app, identity=Identity(None))
    return redirect(url_for("index"))


#
# =======================================================================================================================
# ============================= Gestion Authentification Google ===================================================================
# =======================================================================================================================
#


from flask_oauthlib.client import OAuth

GOOGLE_CLIENT_ID = (
    "6354560417-l78je9noot5ul7tpg8muk9gps9p1gded.apps.googleusercontent.com"
)

GOOGLE_CLIENT_SECRET = "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"
oauth = OAuth(app)


google = oauth.remote_app(
    "google",
    consumer_key=GOOGLE_CLIENT_ID,
    consumer_secret=GOOGLE_CLIENT_SECRET,
    request_token_params={
        "scope": "email profile"  # Spécifiez les autorisations nécessaires
    },
    base_url="https://www.googleapis.com/oauth2/v1/",
    request_token_url=None,
    access_token_method="POST",
    access_token_url="https://accounts.google.com/o/oauth2/token",
    authorize_url="https://accounts.google.com/o/oauth2/auth",
)


@google.tokengetter
def get_google_oauth_token():
    return session.get("google_token")


@app.route("/google-login")
def login_google():
    return google.authorize(callback=url_for("callback", _external=True))


@app.route("/callback")
def callback():
    response = google.authorized_response()
    if response is None or response.get("access_token") is None:
        return "Accès refusé : raison={} erreur={}".format(
            request.args["error_reason"], request.args["error_description"]
        )

    session["google_token"] = (response["access_token"], "")
    user_info = google.get("userinfo")

    print("iigigigig", user_info.data)
    email_retrieve = user_info.data["email"]

    print("gggggggg", user_info.data["email"])
    existing_user = User.query.filter_by(google_login=email_retrieve).first()

    if existing_user:
        existing_user.google_id = user_info.data["id"]
        existing_user.nom = user_info.data["name"]
        existing_user.prenom = user_info.data["given_name"]
        existing_user.profile_image = user_info.data["picture"]
        existing_user.roles = (
            "admin"
            if user_info.data["email"]
            in ["eldy@gmail.com", "gloireondongo1205@gmail.com"]
            else "user"
        )
        saveUser(existing_user)
        login_user(existing_user)

    else:
        new_user = User(
            nom=user_info.data["name"],
            prenom=user_info.data["given_name"],
            login=user_info.data["email"],
            google_id=user_info.data["id"],
            google_login=user_info.data["email"],
            profile_image=user_info.data["picture"],
            roles="admin"
            if user_info.data["email"]
            in ["eldy@gmail.com", "gloireondongo1205@gmail.com"]
            else "user",
        )
        saveUser(new_user)
        login_user(new_user)

    print("=========Contenu de la session:=============", session)
    return redirect(url_for("index"))


def generate_reset_token():
    return secrets.token_urlsafe(30)


def send_reset_email(user):
    reset_token = generate_reset_token()
    user.reset_token = reset_token
    updateSession()

    reset_link = url_for("reset_password", token=reset_token, _external=True)
    msg = Message("Réinitialisation de mot de passe", recipients=[user.login])

    msg.body = f"Cliquez sur le lien suivant pocur réinitialiser votre mot de passe : {reset_link}"
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


# =======================================================================================================================
# ============================= Gestion du panier========================================================================
# =======================================================================================================================
#


@app.route("/destroy_session")
def destroy_session():
    # Vérifiez d'abord si la session existe
    if session:
        # Utilisez la méthode clear() pour détruire la session
        session.clear()

    return "Session détruite avec succès!"


from flask_login import current_user


@app.route("/add_panier/<int:id>")
def add_panier(id):
    if current_user.is_authenticated:
        # Utilisateur connecté, utilisez le panier en base de données
        user_id = current_user.id
        user_cart = CartItem.query.filter_by(user_id=user_id, annonce_id=id).first()

        if user_cart:
            user_cart.quantity += 1
        else:
            user_cart = CartItem(user_id=user_id, annonce_id=id, quantity=1)
            ajouter_cart(user_cart)
        updateSession()
    else:
        # Utilisateur non connecté, utilisez le panier en session
        if "panier" not in session:
            session["panier"] = []
            session["quantite"] = []
            session["total"] = 0.0

        product = Item.query.get(id)
        if product:
            if id in session["panier"]:
                index = session["panier"].index(id)
                session["quantite"][index] += 1
            else:
                session["panier"].append(id)
                session["quantite"].append(1)

            session["total"] += float(product.prix)

    return redirect(url_for("Panier"))


@app.route("/remove_from_cart/<int:id>")
def remove_from_cart(id):
    if current_user.is_authenticated:
        # Utilisateur connecté, utilisez le panier en base de données
        user_id = current_user.id
        user_cart = CartItem.query.filter_by(user_id=user_id, annonce_id=id).first()

        if user_cart:
            user_cart.quantity -= 1
            if user_cart.quantity <= 0:
                delete_cart(user_cart)
        updateSession()
    else:
        # Utilisateur non connecté, utilisez le panier en session
        if "panier" in session:
            if id in session["panier"]:
                index = session["panier"].index(id)
                session["quantite"][index] -= 1

                product = Item.query.get(id)
                if product:
                    session["total"] -= float(product.prix)

                if session["quantite"][index] <= 0:
                    session["panier"].pop(index)
                    session["quantite"].pop(index)

    return redirect(url_for("Panier"))


@app.route("/Panier")
def Panier():
    if current_user.is_authenticated:
        # Utilisateur connecté, récupérez le panier depuis la base de données
        user_id = current_user.id

        user_cart_items = CartItem.query.filter_by(user_id=user_id).all()
        items_in_cart = [
            cart_item.item
            for cart_item in user_cart_items
            if cart_item.item is not None
        ]

        total_quantity = sum(
            cart_item.quantity
            for cart_item in user_cart_items
            if cart_item.quantity is not None
        )
        total_amount = sum(
            cart_item.item.prix * cart_item.quantity
            for cart_item in user_cart_items
            if cart_item.item is not None and cart_item.quantity is not None
        )

    else:
        # Utilisateur non connecté, récupérez le panier depuis la session
        items_in_cart, total_quantity = get_items_in_cart()
        total_amount = session.get("total", 0.0)

    return render_template(
        "/pages/panier.html",
        items_in_cart=items_in_cart,
        total_quantity=total_quantity,
        total_amount=total_amount,
    )


def get_items_in_cart():
    items_in_cart = []
    total_quantity = 0

    if "panier" in session:
        for index in range(len(session["panier"])):
            item_id = session["panier"][index]
            quantity = session["quantite"][index]
            product = Item.query.get(item_id)

            if product and quantity > 0:
                items_in_cart.append(product)
                total_quantity += quantity

    return items_in_cart, total_quantity


#
# =======================================================================================================================
# ============================= Gestion des commandes ===================================================================
# =======================================================================================================================
#


@app.route("/checkout", methods=["GET", "POST"])
@login_required
def checkout():
    form = CheckoutForm()
    if current_user.is_authenticated:
        # Utilisateur connecté, récupérez le panier depuis la base de données
        user_id = current_user.id

        user_cart_items = CartItem.query.filter_by(user_id=user_id).all()
        items_in_cart = [
            cart_item.item
            for cart_item in user_cart_items
            if cart_item.item is not None
        ]

        total_amount = sum(
            cart_item.item.prix * cart_item.quantity
            for cart_item in user_cart_items
            if cart_item.item is not None and cart_item.quantity is not None
        )

    if form.validate_on_submit():
        delivery_address = form.delivery_address.data
        phone_number = form.phone_number.data
        email = form.email.data
        country = form.country.data

        order_id = create_order(
            current_user.id,
            items_in_cart,
            delivery_address,
            phone_number,
            email,
            country,
            total_amount,
        )

        checkout_message = create_checkout_message(
            items_in_cart,
            total_amount,
            delivery_address,
            phone_number,
            email,
            country,
        )
        send_whatsapp_message(checkout_message)

        # clear_cart()

        flash("Votre commande a été passée avec succès!", "success")
        return redirect(url_for("index"))

    return render_template(
        "/pages/checkout.html",
        items_in_cart=items_in_cart,
        total_amount=total_amount,
        form=form,
    )


def create_order(
    user_id, items_in_cart, delivery_address, phone_number, email, country, total_amount
):
    # Create an order
    order = Order(
        user_id=user_id,
        total_amount=total_amount,
        delivery_address=delivery_address,
        phone_number=phone_number,
        email=email,
        country=country,
    )
    add_order(order)
    updateSession()

    # Create order items
    for item in items_in_cart:
        order_item = OrderItem(
            order_id=order.id,
            annonce_id=item.id,
            quantity=item.quantity,
        )
        add_order_item(order_item)
        annonce = get_annonce_by_id(item.id)
        if annonce:
            annonce.quantity -= item.quantity
            update_annonce_quantity(annonce)

    updateSession()

    return order.id


def create_checkout_message(
    items_in_cart,
    total_amount,
    delivery_address,
    phone_number,
    email,
    country,
):
    message = "Votre commande :\n"
    for item in items_in_cart:
        item_name = item.title
        item_price = item.prix
        item_quantity = item.quantity
        message += f"{item_name} x{item_quantity}: {item_price * item_quantity}€\n"

    message += f"Total : {total_amount} CFA\n"
    message += f"Adresse de livraison : {delivery_address}\n"
    message += f"Numéro de téléphone : {phone_number}\n"
    message += f"Email : {email}\n"
    message += f"Pays : {country}"

    return message


from decouple import config


@app.context_processor
def inject_message_form():
    return {"messageForm": MessageForm()}


@app.route("/send-message", methods=["POST"])
def handle_form():
    messageForm = MessageForm()
    if messageForm.validate_on_submit():
        message = (
            f"Votre commande: {messageForm.article.data}\n"
            f"Votre message: {messageForm.message.data}"
        )
        send_whatsapp_message(message)
        flash("Message envoyé avec succès!", "success")
        return redirect(url_for("index"))
    else:
        return redirect(url_for("index"))


def send_whatsapp_message(message_receveid):
    TWILIO_ACCOUNT_SID = "AC133734595c6e3326b9cf8aae0dd5d1dd"
    TWILIO_AUTH_TOKEN = "d285e0f4a064345a8521d4d7f3518207"

    """ TWILIO_ACCOUNT_SID = "ACda1a374fc048affd076363ebd0f1bb5d"
    TWILIO_AUTH_TOKEN = "7659957c485181ae33f15d3825f68d80" """
    # account_sid = "ACda1a374fc048affd076363ebd0f1bb5d"
    # auth_token = "008dda7a6424142308e6c538b44dcdea"
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    message = client.messages.create(
        # +14155238886
        from_="whatsapp:+14155238886",
        body=message_receveid,
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
    annonces_favoris = user.favorites.all()
    annonces_favoris_ids = [fav.annonce_id for fav in annonces_favoris]

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


#
# =======================================================================================================================
# ============================= Gestion des contacts =====================================================================
# =======================================================================================================================
#


@app.route("/newsletter", methods=["POST"])
@login_required
def newsletter():
    if request.method == "POST":
        email = request.form["email"]
        user_id = current_user.id

        if not email:
            flash("Veuillez fournir une adresse e-mail.", "danger")
            return jsonify(
                {"status": "error", "message": "Veuillez fournir une adresse e-mail."}
            )
        if Subscriber.query.filter_by(email=email).first():
            message = f"L'adresse e-mail {email} est déjà abonnée."
            flash(message, "info")
            return redirect(url_for("index"))

        subscriber = Subscriber(email=email)
        add_subscriber(subscriber, user_id)
        updateSession()

        send_newsletter(email)

        flash(f"La newsletter a été envoyée à {email} avec succès!", "success")

    return redirect(url_for("index"))


def send_newsletter(email):
    subject = "Bienvenue à notre newsletter !"
    body = "Merci de vous être abonné à notre newsletter. Vous serez informer les dernières actualités et mises à jour."
    sender = "noreply@gmail.com"

    msg = Message(subject, sender=sender, recipients=[email])
    msg_body = body

    msg.body = ""

    data = {"app_name": "DYDYSHOP", "body": msg_body}
    msg.html = render_template("email/confirmEmail.html", user_name=email, data=data)
    try:
        mail.send(msg)
        print(f"Newsletter envoyée avec succès à {email}")
    except Exception as e:
        print(f"Erreur lors de l'envoi de la newsletter à {email}: {str(e)}")


@app.route("/Contact")
def Contact():
    return render_template("/pages/contact.html")


def send_contact(email):
    subject = "Bienvenue à notre newsletter !"
    body = "Merci de vous être abonné à notre newsletter. Vous serez informer les dernières actualités et mises à jour."
    sender = "noreply@gmail.com"

    msg = Message(subject, sender=sender, recipients=[email])
    msg_body = body

    msg.body = ""

    data = {"app_name": "DYDYSHOP", "body": msg_body}
    msg.html = render_template("email/confirmEmail.html", user_name=email, data=data)
    try:
        mail.send(msg)
        print(f"vous avez contacté avec succès dydyshop {email}")
    except Exception as e:
        print(f"Erreur lors de l'envoi de contact à {email}: {str(e)}")


def getUser(user_id):
    """
    Get user information by user ID.

    Parameters:
        user_id (int): The ID of the user.

    Returns:
        User: User object if found, None otherwise.
    """
    user = User.query.get(user_id)
    return user


@app.route("/Profile", methods=["GET", "POST"])
@login_required
def Profile():
    form = ProfileForm()
    if form.validate_on_submit():
        current_user.nom = form.nom.data
        current_user.prenom = form.prenom.data
        current_user.tel = form.tel.data
        current_user.pays = form.pays.data
        current_user.adresse = form.adresse.data
        updateSession()
        flash("Votre profil a été mis à jour avec succès!", "success")
        return redirect(url_for("Profile"))
    elif request.method == "GET":
        form.nom.data = current_user.nom
        form.prenom.data = current_user.prenom
        form.tel.data = current_user.tel
        form.pays.data = current_user.pays
        form.adresse.data = current_user.adresse
    return render_template("/pages/profile.html", form=form, user=current_user)

@app.route("/Order")
@login_required
def OrderPage():
    page = request.args.get(get_page_parameter(), type=int, default=1)
    NbreElementParPage = 2
    offset = (page - 1) * NbreElementParPage
    orders = ["HH", "II"]
    pagination = Pagination(page=page, per_page=NbreElementParPage, total=len(orders))
    return render_template(
        "/pages/order.html",
        user=current_user,
        pagination=pagination,
    )


@app.route("/mark_notification_read/<int:notification_id>")
@login_required
@admin_required
def mark_notification_read(notification_id):
    notification = Notification.query.get(notification_id)
    if notification and notification.user == current_user:
        notification.read = True
        updateSession()
    return redirect(url_for("dashboard"))


import requests
import re
