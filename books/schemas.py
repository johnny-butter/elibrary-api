from typing import List
from ninja import Schema, ModelSchema

from .models import Book


class BookOut(ModelSchema):
    class Config:
        model = Book
        model_exclude = ['created_at', 'updated_at']


class PaginatedBooksOut(Schema):
    total_pages: int
    data: List[BookOut]
