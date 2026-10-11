from django.conf import settings
from django.db import models

from backend.models import Movie


class CartItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="cart_items")
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name="+")
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-added_at"]
        constraints = [models.UniqueConstraint(fields=["user", "movie"], name="unique_cart_movie")]

    def __str__(self):
        return f"{self.user} - {self.movie}"


class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="orders")
    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.CharField(max_length=255)
    total = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.reference

    @property
    def reference(self):
        return f"MG{self.pk:06d}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    movie = models.ForeignKey(Movie, on_delete=models.SET_NULL, null=True, blank=True, related_name="+")
    title = models.CharField(max_length=120)
    price = models.PositiveIntegerField()

    def __str__(self):
        return self.title

