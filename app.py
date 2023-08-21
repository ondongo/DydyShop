from application import app
#from application import front as f
#Lancement
if __name__ == "__main__":
    print("Voici mon app.py")
    # lancer app
    #debug ===>actualise automatique montre les erreurs de maniere clair
    # f.app.run(debug=True, port=3000,host='0.0.0.0')
    app.run(debug=True, port=3000,host='0.0.0.0')
    
    
    
