from flask import Flask
from flask_pymongo import PyMongo

app = Flask(__name__)
app.config["MONGODB_SETTINGS"] = {'DB': "WordsData"}
app.config["SECRET_KEY"] = "KeepThisS3cr3t"

db = PyMongo(app)

if __name__ == '__main__':
    app.run()
