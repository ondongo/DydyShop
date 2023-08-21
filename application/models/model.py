import hashlib
from flask_sqlalchemy import SQLAlchemy
from application.front import app
import datetime
import logging as log 

from sqlalchemy import desc
from flask_login import UserMixin, current_user

from application.models.EnumColorAndSize import EnumColor, EnumSize

db = SQLAlchemy(app)



class Favorite(db.Model):
    __tablename__ = "favorites"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    annonce_id = db.Column(db.Integer, db.ForeignKey('items.id'))

class Size(db.Model):
    __tablename__ = "sizes"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Enum(EnumSize), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'))

class Color(db.Model):
    __tablename__ = "colors"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Enum(EnumColor), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'))


class Category(db.Model):
    __tablename__ = "categories"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    #item_id = db.Column(db.Integer, db.ForeignKey('items.id'))
    
    
    
class Item(db.Model):
    __tablename__ = "items"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    prix = db.Column(db.Float, nullable=True)
    categorie = db.Column(db.String(200))
    sousCategorie = db.Column(db.String(200))
    img_url = db.Column(db.String(255), nullable=True)
    img_title = db.Column(db.String(100), nullable=True)
    datePub = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    published = db.Column(db.Boolean, default=True)
    deleted = db.Column(db.Boolean, default=False)
    nbreVues = db.Column(db.Integer, default=0)
    favorites = db.relationship('Favorite', backref='item', lazy='dynamic')
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    sizes = db.relationship('Size', backref='item')
    colors = db.relationship('Color', backref='item')

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(200), nullable=False)
    prenom = db.Column(db.String(200), nullable=False)
    tel = db.Column(db.String(200), nullable=False)
    login = db.Column(db.String(200), nullable=False)
    password = db.Column(db.String(5000), nullable=False)
    active = db.Column(db.Boolean, default=True)
    NbreAnnoncePub = db.Column(db.Integer, default=0)
    favorites = db.relationship('Favorite', backref='user', lazy='dynamic')
    items = db.relationship('Item', backref='user', lazy=True)

    def __repr__(self):
        return f"<User: {self.login}>"

    def check_password(self, password):
        return hashlib.md5(password.encode('utf-8')).hexdigest() == self.password

class CartItem(db.Model):
    __tablename__ = "cart_items"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    annonce_id = db.Column(db.Integer, db.ForeignKey('items.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    item = db.relationship('Item')

class Order(db.Model):
    __tablename__ = "orders"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    items = db.relationship('OrderItem', backref='order', lazy=True)

class OrderItem(db.Model):
    __tablename__ = "order_items"
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    annonce_id = db.Column(db.Integer, db.ForeignKey('items.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    item = db.relationship('Item')


# =====================================================================
# =============================Fin Classe ==============
# =====================================================================




# =====================================================================
# =============================Requetes complexes dans back.py et front.py ==============
# =====================================================================







# ****************************************************************************
# =*****************************Debut Requetes Query Simples***********************************
# **********************************************************************


#************************************Annonces ***********************************
# ========-----Afficher tous les articles
def getAllAnnonce():
    return Item.query.all()

def getAllAnnonceRecent():
    return Item.query.order_by(desc(Item.datePub)).all()

#========-------Publish
#Visit
def getAllAnnoncePublier():
    return (
        Item.query.filter(Item.published == 1, Item.deleted == 0)
        .order_by(desc(Item.datePub))
        .all()
    )




#=====-----RequeteCorbeille
def getAllAnnonceDel():
    return  (
        Item.query.filter(Item.deleted == 1,Item.user_id==current_user.id)
        .order_by(desc(Item.datePub))
        .all()
    )


#========== Non---------Publish
def getAllAnnonceBrouillon():
    return (
        
        Item.query.filter(Item.published == 0, Item.deleted == 0,Item.user_id==current_user.id)
        .order_by(desc(Item.datePub))
        .all()
    )


#=======-------------Afficher l'article qui a cet id
def findAnnonceById(id_annonce):
    item = Item.query.get(id_annonce)
    if Item is not None:
        Item.nbreVues += 1
        db.session.commit()
    return item

# def solution(id_annonce):
#     return Item.query.get(id_annonce)


def getAllAnnonceA_La_Une():
    return (
            Item.query.order_by(desc(Item.nbreVues)).limit(5).all()
        )



#============Save objet de type article====================
def saveAnnonce(Item: Item):
    db.session.add(Item)
    db.session.commit()
    


#==============================---------Modifier Item

def editAnnonceModel(Item:Item):
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

#==========---------Faire passer à publier

def un_published(id_annonce):
    Item = Item.query.get(id_annonce)

    # Tester si c'est une publication:
    if not Item.published:
        Item.datePub = datetime.datetime.utcnow()

    Item.published = not Item.published
    db.session.commit()



#=======---------Mettre à la Corbeille=======CoteModel
def un_delete(id_annonce):
    Item = Item.query.get(id_annonce)

    Item.deleted = not Item.deleted
    db.session.commit()
    
    
def un_deleteFavorite(favorite:Favorite):
    db.session.delete(favorite)
    db.session.commit()


#========---------Mettre Favori
# def ajouter_favori(user_id, annonce_id):
#     favori = Favorite(user_id=user_id, annonce_id=annonce_id)
#     db.session.add(favori)
#     db.session.commit()



#========---------Mettre Au panier
def transfer_session_cart_to_db_cart(user_id, session_cart):
    user_cart = CartItem.query.filter_by(user_id=user_id).first()
    if not user_cart:
        user_cart = CartItem(user_id=user_id)
        db.session.add(user_cart)
        db.session.commit()

    for product_id in session_cart:
        cart_item = CartItem.query.filter_by(cart=user_cart, annonce_id=product_id).first()
        if cart_item:
            cart_item.quantity += 1
        else:
            cart_item = CartItem(cart=user_cart, annonce_id=product_id, quantity=1 )
            db.session.add(cart_item)

    db.session.commit()


#************************************ USER REQUETES ***********************************

def saveUser(user: User):
    db.session.add(user)
    db.session.commit()


def ajouter_favori(favorite: Favorite):
    db.session.add(favorite)
    db.session.commit()


# =====================================================================
# ============Création de commande(Excution au lancement)==============
# ========================decorators init==============================
@app.cli.command('EldyDb')
def init_db():
    with app.app_context():
        db.drop_all()
        db.create_all()
        
        log.warning("Base de donnees actualisee")

# ==================Test---------------

#01 ========== insert 
@app.cli.command('insert-user')
def insert_user():
    user=User()
    user.nom = 'ONDONGO'
    user.prenom = 'PrinceDeGloire'
    user.tel = '771592145'
    user.login = 'gloireondongo1205@gmail.com'
    user.password = '1234'
    
# ============save
    
    
    user3 = User(
        nom="Eldy",
        prenom="ODG",
        tel="78555555",
        login="Eldy@yahoo.com",
        password="171295"
    )
    # db.session.add(user3)
    db.session.add_all([user,user3])
    db.session.commit()
    log.warning(f"{user} est bien inséré")
    log.warning(f"{user3} est bien inséré")


#02 ========== select =======
@app.cli.command('select-all-user')
def selectAll_user():
    users=User.query.all()
    print(users)
    
#03 ========== select-where =======
@app.cli.command('selectby-user')
def selectwhere_user():
    userby=User.query.filter(login="gloireondongo1205@gmail.com").all()
    
    print(userby)
    
#03 ========== select-like =======
@app.cli.command('selectlike-user')
def selectLike_user():
    userbyLike=User.query.filter(User.login.like('%g%')).all()
    
    print(userbyLike)
    






        
























