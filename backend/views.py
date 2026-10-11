from functools import wraps

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.db.models import ProtectedError, Q, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from backend.forms import CategoryForm, LanguageForm, MovieForm
from backend.models import Category, Language, Movie
from frontend.models import Order


def staff_required(view):
    return wraps(view)(staff_member_required(view, login_url="dashboard_login"))


def dashboard_login(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect("dashboard")
    form = AuthenticationForm(request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.get_user()
        if user.is_staff:
            login(request, user)
            target = request.GET.get("next")
            if target and url_has_allowed_host_and_scheme(target, {request.get_host()}, request.is_secure()):
                return redirect(target)
            return redirect("dashboard")
        form.add_error(None, "This account does not have access to the dashboard.")
    return render(request, "dashboard/login.html", {"form": form})


@staff_required
def dashboard(request):
    movies = Movie.objects.select_related("category", "language")
    query = request.GET.get("q", "").strip()
    if query:
        movies = movies.filter(Q(title__icontains=query) | Q(category__name__icontains=query))
    stats = {
        "movies": Movie.objects.count(),
        "orders": Order.objects.count(),
        "revenue": Order.objects.aggregate(total=Sum("total"))["total"] or 0,
        "customers": User.objects.filter(is_staff=False).count(),
    }
    return render(request, "dashboard/movies.html", {"movies": movies, "stats": stats, "query": query})


@staff_required
def movie_create(request):
    form = MovieForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        movie = form.save()
        messages.success(request, f"“{movie.title}” was added.")
        return redirect("dashboard")
    return render(request, "dashboard/movie_form.html", {"form": form, "title": "Add title"})


@staff_required
def movie_edit(request, pk):
    movie = get_object_or_404(Movie, pk=pk)
    form = MovieForm(request.POST or None, request.FILES or None, instance=movie)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, f"“{movie.title}” was updated.")
        return redirect("dashboard")
    return render(request, "dashboard/movie_form.html", {"form": form, "movie": movie, "title": "Edit title"})


@staff_required
@require_POST
def movie_delete(request, pk):
    movie = get_object_or_404(Movie, pk=pk)
    movie.delete()
    messages.success(request, f"“{movie.title}” was deleted.")
    return redirect("dashboard")


@staff_required
def taxonomy(request):
    category_form = CategoryForm(prefix="category")
    language_form = LanguageForm(prefix="language")
    if request.method == "POST":
        if "category-name" in request.POST:
            category_form = CategoryForm(request.POST, prefix="category")
            if category_form.is_valid():
                category_form.save()
                messages.success(request, "Category added.")
                return redirect("taxonomy")
        else:
            language_form = LanguageForm(request.POST, prefix="language")
            if language_form.is_valid():
                language_form.save()
                messages.success(request, "Language added.")
                return redirect("taxonomy")
    return render(request, "dashboard/taxonomy.html", {
        "categories": Category.objects.all(),
        "languages": Language.objects.all(),
        "category_form": category_form,
        "language_form": language_form,
    })


@staff_required
@require_POST
def taxonomy_delete(request, kind, pk):
    model = Category if kind == "category" else Language
    obj = get_object_or_404(model, pk=pk)
    try:
        obj.delete()
        messages.success(request, f"“{obj}” was deleted.")
    except ProtectedError:
        messages.error(request, f"“{obj}” is used by existing titles and can't be deleted.")
    return redirect("taxonomy")


@staff_required
def order_list(request):
    orders = Order.objects.select_related("user").prefetch_related("items")
    return render(request, "dashboard/orders.html", {"orders": orders})
