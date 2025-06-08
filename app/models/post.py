from sqlalchemy import String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.extensions import db


class Post(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100), nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    image_url: Mapped[str] = mapped_column(default="/test", server_default="/test")

    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'), nullable=True)

    # user = db.relationship('User', back_populates='posts', passive_deletes=True)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "image_url": self.image_url,
            "user_id": self.user_id
        }
