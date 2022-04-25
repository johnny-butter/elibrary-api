from django.db import models


class Cart(models.Model):
    user = models.ForeignKey('users.User', models.CASCADE)
    book = models.ForeignKey('books.Book', models.RESTRICT)
    unit_price = models.DecimalField(decimal_places=2, max_digits=7)
    amount = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = [['user', 'book']]
