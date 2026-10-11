from django.urls import path

from backend import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("login/", views.dashboard_login, name="dashboard_login"),
    path("titles/add/", views.movie_create, name="movie_create"),
    path("titles/<int:pk>/edit/", views.movie_edit, name="movie_edit"),
    path("titles/<int:pk>/delete/", views.movie_delete, name="movie_delete"),
    path("catalogue/", views.taxonomy, name="taxonomy"),
    path("catalogue/<str:kind>/<int:pk>/delete/", views.taxonomy_delete, name="taxonomy_delete"),
    path("orders/", views.order_list, name="dashboard_orders"),
]
