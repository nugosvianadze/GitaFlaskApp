from flask import Flask

from app.models.post import Post
from app.models.user import User, Profile, Role
from app.extensions import migrate, bcrypt, faker, db, bootstrap, login_manager
from app.config import Config
from app.routes.user import user_bp
from app.routes.blog import blog_bp


def register_blueprints(app):
    bps = [user_bp, blog_bp]

    for bp in bps:
        app.register_blueprint(bp)


def register_extensions(app):
    migrate.init_app(app)
    bcrypt.init_app(app)
    db.init_app(app)
    bootstrap.init_app(app)
    login_manager.init_app(app)

def create_app() -> Flask:
    app = Flask(__name__)

    app.config.from_object(Config)

    register_extensions(app)
    register_blueprints(app)

    return app
