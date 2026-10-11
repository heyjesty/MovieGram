from django.urls import path

from frontend import views

urlpatterns = [
    path("", views.home, name="home"),
    path("browse/", views.movie_list, name="movie_list"),
    path("category/<slug:slug>/", views.movie_list, name="category"),
    path("movie/<int:pk>/", views.movie_detail, name="movie_detail"),
    path("cart/", views.cart, name="cart"),
    path("cart/add/<int:pk>/", views.cart_add, name="cart_add"),
    path("cart/remove/<int:pk>/", views.cart_remove, name="cart_remove"),
    path("checkout/", views.checkout, name="checkout"),
    path("orders/", views.orders, name="orders"),
    path("login/", views.login_view, name="login"),
    path("register/", views.register, name="register"),
    path("logout/", views.logout_view, name="logout"),
]
