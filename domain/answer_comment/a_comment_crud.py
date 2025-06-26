from datetime import datetime

from sqlalchemy.orm import Session

from domain.answer_comment.a_comment_schema import CommentCreate
from models import Answer, User, AnswerComment


def create_comment(db: Session, answer: Answer, comment_create: CommentCreate, user: User):
    db_comment = AnswerComment(answer=answer,
                               content=comment_create.content,
                               create_date=datetime.now(),
                               user=user)
    db.add(db_comment)
    db.commit()


def get_comment(db: Session, comment_id: int):
    return db.query(AnswerComment).get(comment_id)

def delete_comment(db: Session, db_comment: AnswerComment):
    db.delete(db_comment)
    db.commit()
