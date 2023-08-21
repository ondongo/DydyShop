import os




APP_NAME = "DydyShop | Online"


NO_PHOTO = "https://t4.ftcdn.net/jpg/04/70/29/97/360_F_470299797_UD0eoVMMSUbHCcNJCdv2t8B2g1GVqYgs.jpg"

# INFO DE BASES DE DONNEES
# SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(basedir, "Expat_Dakar.sqlite")
basedir = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(basedir, "eldy.sqlite")

SECRET_KEY = "WriteHereYourSecretKey"

