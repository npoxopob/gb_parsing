from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from sqlalchemy import Column, Integer, String, ForeignKey, Table, Text, DateTime

Base = declarative_base()

"""
one to one
one to many - many to one
many to many 
"""

tag_post = Table(
    "tag_post",
    Base.metadata,
    Column('post_id', Integer, ForeignKey('post.id')),
    Column('tag_id', Integer, ForeignKey('tag.id'))
)



class Post(Base):
    __tablename__ = 'post'
    id = Column(Integer, autoincrement=True, primary_key=True)
    url = Column(String, unique=True, nullable=False)
    title = Column(String, unique=False, nullable=False)
    img_url = Column(String, unique=False, nullable=False)
    date_time = Column(DateTime, unique=False, nullable=False)
    author_id = Column(Integer, ForeignKey('author.id'))
    author = relationship("Author")
    tags = relationship('Tag', secondary=tag_post)

class Author(Base):
    __tablename__ = 'author'
    id = Column(Integer, autoincrement=True, primary_key=True)
    url = Column(String, unique=True, nullable=False)
    name = Column(String, unique=False)
    posts = relationship("Post")

class Comment(Base):
    __tablename__ = "comment"
    id = Column(Integer, primary_key=True)
    text = Column(Text, unique=False)
    parent_id = Column(Integer, nullable=True)
    writer_id = Column(Integer, ForeignKey('writer.id'))
    writer = relationship("Writer")
    post_id = Column(Integer, ForeignKey("post.id"))
    post = relationship("Post")

class Writer(Base):
    __tablename__ = "writer"
    id = Column(Integer, autoincrement=True, primary_key=True)
    author_name = Column(String, unique=False)
    comment = relationship("Comment")


class Tag(Base):
    __tablename__ = 'tag'
    id = Column(Integer, autoincrement=True, primary_key=True)
    url = Column(String, unique=True, nullable=False)
    name = Column(String, unique=True, nullable=False)
    posts = relationship("Post", secondary=tag_post)
