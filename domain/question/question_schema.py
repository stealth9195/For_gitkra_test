import datetime

from pydantic import BaseModel, field_validator

from domain.answer.answer_schema import Answer


class Question(BaseModel):
    id: int
    subject: str
    content: str | None = None # content 항목은 문자열 또는(|) None을 가질 수 있고, 디폴트 값은 None이라는 의미
    create_date: datetime.datetime
    answers: list[Answer] = []

class QuestionCreate(BaseModel):
    subject: str
    content: str

    @field_validator('subject', 'content')
    def not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('빈 값은 허용되지 않습니다.')
        return v

class QuestionList(BaseModel):
    total: int = 0
    question_list: list[Question] = []