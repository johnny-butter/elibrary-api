from django.db import models
from django.utils import timezone


class Book(models.Model):
    name = models.CharField(max_length=128)
    image_url = models.URLField(null=True)
    type = models.CharField(blank=True, null=True, max_length=128)
    author = models.CharField(blank=True, null=True, max_length=128)
    publisher = models.CharField(blank=True, null=True, max_length=128)
    published_at = models.DateTimeField(blank=True, null=True)
    price = models.DecimalField(decimal_places=2, max_digits=7)
    stock = models.IntegerField(default=0)
    is_vip_only = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(null=True)

    def __str__(self):
        return self.name


class CollectdBookQuerySet(models.QuerySet):
    def user_collected(self, user_id: int):
        return self.filter(user_id=user_id, is_collected=True)


class CollectdBook(models.Model):
    book = models.ForeignKey('Book', models.CASCADE)
    user = models.ForeignKey('users.User', models.CASCADE)
    is_collected = models.BooleanField(default=True)

    books = CollectdBookQuerySet.as_manager()
