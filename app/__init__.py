from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_redis import FlaskRedis
from redis import Redis

import logging
import secrets

db = SQLAlchemy()
migrate = Migrate()
redis_client = FlaskRedis()

def create_app():
    app = Flask(__name__)
    
    llave_secreta = secrets.token_urlsafe(24)
    app.config["LLAVE_SECRETA"] = llave_secreta

    if app.config["ENV"] == 'production':
        app.config.from_object("config.ProductionConfig")
        
    elif app.config["ENV"] == 'testing':
        app.config.from_object("config.TestingConfig")
    else:
        app.config.from_object("config.DevelopmentConfig")
        logging.basicConfig(filename='app_development.log', level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s')

    db.init_app(app)
    migrate.init_app(app, db)
    #Hay 3 comandos principales en la terminal para crear y actualizar las db con Flask-Migrate: 
    #1. flask db init (solo al inicio)
    #2. flask db migrate -m "Initial database"
    #3. flask db upgrade
    redis_client.init_app(app)

    from .publico import bp_publico
    app.register_blueprint(bp_publico)

    from .admin import bp_admin
    app.register_blueprint(bp_admin)

    return app