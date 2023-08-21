from flask_wtf import FlaskForm

from wtforms import StringField, EmailField, PasswordField

from wtforms.validators import InputRequired, Length, Email

#===============> Je prefere utiliser Mes propres Formulaires 
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
