import math

from typing import List

from ninja import Router, Schema
from ninja.pagination import paginate, PaginationBase

from django.core.cache import cache
from django.db import models

from .models import Book, CollectdBook
from .schemas import BookOut, PaginatedBooksOut

from services.auth_service import AuthJWT


class PagePagination(PaginationBase):
    class Input(Schema):
        page: int
        page_size: int = 9

    # **kwargs: kwargs that will contain all the arguments that decorated function received
    # (to access pagination input get params["pagination"] - it will be a validated instance of your Input class)
    def paginate_queryset(self, items: models.QuerySet, request, **kwargs):
        pagination_input = kwargs['pagination']

        page = pagination_input.page
        page_size = pagination_input.page_size

        cache_key = f'books_p{page}_s{page_size}'
        ret = cache.get(cache_key)

        if not ret:
            ret = list(items[((page - 1) * page_size):(page * page_size)])
            cache.add(cache_key, ret, 5 * 60)

        return {
            'total_pages': math.ceil(self._get_books_count(items) / page_size),
            'data': ret,
        }

    def _get_books_count(self, query_set: models.QuerySet) -> int:
        cache_key = 'books_total_count'

        ret = cache.get(cache_key)

        if not ret:
            ret = query_set.count()
            cache.add(cache_key, ret, 5 * 60)

        return ret


router = Router()


@router.get("", response=PaginatedBooksOut)
@paginate(PagePagination)
def books(request, **kwargs):
    books = Book.objects.all()

    return books


@router.put("/{book_id}/collect", response={204: None}, auth=AuthJWT())
def collect_book(request, book_id: int):
    collected_book, is_created = CollectdBook.objects.get_or_create(book_id=book_id, user_id=request.auth['user_id'])

    if (not is_created):
        collected_book.is_collected = not collected_book.is_collected
        collected_book.save()

    return 204, None


@router.get('/collected', response=List[BookOut], auth=AuthJWT())
def collected_books(request):
    collected_books_ids = CollectdBook.books. \
        user_collected(request.auth['user_id']). \
        values_list('book_id', flat=True)

    return Book.objects.filter(id__in=collected_books_ids)


@router.get('/collected_ids', response=List[int], auth=AuthJWT())
def collected_books_ids(request):
    return CollectdBook.books.user_collected(request.auth['user_id']).values_list('book_id', flat=True)
