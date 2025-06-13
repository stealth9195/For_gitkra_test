import datetime

from pydantic import BaseModel, field_validator

from domain.user.user_schema import User #답변 작성자 이름 표시

class AnswerCreate(BaseModel):
    content: str

    @field_validator('content')
    def not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('빈 값은 허용되지 않습니다.')
        return v

class Answer(BaseModel):
    id: int
    content: str
    create_date: datetime.datetime
    user: User | None
    question_id: int
    modify_date: datetime.datetime | None = None
    voter: list[User] = []

class AnswerList(BaseModel):
    total: int = 0
    answer_list: list[Answer] = []

class AnswerUpdate(AnswerCreate):
    answer_id: int

class AnswerVote(BaseModel):
    answer_id: int


class AnswerDelete(BaseModel):
    answer_id: int