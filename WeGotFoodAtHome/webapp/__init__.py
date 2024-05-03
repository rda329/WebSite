from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

db = SQLAlchemy()
DB_NAME = "WeGotFoodAtHome_db"


def create_app():
    app = Flask(__name__, static_url_path='/static')
 
    
    app.config["SECRET_KEY"] = "helloworld"
   
    


    from .views import views
    from .auth import auth


    
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    

    return app

