from flask_wtf import FlaskForm

from wtforms import StringField, EmailField, PasswordField, SubmitField

from wtforms.validators import InputRequired, Length, Email, DataRequired, EqualTo


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
    email = EmailField(
        "Email",
        validators=[
            # InputRequired("Le champs est requis!!!"),
            Email(),
        ],
    )
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



class SubscribeForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    submit = SubmitField("Subscribe")


class ArticleForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
