from flask import Flask
from firebase_admin import credentials, initialize_app


cred = credentials.Certificate("api/key.json")
#default_app = initialize_app(cred)
default_app = initialize_app(cred, {'storageBucket': 'microservice-img-ent-sal.appspot.com'})

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = '12345rtfescdvf'

    from .imgAPI import imgAPI

    app.register_blueprint(imgAPI, url_prefix='/img')
    return app