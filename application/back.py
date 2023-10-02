import dbm
from .front import app

from flask import render_template, request, redirect, url_for, flash,session
from application.models.EnumColorAndSize import *
from application.models.EnumCategorie import *
from application.models.SousCategorie import *
from .front import app
from sqlalchemy import desc
from flask_login import login_required
from flask_paginate import Pagination, get_page_parameter
#from flask_oauthlib.client import OAuth
#Hash password
import hashlib
from flask_login import LoginManager,  login_user, logout_user, login_required, current_user
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

from twilio.rest import Client



# =====================================================================
# =============================Import Model===========================
# =====================================================================

from application.models.model import(
    CartItem,
    Item,
    Favorite,
    ajouter_favori,
    findAnnonceById,
    getAllAnnoncePublier,
    getAllAnnonceBrouillon,
    getAllAnnonceDel,
    saveAnnoncePersistance,
    transfer_session_cart_to_db_cart,
    un_delete,
    un_deleteFavorite,
    un_published,
    editAnnonceModel,
    
    User,
    saveUser,

    
)



listcategories=list(EnumCategorie)
#listEtats=list(EnumEtatArticle)



# =====================================================================
# =============================Publier Item Flask + JS===========================
# =====================================================================

@app.route('/admin/add/<categorie>', methods=['GET', 'POST'],defaults={"id_annonce":0,"categorie":None})
@app.route('/admin/add/<categorie>', methods=['GET', 'POST'],defaults={"id_annonce":0})
@login_required
def publierAnnonce(id_annonce, categorie):
    
    
        Item = findAnnonceById(id_annonce)
        sous_categories = []
        recupcategories = categorie
        if request.method == 'GET':
            # ============01
            if categorie == 'hommes':
                sous_categories = SousCategorieHomme.__members__.values()
            # ===========02
            elif categorie == 'femmes':
                sous_categories = SousCategorieFemmme.__members__.values()
          
    
        return render_template("/back/formAdd.html",Item=Item,listcategories=listcategories,sous_categories=sous_categories,recupcategories=recupcategories)






# =====================================================================
# =============================Edit Item===========================
# =====================================================================


@app.route('/admin/edit/<int:id_annonce>', methods=['GET', 'POST'])
@login_required
def editAnnonce(id_annonce):
    Item = Item.query.get(id_annonce)
    return render_template("/back/editArticle.html", Item=Item, listcategories=listcategories)

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
        editAnnonceModel(Item)
    return redirect(url_for("gestionAnnonce"))


#************************************Save ***********************************


@app.route("/save", methods=["POST"])
def save():
    id_annonce = request.form.get("id_annonce")
    title_form = request.form.get("title")
    categorie_form = request.form.get("categorie")
    sous_categorie_form = request.form.get("sous_categorie")
    description_form = request.form.get("description")
    prix_form = request.form.get("prix")
    publish_form = request.form.get("publish")
    img_url_form = request.form.get("img_url")
    img_title_form = request.form.get("img_title")
    # if not publish_form:
    #     publish_form = False
    # else:
    #     publish_form = True

    publish_form = False if not publish_form else True
        # Vérifiez si l'utilisateur a téléchargé des images
    images = request.files.getlist("images")

    # Creer un objet de type Item
    new_annonce = Item(
        id= id_annonce,
        title=title_form,
        description=description_form ,
        prix=prix_form,
        published=publish_form,
        #img_url=img_url_form,
        img_title=img_title_form,
        categorie=categorie_form,
        user_id=current_user.id,
        sousCategorie=sous_categorie_form
        # datePub=datetim
    )
    
    saveAnnoncePersistance(new_annonce, images)
    return redirect(url_for("gestionArticle"))
    


# =====================================================================
# =============================Gerer Item Admin
# -===========================
# =====================================================================  
 
@app.route('/admin/gestion')
@login_required
def gestionArticle():
        annonces =(
        Item.query.filter(Item.published == 1, Item.deleted == 0,Item.user_id==current_user.id).order_by((Item.datePub)).all())
        count_publier=len(annonces)
        return render_template("/back/gesArticle.html",annonces=annonces,listcategories=listcategories,count_publier=count_publier)
 
@app.route('/admin/dashboard')
@login_required
def gestiondash():
        annonces =(
        Item.query.filter(Item.published == 1, Item.deleted == 0,Item.user_id==current_user.id).order_by((Item.datePub)).all())
        count_publier=len(annonces)
        return render_template("/back/dashboard.html",annonces=annonces,listcategories=listcategories,count_publier=count_publier)
 



#************************************ListCorbeille***********************************
@app.route('/admin/listings/Corbeille')
@login_required
def gestionAnnonce_Corbeille():
        annonces =getAllAnnonceDel()
        count_corbeille =len(annonces)
        return render_template("/back/gestionAnnonce.html",annonces=annonces,listcategories=listcategories,count_corbeille=count_corbeille)
    

#************************************Brouillon ***********************************
@app.route('/admin/listings/Brouillon')
@login_required
def gestionAnnonce_Brouillon():
        annonces =getAllAnnonceBrouillon()
        count_brouillon =len(annonces)
        return render_template("/back/gestionAnnonce.html",annonces=annonces,listcategories=listcategories,count_brouillon=count_brouillon)





#************************************Delete ***********************************
@app.route("/admin/Item/<int:id_annonce>/delete")
def un_deleteAnnonce(id_annonce):
    un_delete(id_annonce)
    return redirect(url_for("gestionAnnonce"))


#************************************Publish ***********************************
@app.route("/admin/Item/<int:id_annonce>/publish")
def un_publishAnnonce(id_annonce):
    un_published(id_annonce)
    return redirect(url_for("gestionAnnonce"))

#**********************Recherche Avancee *********************************** 
@app.route('/recherche-annonceAvancee')
def recherche_annonAvancee():
    query = request.args.get('searchAvance')
    annonces=(Item.query.filter( Item.user_id==current_user.id,
                                   Item.title.ilike(f"%{query}%"))
        .order_by(desc(Item.datePub))
        .all())
    count =len(annonces)
    return render_template("/back/gestionAnnonce.html",annonces=annonces,count=count)



# =====================================================================
# =============================Gestion de la connexion===========================
# =====================================================================


#*****************************Creer Compte*********************************** 
@app.route("/compte/creation", methods=["POST","GET"])
def creation_compte():
    if request.method == "POST":
        nom = request.form.get("nom")
        prenom = request.form.get("prenom")
        tel_recup = request.form.get("tel")
        login_recup = request.form.get("login")
        password = request.form.get("pass")
        password_confirmation = request.form.get("PassConfirmation")

        if password != password_confirmation:
            flash("Les mots de passe ne correspondent pas. Veuillez réessayer.", "danger")
            return redirect(url_for("creation_compte"))

        # Hasher le mot de passe dans la base de données
        hashed_password = hashlib.md5(password.encode('utf-8')).hexdigest()

        # Créez un nouvel utilisateur et enregistrez-le dans la base de données
        nouvel_utilisateur = User(nom=nom, prenom=prenom, tel=tel_recup, login=login_recup, password=hashed_password)
        
        test_existance = User.query.filter_by(tel=tel_recup, login=login_recup).first()
        if test_existance:
            flash("Ce login ou tel déjà utilisé. Veuillez en choisir un autre.")
            return redirect(url_for('creation_compte'))
        else:
            saveUser(nouvel_utilisateur)

            flash("Votre compte a été créé avec succès! Veuillez vous connecter.", "success")
            return redirect(url_for("login"))

    
    return render_template("/back/creation_compte.html")



#*****************************Connexion *********************************** 
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))



@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        login = request.form['login']
        password = request.form['pass']
        tel = request.form['tel']
        user = User.query.filter_by(login=login, tel=tel).first()
        
        if user and user.check_password(password):
            login_user(user)
            
            # Check for and transfer session cart to database cart
            if 'panier' in session:
                transfer_session_cart_to_db_cart(user.id, session['panier'])
                session.pop('panier')
                session.pop('total')

            return redirect(url_for('index'))
        else:
            flash('Login ou mot de passe incorrect')
            return render_template('/back/login.html')
    else:
        return render_template("/back/login.html")


#*****************************Connexion avec Google·*********************************** 
''' oauth = OAuth(app)


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



 '''


# Deconnexion
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

# Gestion du panier
@app.route("/add_panier/<int:id>")
def add_panier(id):
    if 'panier' not in session:
        session['panier'] = []
        session['total'] = 0.0
    
    product = Item.query.get(id)
    if product:
        session['panier'].append(id)
        session['total'] += float(product.prix)
    
    return redirect(url_for('index'))


@app.route("/remove_from_cart/<int:id>")
def remove_from_cart(id):
    if 'panier' in session:
        session['panier'].remove(id)
        product = Item.query.get(id)
        if product:
            session['total'] -= float(product.prix)
        return redirect(url_for('cart'))
    return redirect(url_for('index'))

@app.route("/Panier")
def Panier():
    items_in_cart = []
    if 'panier' in session:
        items_in_cart = [Item.query.get(item_id) for item_id in session['panier']]
    
    return render_template("/pages/panier.html", items_in_cart=items_in_cart)



# ===================================================================
# ============================= Gestion des commandes ===============
# =====================================================================
@app.route('/checkout')
def checkout():
    # Obtenez les détails des articles dans le panier à partir de votre base de données
    cart_items = get_cart_items()

    # Créez un message de vérification en convertissant les détails du panier en texte
    checkout_message = create_checkout_message(cart_items)

    # Envoyez le message WhatsApp (utilisez vos propres informations Twilio)
    send_whatsapp_message(checkout_message)

    # Réinitialisez le panier après la commande
    clear_cart()

    flash('Votre commande a été passée avec succès!', 'success')
    return redirect(url_for('index'))

# Fonction pour obtenir les détails des articles dans le panier depuis la base de données
def get_cart_items():
    cart_items = CartItem.query.all()
    cart_item_details = []

    for cart_item in cart_items:
        item = Item.query.get(cart_item.annonce_id)
        if item:
            item_details = {
                'name': item.title,
                'price': item.prix,
                'quantity': cart_item.quantity,
            }
            cart_item_details.append(item_details)

    return cart_item_details

# Fonction pour créer un message de vérification en convertissant les détails du panier en texte
def create_checkout_message(cart_items):
    message = "Votre commande :\n"
    total_price = 0
    for item in cart_items:
        item_name = item['name']
        item_price = item['price']
        item_quantity = item['quantity']
        total_price += item_price * item_quantity
        message += f"{item_name} x{item_quantity}: {item_price * item_quantity}€\n"
    message += f"Total : {total_price}€"
    return message



account_sid = 'ACda1a374fc048affd076363ebd0f1bb5d'
auth_token = '008dda7a6424142308e6c538b44dcdea'
# Fonction pour envoyer un message WhatsApp (utilisez vos propres informations Twilio)
def send_whatsapp_message(message):
    client = Client(account_sid, auth_token)

    message = client.messages.create(

    from_='whatsapp:+14155238886',
    body=message,
    to='whatsapp:+221784603783'
    )

    
    

def clear_cart():
    CartItem.query.delete()
    db.session.commit()



# ===================================================================
# =============================404 Error=========================================
# =====================================================================

@app.errorhandler(404)
def page404(error):
    return render_template("errors/404.html")





# ===================================================================
# =============================Gestion des favoris  =========================================
# =====================================================================

@app.route('/favoris')
@login_required
def articles_favoris():
    user = User.query.get(current_user.id)
    annonces_favoris = user.favorites
    list_favoris = []
    for Item in annonces_favoris:
        list_favoris.append(Item.id)
    # Retrieve the information of the articles in the ids_articles_favoris list
    annonce_favoris_info = Item.query.filter(Item.id.in_(list_favoris)).all()
    count_fav=len(annonce_favoris_info)
    # Render the template with the list of articles in favoris
    return render_template('/back/favori.html', annonces_favoris=annonce_favoris_info,count_fav=count_fav)


#******************Ajouter Favori*********************************** 
@app.route('/ajouter_favoriBack/<int:id_annonce>', methods=['GET','POST'])
@login_required
def ajouter_favoriBack(id_annonce):
    Item = Item.query.get(id_annonce)
    user = User.query.get(current_user.id)
    if Item not in user.favorites:
        favorite = Favorite(annonce_id=Item.id, user_id=current_user.id)
        ajouter_favori(favorite)
        flash("L'Item a été ajoutée à vos favoris avec succès", 'success')
        return redirect(url_for('articles_favoris'))
    else:
        flash('Impossible Deja en favori')


@app.route('/retirer_favoriBack/<int:id_annonce>', methods=['GET','POST'])
@login_required
def retirer_favoriBack(id_annonce):
    return redirect(url_for('articles_favoris'))



#====>Favori G
@app.route('/favorites/delete/<int:favorite_id>', methods=['POST','GET'])
def delete_favorite(favorite_id):
    # Récupérer le favori à supprimer de la base de données
    favorite = Favorite.query.get(favorite_id)
    # Vérifier si le favori existe
    if favorite:
        un_deleteFavorite(favorite)
    # Rediriger vers la page des favoris après la suppression
    return redirect(url_for('articles_favoris'))

