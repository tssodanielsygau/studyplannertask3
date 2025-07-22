from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
from flask_migrate import Migrate
from .models import db  # Import db globally

migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'hjshjhdjah kjshkjdhjs'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'

    db.init_app(app)
    migrate = Migrate(app, db)
    
    from .views import views
    from .auth import auth
    from .models import User, Note  

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    # Register calendar blueprint (optional for modular routing)
    from .calendar_routes import calendar_bp
    app.register_blueprint(calendar_bp, url_prefix='/calendar')

    with app.app_context():
        db.create_all()

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app

def create_database(app):
    if not path.exists('website/' + "db.sqlite"):
        with app.app_context():
            db.create_all()
        print('Created Database!')
