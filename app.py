from api import app

# from api import front as f


# Lancement
if __name__ == "__main__":
    print("Voici mon app.py")
    # lancer app
    # debug ===>actualise automatique montre les erreurs de maniere clair
    app.run(debug=True, port=3100, host="0.0.0.0")
