import hashlib
from flask_sqlalchemy import SQLAlchemy
from api.front import app
import datetime
import logging as log
from datetime import datetime
from sqlalchemy import desc, func
from flask_login import UserMixin, current_user

from typing import List
from werkzeug.datastructures import FileStorage
from application.models.EnumColorAndSize import EnumSize
from api.models.EnumColorAndSize import EnumSize
from flask_uploads import UploadSet, configure_uploads, IMAGES, UploadNotAllowed


from api.models.EnumColorAndSize import EnumColor, EnumSize


db = SQLAlchemy(app)
photos = UploadSet("photos", IMAGES)
app.config["UPLOADED_PHOTOS_DEST"] = "uploads"
configure_uploads(app, photos)


class Subscriber(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)


class Favorite(db.Model):
    __tablename__ = "favorites"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    annonce_id = db.Column(db.Integer, db.ForeignKey("items.id"))


class Image(db.Model):
    __tablename__ = "images"
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey("items.id"), nullable=False)


class Category(db.Model):
    __tablename__ = "categories"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    subcategories = db.relationship("SubCategory", backref="category")


class SubCategory(db.Model):
    __tablename__ = "sub_categories"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"))


class Item(db.Model):
    __tablename__ = "items"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    prix = db.Column(db.Float, nullable=True)
    img_url = db.Column(db.String(255), nullable=True)
    img_title = db.Column(db.String(100), nullable=True)
    date_pub = db.Column(db.DateTime, default=datetime.utcnow)
    published = db.Column(db.Boolean, default=True)
    deleted = db.Column(db.Boolean, default=False)
    nbre_vues = db.Column(db.Integer, default=0)
    favorites = db.relationship("Favorite", backref="item", lazy="dynamic")
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    quantity = db.Column(db.Integer, default=0)
    images = db.relationship("Image", backref="item", lazy=True)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"))
    subcategory_id = db.Column(db.Integer, db.ForeignKey("sub_categories.id"))
    color1 = db.Column(db.String(100), nullable=True)
    color2 = db.Column(db.String(100), nullable=True)
    color3 = db.Column(db.String(100), nullable=True)
    size1 = db.Column(db.String(100), nullable=True)
    size2 = db.Column(db.String(100), nullable=True)
    size3 = db.Column(db.String(100), nullable=True)


class User(db.Model, UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(200), nullable=False)
    prenom = db.Column(db.String(200), nullable=False)
    tel = db.Column(db.String(200), nullable=False)
    login = db.Column(db.String(200), nullable=False)
    password = db.Column(db.String(5000), nullable=False)
    google_id = db.Column(db.String(200), unique=True)
    google_login = db.Column(db.String(200), unique=True)
    active = db.Column(db.Boolean, default=True)
    NbreAnnoncePub = db.Column(db.Integer, default=0)
    favorites = db.relationship("Favorite", backref="user", lazy="dynamic")
    items = db.relationship("Item", backref="user", lazy=True)
    roles = db.Column(db.String(50))
    confirmation_token = db.Column(db.String, unique=True)
    confirmed = db.Column(db.Boolean, default=False)
    # reset_token = db.Column(db.String(200), unique=True)

    def __repr__(self):
        return f"<User: {self.login}>"

    def check_password(self, password):
        return hashlib.md5(password.encode("utf-8")).hexdigest() == self.password

    def is_admin(self):
        return "admin" in self.roles


class CartItem(db.Model):
    __tablename__ = "cart_items"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    annonce_id = db.Column(db.Integer, db.ForeignKey("items.id"), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    item = db.relationship("Item")


class Order(db.Model):
    __tablename__ = "orders"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    items = db.relationship("OrderItem", backref="order", lazy=True)


class OrderItem(db.Model):
    __tablename__ = "order_items"
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"), nullable=False)
    annonce_id = db.Column(db.Integer, db.ForeignKey("items.id"), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    item = db.relationship("Item")


def getAllAnnonce():
    return Item.query.all()


def getAllAnnonceRecent():
    return Item.query.order_by(desc(Item.date_pub)).limit(5).all()


def getAllAnnonceA_La_Une():
    return Item.query.order_by(desc(Item.nbre_vues)).limit(5).all()


def getAllAnnoncePublier():
    return (
        Item.query.filter(Item.published == True, Item.deleted == False)
        .order_by(desc(Item.date_pub))
        .all()
    )


def getAllAnnonceDel():
    return (
        Item.query.filter(Item.deleted == True, Item.user_id == current_user.id)
        .order_by(desc(Item.date_pub))
        .all()
    )


def getAllAnnonceBrouillon():
    return (
        Item.query.filter(
            Item.published == False,
            Item.deleted == False,
            Item.user_id == current_user.id,
        )
        .order_by(desc(Item.date_pub))
        .all()
    )


def findAnnonceById(id_annonce):
    item = Item.query.get(id_annonce)
    if item is not None:
        item.nbre_vues += 1
        db.session.commit()
    return item



def create_item(new_item: Item):
    db.session.add(new_item)
    db.session.commit()
    



def editAnnonceModel(Item: Item):
    old_annonce = Item.query.get(Item.id)
    #
    old_annonce.title = Item.title
    old_annonce.description = Item.description
    old_annonce.published = Item.published
    old_annonce.img_title = Item.img_title
    old_annonce.img_url = Item.img_url
    old_annonce.prix = Item.prix
    old_annonce.categorie = Item.categorie
    old_annonce.lieuPub = Item.lieuPub
    old_annonce.etat = Item.etat
    db.session.commit()


def un_published(id_annonce):
    Item = Item.query.get(id_annonce)

    # Tester si c'est une publication:
    if not Item.published:
        Item.datePub = datetime.datetime.utcnow()

    Item.published = not Item.published
    db.session.commit()


def un_delete(id_annonce):
    Item = Item.query.get(id_annonce)

    Item.deleted = not Item.deleted
    db.session.commit()


def un_deleteFavorite(favorite: Favorite):
    db.session.delete(favorite)
    db.session.commit()


def add_favori(favorite):
    db.session.add(favorite)
    db.session.commit()


# ========---------Mettre Au panier
def transfer_session_cart_to_db_cart(user_id, session_cart):
    user_cart = CartItem.query.filter_by(user_id=user_id).first()

    # Si le panier de l'utilisateur n'existe pas, créez-en un nouveau
    if not user_cart:
        user_cart = CartItem(user_id=user_id)
        db.session.add(user_cart)
        db.session.commit()

    for product_id in session_cart:
        if product_id is not None:
            cart_item = CartItem.query.filter_by(
                annonce_id=product_id, user_id=user_id
            ).first()

        # Si le produit est déjà dans le panier de l'utilisateur, augmentez la quantité
        if cart_item:
            cart_item.quantity += 1
        else:
            # Sinon, ajoutez le produit au panier de l'utilisateur avec une quantité de 1
            cart_item = CartItem(user_id=user_id, annonce_id=product_id, quantity=1)
            db.session.add(cart_item)

    db.session.commit()


def clear_cart():
    CartItem.query.delete()
    db.session.commit()


# ************************************ USER REQUETES ***********************************


def saveUser(user: User):
    db.session.add(user)
    db.session.commit()


def ajouter_favori(favorite: Favorite):
    db.session.add(favorite)
    db.session.commit()


def updateSession():
    db.session.commit()


def updatecategory(category: Category):
    db.session.add(category)
    db.session.commit()


def updatesubcategory(subcategory: SubCategory):
    db.session.add(subcategory)
    db.session.commit()


# =====================================================================
# ============Création de commande(Excution au lancement)==============
# ========================decorators init==============================
@app.cli.command("EldyDb")
def init_db():
    with app.app_context():
        db.drop_all()
        db.create_all()

        log.warning("Base de donnees actualisee")
