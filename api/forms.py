from flask_wtf import FlaskForm

from wtforms import (
    SelectField,
    StringField,
    EmailField,
    PasswordField,
    SubmitField,
    TextAreaField,
)

from wtforms.validators import InputRequired, Length, DataRequired, EqualTo


# ===============> Je prefere utiliser Mes propres Formulaires
class RegisterForm(FlaskForm):
    firstname = StringField(
        "Prénom",
        validators=[
            InputRequired("Le champs est requis!!!"),
            Length(min=3, max=25, message="La taille min est 3 et max est 25"),
        ],
    )
    lastname = StringField(
        "Nom",
        validators=[
            # InputRequired("Le champs est requis!!!"),
            Length(
                min=3,
                max=25,
                message="La taille min est 3 et max est 25",
            ),
        ],
    )
    email = EmailField("Email", validators=[DataRequired()])
    password = PasswordField(
        "Mot de Passe",
        validators=[
            # InputRequired("Le champs est requis!!!"),
            Length(min=6, message="Le mot de passe doit au moins avoit 6 carateres!"),
        ],
    )
    confirmation = PasswordField(
        "Confirmation",
        validators=[
            # InputRequired("Le champs est requis!!!"),
            Length(min=6, message="Le mot de passe doit au moins avoit 6 carateres!"),
        ],
    )


class LoginForm(FlaskForm):
    tel = StringField(
        "Numéro",
        validators=[
            InputRequired("Le champ est requis!!!"),
            Length(
                min=9,
                max=9,
                message="Le numéro doit comporter 9 chiffres, ne mettez pas l'identifiant du pays",
            ),
        ],
    )
    login = StringField("Login", validators=[InputRequired("Le champ est requis!!!")])
    password = PasswordField(
        "Mot de Passe",
        validators=[
            InputRequired("Le champ est requis!!!"),
            Length(min=8, message="Le mot de passe doit avoir au moins 8 caractères!"),
        ],
    )

    submit = SubmitField("Se Connecter")


class CheckoutForm(FlaskForm):
    delivery_address = StringField("Adresse de livraison", validators=[DataRequired()])
    phone_number = StringField("Numéro de téléphone", validators=[DataRequired()])
    country = SelectField(
        "Pays",
        choices=[("Senegal", "Sénégal"), ("Congo", "Congo"), ("France", "France")],
        validators=[DataRequired()],
    )
    email = StringField("Email")
    submit = SubmitField("Valider la commande")


class SubscribeForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    submit = SubmitField("Subscribe")


class ArticleForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])


class MessageForm(FlaskForm):
    article = StringField("Votre article à commander:", validators=[DataRequired()])
    message = TextAreaField("Message:", validators=[DataRequired()])
    submit = SubmitField("Envoyer message sur Whatsapp")


class ProfileForm(FlaskForm):
    nom = StringField("Nom", validators=[DataRequired(), Length(max=200)])
    prenom = StringField("Prénom", validators=[Length(max=200)])
    tel = StringField("Téléphone", validators=[DataRequired()])
    pays = SelectField(
        "Pays",
        choices=[
            ("Sénégal", "Sénégal"),
            ("Congo", "Congo"),
            ("Gabon", "Gabon"),
            ("France", "France"),
        ],
    )
    adresse = StringField("Adresse", validators=[Length(max=200)])
    submit = SubmitField("Modifier")
