from datetime import datetime
from sqlalchemy.dialects.postgresql import ARRAY
from .db import DB


class Post(DB.Model):
  _tablename_ = 'posts'
  creation_date = DB.Column(DB.DateTime, default=datetime.utcnow)
  id = DB.Column(DB.Integer, autoincrement=True, unique=True, primary_key=True)
  author = DB.Column(DB.String)
  summary = DB.Column(DB.String)
  is_active = DB.Column(DB.Boolean)
  title = DB.Column(DB.String(50))
  body = DB.Column(DB.String)
  slug = DB.Column(DB.String(50))
  uuid = DB.Column(DB.String, unique=True)
  tags = DB.Column(DB.ARRAY(DB.String))

  def __repr__(self):
    return '<Post %r>' % self.title
