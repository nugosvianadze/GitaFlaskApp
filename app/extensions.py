from faker import Faker
from flask_bcrypt import Bcrypt
from flask_bootstrap import Bootstrap4
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention={
        "ix": 'ix_%(column_0_label)s',
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s"
    })

# session_options={'autocommit': True} for auto commiting
db = SQLAlchemy(model_class=Base)
faker = Faker("ka_GE")
migrate = Migrate()
bcrypt = Bcrypt()
bootstrap = Bootstrap4()
login_manager = LoginManager()
login_manager.login_view = "user.login"
login_manager.login_message = "You are not allowed to do this action! Log in!"