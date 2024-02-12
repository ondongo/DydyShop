from api import app

# from api import front as f

app.config["PREFERRED_URL_SCHEME"] = "https"
# Lancement
if __name__ == "__main__":
    print("Voici mon app.py")
    app.run(debug=False)
