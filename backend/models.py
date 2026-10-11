from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=60, unique=True, blank=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("category", args=[self.slug])


class Language(models.Model):
    name = models.CharField(max_length=50, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Movie(models.Model):
    title = models.CharField(max_length=120)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="movies")
    language = models.ForeignKey(Language, on_delete=models.PROTECT, related_name="movies")
    price = models.PositiveIntegerField(help_text="Price in rupees")
    description = models.TextField(blank=True)
    thumbnail = models.ImageField(upload_to="Thumb")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "-id"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("movie_detail", args=[self.pk])

