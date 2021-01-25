from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import models


class Database:
    def __init__(self, db_url):
        engine = create_engine(db_url)
        models.Base.metadata.create_all(bind=engine)
        self.maker = sessionmaker(bind=engine)

    def get_or_create(self, session, model, unique_key, **data):
        condition = (getattr(model, unique_key) == data[unique_key])
        db_data = session.query(model).filter(condition).first()

        if not db_data:
            db_data = model(**data)
        return db_data

    def create_post(self, data):
        session = self.maker()
        tags = map(
            lambda tag_data: self.get_or_create(session, models.Tag, **tag_data, unique_key="url"), data["tags"]
        )
        author = self.get_or_create(session, models.Author, **data["author"], unique_key="url")
        post = self.get_or_create(session, models.Post, **data["post_data"], author=author, unique_key="url")

        post.tags.extend(tags)

        session.add(post)

        for cmt in data["comments"]:
            writer = self.get_or_create(session, models.Writer, **cmt["writer"], unique_key="id")
            comment = self.get_or_create(session, models.Comment, **cmt["comment"], unique_key="id", post=post,
                                         writer=writer)
            session.add(writer)
            session.add(comment)

        try:
            session.commit()
        except Exception:
            session.rollback()
        finally:
            session.close()
