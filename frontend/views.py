from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from backend.models import Category, Language, Movie
from frontend.forms import CheckoutForm, RegisterForm
from frontend.models import CartItem, OrderItem

HERO_SLIDES = [
    {
        "image": "img/hero/super-mario.jpg",
        "label": "Animation",
        "title": "The Super Mario Bros. Movie",
        "text": "Mario and Luigi are swept into the Mushroom Kingdom in a colourful race to stop Bowser.",
    },
    {
        "image": "img/hero/mavka.jpg",
        "label": "Adventure",
        "title": "Mavka: The Forest Song",
        "text": "A forest spirit must choose between her love for a human and her duty to protect the forest.",
    },
    {
        "image": "img/hero/confidential-informant.jpg",
        "label": "Action",
        "title": "Confidential Informant",
        "text": "Two narcotics detectives cross the line during the hunt for a cop killer.",
    },
]


def _safe_next(request, fallback):
    target = request.POST.get("next") or request.GET.get("next")
    if target and url_has_allowed_host_and_scheme(target, {request.get_host()}, request.is_secure()):
        return target
    return fallback


def _owned_movie_ids(user):
    if not user.is_authenticated:
        return set()
    return set(
        OrderItem.objects.filter(order__user=user, movie__isnull=False).values_list("movie_id", flat=True)
    )


def home(request):
    movies = Movie.objects.select_related("category", "language")
    sections = []
    for category in Category.objects.all():
        items = [m for m in movies if m.category_id == category.id][:10]
        if items:
            sections.append({"category": category, "movies": items})
    return render(request, "store/home.html", {
        "slides": HERO_SLIDES,
        "latest": movies[:10],
        "sections": sections,
    })


def movie_list(request, slug=None):
    movies = Movie.objects.select_related("category", "language")
    category = None
    if slug:
        category = get_object_or_404(Category, slug=slug)
        movies = movies.filter(category=category)

    query = request.GET.get("q", "").strip()
    if query:
        movies = movies.filter(Q(title__icontains=query) | Q(description__icontains=query))

    language = request.GET.get("language", "")
    if language:
        movies = movies.filter(language__name=language)

    sort = request.GET.get("sort", "new")
    movies = movies.order_by({"price": "price", "-price": "-price", "title": "title"}.get(sort, "-created_at"))

    page = Paginator(movies, 24).get_page(request.GET.get("page"))
    if category:
        heading = category.name
    elif query:
        heading = f"Results for “{query}”"
    else:
        heading = "All titles"
    return render(request, "store/movie_list.html", {
        "page": page,
        "category": category,
        "query": query,
        "heading": heading,
        "languages": Language.objects.all(),
        "selected_language": language,
        "sort": sort,
    })


def movie_detail(request, pk):
    movie = get_object_or_404(Movie.objects.select_related("category", "language"), pk=pk)
    in_cart = request.user.is_authenticated and request.user.cart_items.filter(movie=movie).exists()
    related = Movie.objects.filter(category=movie.category).exclude(pk=movie.pk).select_related("category", "language")[:6]
    return render(request, "store/movie_detail.html", {
        "movie": movie,
        "in_cart": in_cart,
        "owned": movie.pk in _owned_movie_ids(request.user),
        "related": related,
    })


@login_required
@require_POST
def cart_add(request, pk):
    movie = get_object_or_404(Movie, pk=pk)
    if movie.pk in _owned_movie_ids(request.user):
        messages.info(request, f"You already own “{movie.title}”.")
    else:
        _, created = CartItem.objects.get_or_create(user=request.user, movie=movie)
        if created:
            messages.success(request, f"“{movie.title}” was added to your cart.")
        else:
            messages.info(request, f"“{movie.title}” is already in your cart.")
    return redirect(_safe_next(request, "cart"))


@login_required
@require_POST
def cart_remove(request, pk):
    item = get_object_or_404(CartItem, pk=pk, user=request.user)
    item.delete()
    messages.success(request, f"“{item.movie.title}” was removed from your cart.")
    return redirect("cart")


@login_required
def cart(request):
    items = request.user.cart_items.select_related("movie", "movie__language", "movie__category")
    total = items.aggregate(total=Sum("movie__price"))["total"] or 0
    return render(request, "store/cart.html", {"items": items, "total": total})


@login_required
def checkout(request):
    items = list(request.user.cart_items.select_related("movie"))
    if not items:
        messages.info(request, "Your cart is empty.")
        return redirect("cart")
    total = sum(item.movie.price for item in items)

    if request.method == "POST":
        form = CheckoutForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                order = form.save(commit=False)
                order.user = request.user
                order.total = total
                order.save()
                OrderItem.objects.bulk_create(
                    OrderItem(order=order, movie=i.movie, title=i.movie.title, price=i.movie.price) for i in items
                )
                request.user.cart_items.all().delete()
            messages.success(request, f"Order {order.reference} confirmed. Enjoy the show!")
            return redirect("orders")
    else:
        form = CheckoutForm(initial={
            "full_name": request.user.get_full_name(),
            "email": request.user.email,
        })
    return render(request, "store/checkout.html", {"form": form, "items": items, "total": total})


@login_required
def orders(request):
    user_orders = request.user.orders.prefetch_related("items", "items__movie")
    return render(request, "store/orders.html", {"orders": user_orders})


def register(request):
    if request.user.is_authenticated:
        return redirect("home")
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome to MovieGram, {user.username}!")
            return redirect(_safe_next(request, "home"))
    else:
        form = RegisterForm()
    return render(request, "store/register.html", {"form": form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect("home")
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            messages.success(request, f"Welcome back, {form.get_user().username}!")
            return redirect(_safe_next(request, "home"))
    else:
        form = AuthenticationForm(request)
    return render(request, "store/login.html", {"form": form})


@require_POST
def logout_view(request):
    logout(request)
    messages.success(request, "You have been signed out.")
    return redirect("home")
