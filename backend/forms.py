from django import forms

from backend.models import Category, Language, Movie


class MovieForm(forms.ModelForm):
    class Meta:
        model = Movie
        fields = ["title", "category", "language", "price", "description", "thumbnail"]
        widgets = {"description": forms.Textarea(attrs={"rows": 4})}
        labels = {"price": "Price (₹)", "thumbnail": "Poster image"}


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name"]
        labels = {"name": "New category"}


class LanguageForm(forms.ModelForm):
    class Meta:
        model = Language
        fields = ["name"]
        labels = {"name": "New language"}
