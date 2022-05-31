import datetime as dt
import sqlalchemy as sq
import sqlalchemy.orm as _orm
import passlib.hash as hash

import database as db

class UserModel(db.Base):
    __tablename__ = "users"
    id = sq.Column(sq.Integer, primary_key=True, index=True)
    email = sq.Column(sq.String, unique=True, index=True)
    name = sq.Column(sq.String)
    phone = sq.Column(sq.String)
    password_hash = sq.Column(sq.String)
    created_at = sq.Column(sq.DateTime, default=dt.datetime.utcnow())
    posts = _orm.relationship("PostModel", back_populates="user")

    def password_verification(self, password: str):
        return hash.bcrypt.verify(password, self.password_hash)

class PostModel(db.Base):
    __tablename__ = "posts"
    id = sq.Column(sq.Integer, primary_key=True, index=True)
    user_id = sq.Column(sq.Integer, sq.ForeignKey("users.id"))
    post_title = sq.Column(sq.String, index=True)
    post_description = sq.Column(sq.String, index=True)
    post_image = sq.Column(sq.String)
    created_at = sq.Column(sq.DateTime, default=dt.datetime.utcnow())
    user = _orm.relationship("UserModel", back_populates="posts")

