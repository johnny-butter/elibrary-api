from typing import List

from ninja import Router, Schema
from ninja.pagination import paginate, PaginationBase

from django.core.cache import cache
from .models import Book, CollectdBook
from .schemas import PaginatedBooksOut

from services.auth_service import AuthJWT


class PagePagination(PaginationBase):
    class Input(Schema):
        page: int
        page_size: int = 9

    # **kwargs: kwargs that will contain all the arguments that decorated function received
    # (to access pagination input get params["pagination"] - it will be a validated instance of your Input class)
    def paginate_queryset(self, items, request, **kwargs):
        pagination_input = kwargs['pagination']

        page = pagination_input.page
        page_size = pagination_input.page_size

        cache_key = f'books_p{page}_s{page_size}'

        ret = cache.get(cache_key)

        if not ret:
            ret = list(items[((page - 1) * page_size):(page * page_size)])
            cache.add(cache_key, ret, 5 * 60)

        return {
            'total_pages': 999,
            'data': ret,
        }


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


@router.get("/collected", response=List[int], auth=AuthJWT())
def collected_books(request):
    collected_books = CollectdBook.objects.filter(user_id=request.auth['user_id'], is_collected=True)

    return [collected_book.book_id for collected_book in collected_books]
