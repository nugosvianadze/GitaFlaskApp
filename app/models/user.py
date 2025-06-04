from datetime import datetime

from flask_bcrypt import Bcrypt
from sqlalchemy import String, Text, ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from app.extensions import db


user_roles_association_table = db.Table('user_roles',
                                        db.Model.metadata,
                                        db.Column('role_id', db.Integer, ForeignKey('role.id')),
                                        db.Column('user_id', db.Integer, ForeignKey('user.id'))
                                        )


class Role(db.Model):
    __tablename__ = 'role'

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]

    users = db.relationship('User', secondary=user_roles_association_table, back_populates='roles')

    def __repr__(self):
        return self.title


class User(db.Model):
    __tablename__ = 'user'

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(250), nullable=False)
    username: Mapped[str] = mapped_column(String(100))
    address: Mapped[str]
    birth_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=True)

    roles = db.relationship('Role', secondary=user_roles_association_table, back_populates='users')
    posts = db.relationship('Post', backref='user', cascade='all, delete', lazy=True)
    profile = db.relationship('Profile', uselist=False, backref='user', cascade='all, delete')
    # posts = db.relationship('Post', back_populates='user', cascade='all, delete')  # need to def user
    # relation in post model

    # def __repr__(self):
    #     return f'{self.id} - {self.username}'
    # user.profile
    # profile.user

    def authenticate(self, password, bcrypt):
        return bcrypt.check_password_hash(self.password, password)

    @staticmethod
    def hash_password(password, bcrypt: Bcrypt):
        return bcrypt.generate_password_hash(password)


class Profile(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    bio = db.Column(db.Text, nullable=True)

    user_id = db.Column(db.Integer, ForeignKey('user.id'), unique=True)

