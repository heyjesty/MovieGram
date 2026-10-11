from django.contrib import admin

from backend.models import Category, Language, Movie


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "slug"]
    prepopulated_fields = {"slug": ["name"]}


@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ["name"]


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ["title", "category", "language", "price", "created_at"]
    list_filter = ["category", "language"]
    search_fields = ["title"]
