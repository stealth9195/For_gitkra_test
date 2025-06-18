from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status

from database import get_db
from domain.answer_comment import a_comment_schema, a_comment_crud
from domain.answer import answer_crud
from domain.user.user_router import get_current_user
from models import User

router = APIRouter(
    prefix="/api/comment",
)


@router.post("/create/{answer_id}", status_code=status.HTTP_204_NO_CONTENT)
def comment_create(answer_id: int,
                   _comment_create: a_comment_schema.CommentCreate,
                   db: Session = Depends(get_db),
                   current_user: User = Depends(get_current_user)):
    # create comment
    answer = answer_crud.get_answer(db, answer_id=answer_id)
    if not answer:
        raise HTTPException(status_code=404, detail="Answer not found")
    a_comment_crud.create_comment(db, answer=answer,
                                  comment_create=_comment_create,
                                  user=current_user)


@router.get("/detail/{comment_id}", response_model=a_comment_schema.Comment)
def comment_detail(comment_id: int, db: Session = Depends(get_db)):
    comment = a_comment_crud.get_comment(db, comment_id=comment_id)
    return comment
