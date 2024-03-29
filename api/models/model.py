import hashlib
from flask_sqlalchemy import SQLAlchemy
from api.front import app
import datetime
import logging as log
from datetime import datetime
from sqlalchemy import desc, func
from flask_login import UserMixin, current_user
from api.models.EnumColorAndSize import EnumSize
from flask_uploads import UploadSet, configure_uploads, IMAGES, UploadNotAllowed


from typing import List
from werkzeug.datastructures import FileStorage
from api.models.EnumColorAndSize import EnumSize
from api.models.EnumColorAndSize import EnumSize
from flask_uploads import UploadSet, configure_uploads, IMAGES, UploadNotAllowed


from api.models.EnumColorAndSize import EnumColor, EnumSize


db = SQLAlchemy(app)
photos = UploadSet("photos", IMAGES)
app.config["UPLOADED_PHOTOS_DEST"] = "uploads"
configure_uploads(app, photos)


class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    message = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    read = db.Column(db.Boolean, default=False)


class Subscriber(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)


class Favorite(db.Model):
    __tablename__ = "favorites"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    annonce_id = db.Column(db.Integer, db.ForeignKey("items.id"))
    date_created = db.Column(db.DateTime, default=datetime.utcnow)


class Image(db.Model):
    __tablename__ = "images"
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey("items.id"), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)


class Category(db.Model):
    __tablename__ = "categories"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    subcategories = db.relationship("SubCategory", backref="category")
    date_created = db.Column(db.DateTime, default=datetime.utcnow)


class Review(db.Model):
    __tablename__ = "reviews"
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey("items.id"), nullable=False)


class SubCategory(db.Model):
    __tablename__ = "sub_categories"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"))
    date_created = db.Column(db.DateTime, default=datetime.utcnow)


class Item(db.Model):
    __tablename__ = "items"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    prix = db.Column(db.Float, nullable=True)
    img_url = db.Column(db.String(255), nullable=True)
    img_url2 = db.Column(db.String(255), nullable=True)
    img_url3 = db.Column(db.String(255), nullable=True)
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
    reviews = db.relationship("Review", backref="item", lazy="dynamic")
    color1 = db.Column(db.String(100), nullable=True)
    color2 = db.Column(db.String(100), nullable=True)
    color3 = db.Column(db.String(100), nullable=True)
    size1 = db.Column(db.String(100), nullable=True)
    size2 = db.Column(db.String(100), nullable=True)
    size3 = db.Column(db.String(100), nullable=True)

    @property
    def quantity_in_cart(self):
        cart_item = CartItem.query.filter_by(annonce_id=self.id).first()
        return cart_item.quantity if cart_item else 0

    @property
    def average_rating(self):
        """
        Récupère la moyenne des ratings pour l'article.
        """
        return (
            db.session.query(func.avg(Review.rating))
            .filter_by(item_id=self.id)
            .scalar()
            or 0.0
        )

    @property
    def ratings_count(self):
        """
        Récupère le nombre total de ratings pour l'article.
        """
        return Review.query.filter_by(item_id=self.id).count()


class User(db.Model, UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(200), nullable=False)
    pays = db.Column(db.String(200), nullable=True)
    adresse = db.Column(db.String(200), nullable=True)
    prenom = db.Column(db.String(200))
    tel = db.Column(db.String(200))
    login = db.Column(db.String(200), nullable=False)
    password = db.Column(db.String(5000))
    google_id = db.Column(db.String(200), unique=True)
    google_login = db.Column(db.String(200), unique=True)
    profile_image = db.Column(db.String(200))
    active = db.Column(db.Boolean, default=True)
    NbreAnnoncePub = db.Column(db.Integer, default=0)
    favorites = db.relationship("Favorite", backref="user", lazy="dynamic")
    items = db.relationship("Item", backref="user", lazy=True)
    roles = db.Column(db.String(50))
    confirmation_token = db.Column(db.String, unique=True)
    confirmed = db.Column(db.Boolean, default=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    notifications = db.relationship("Notification", backref="user", lazy="dynamic")
    subscriptions = db.relationship("Subscriber", backref="user", lazy="dynamic")

    def is_subscriber(self):
        """
        Check if the user is a subscriber.

        Returns:
            bool: True if the user is a subscriber, False otherwise.
        """
        return self.subscriptions.count() > 0

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
    annonce_id = db.Column(db.Integer, db.ForeignKey("items.id"))
    quantity = db.Column(db.Integer)
    item = db.relationship("Item")
    date_created = db.Column(db.DateTime, default=datetime.utcnow)


class Order(db.Model):
    __tablename__ = "orders"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    items = db.relationship("OrderItem", backref="order", lazy=True)
    delivery_address = (db.Column(db.String(200)),)
    phone_number = (db.Column(db.String(200)),)
    email = (db.Column(db.String(200)),)
    status = (db.Column(db.String(200)),)
    country = (db.Column(db.String(200)),)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)


class OrderItem(db.Model):
    __tablename__ = "order_items"
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"), nullable=False)
    annonce_id = db.Column(db.Integer, db.ForeignKey("items.id"), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    item = db.relationship("Item")
    date_created = db.Column(db.DateTime, default=datetime.utcnow)


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


def get_annonce_by_id(annonce_id):
    return Item.query.get(annonce_id)


def update_annonce_quantity(annonce: Item):
    db.session.commit()


def findAnnonceById(id_annonce):
    item = Item.query.get(id_annonce)
    if item is not None:
        item.nbre_vues += 1
        db.session.commit()
    return item


""" def getBestSellingItems():
    best_selling_items = (
        db.session.query(Item, func.sum(OrderItem.quantity).label("total_sold"))
        .join(OrderItem, Item.id == OrderItem.annonce_id)
        .group_by(Item.id)
        .order_by(desc("total_sold"))
        .limit(3)
        .all()
    )

    return best_selling_items """


def create_item(new_item: Item):
    db.session.add(new_item)
    db.session.commit()


def create_item(new_item: Item):
    db.session.add(new_item)
    db.session.commit()


def add_images_to_item(item, image_files):
    for image_file in image_files:
        # Sauvegardez le fichier dans le dossier défini par Flask-Uploads
        filename = photos.save(image_file)
        new_image = Image(filename=filename, item_id=item.id)
        db.session.add(new_image)
    db.session.commit()


def editAnnonceModel(Item: Item):
    old_annonce = Item.query.get(Item.id)
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
def transfer_session_cart_to_db(user_id, session_carts, session_quantities):
    user_cart = CartItem.query.filter_by(user_id=user_id).first()

    print("icccccciii", user_cart)
    print("===================", session_carts)
    print("===================", session_quantities)
    if user_cart is None:
        user_cart = CartItem(user_id=user_id)
        db.session.add(user_cart)

    for index in range(len(session_carts)):
        product_id = session_carts[index]
        quantity = session_quantities[index]

        cart_item = CartItem(user_id=user_id, annonce_id=product_id, quantity=quantity)
        db.session.add(cart_item)

    db.session.commit()


def clear_cart(user_id):
    CartItem.query.filter_by(user_id=user_id).delete()
    db.session.commit()


def saveUser(user: User):
    db.session.add(user)
    db.session.commit()


def ajouter_cart(user_cart: CartItem):
    db.session.add(user_cart)


def delete_cart(user_cart: CartItem):
    db.session.delete(user_cart)


def ajouter_favori(favorite: Favorite):
    db.session.add(favorite)
    db.session.commit()


def add_order(order: Order):
    db.session.add(order)


def add_order_item(order_item: OrderItem):
    db.session.add(order_item)


def updateSession():
    db.session.commit()


def updatecategory(category: Category):
    db.session.add(category)
    db.session.commit()


def updatesubcategory(subcategory: SubCategory):
    db.session.add(subcategory)
    db.session.commit()


def add_notification(user, message):
    notification = Notification(user=user, message=message)
    db.session.add(notification)
    db.session.commit()


def add_subscriber(subscriber: Subscriber, user_id):
    subscriber.user_id = user_id
    db.session.add(subscriber)


# =====================================================================
# ============Création de commande(Excution au lancement)==============
# ========================decorators init==============================
@app.cli.command("EldyDb")
def init_db():
    with app.app_context():
        db.drop_all()
        db.create_all()

        log.warning("Base de donnees actualisee")
