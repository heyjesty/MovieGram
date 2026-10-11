from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from backend.models import Movie
from frontend.models import CartItem, Order


class StorefrontTests(TestCase):
    """Catalogue data comes from the seed migration."""

    def setUp(self):
        self.movie = Movie.objects.get(title="Fast X")
        self.user = User.objects.create_user("viewer", "viewer@example.com", "s3cure-pass-123")

    def test_public_pages_render(self):
        urls = [
            reverse("home"),
            reverse("movie_list"),
            reverse("movie_list") + "?q=wick&language=English&sort=-price",
            reverse("category", args=["tv-series"]),
            reverse("movie_detail", args=[self.movie.pk]),
            reverse("login"),
            reverse("register"),
        ]
        for url in urls:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 200)

    def test_missing_pages_return_404(self):
        self.assertEqual(self.client.get(reverse("movie_detail", args=[9999])).status_code, 404)
        self.assertEqual(self.client.get(reverse("category", args=["nope"])).status_code, 404)

    def test_search_filters_results(self):
        response = self.client.get(reverse("movie_list"), {"q": "spider-verse"})
        titles = [m.title for m in response.context["page"].object_list]
        self.assertEqual(titles, ["Spider-Man: Across the Spider-Verse"])

    def test_register_hashes_password_and_logs_in(self):
        response = self.client.post(reverse("register"), {
            "username": "newbie", "email": "newbie@example.com",
            "password1": "Very-strong-pass-42", "password2": "Very-strong-pass-42",
        })
        self.assertRedirects(response, reverse("home"))
        user = User.objects.get(username="newbie")
        self.assertTrue(user.password.startswith("pbkdf2_"))
        self.assertEqual(int(self.client.session["_auth_user_id"]), user.pk)

    def test_duplicate_username_shows_error_instead_of_crashing(self):
        response = self.client.post(reverse("register"), {
            "username": "viewer", "email": "other@example.com",
            "password1": "Very-strong-pass-42", "password2": "Very-strong-pass-42",
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn("username", response.context["form"].errors)

    def test_cart_requires_login(self):
        response = self.client.post(reverse("cart_add", args=[self.movie.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)
        self.assertFalse(CartItem.objects.exists())

    def test_logout_when_signed_out_does_not_crash(self):
        self.assertEqual(self.client.post(reverse("logout")).status_code, 302)

    def test_cart_is_per_user_and_adding_twice_is_safe(self):
        self.client.force_login(self.user)
        self.client.post(reverse("cart_add", args=[self.movie.pk]))
        self.client.post(reverse("cart_add", args=[self.movie.pk]))
        self.assertEqual(self.user.cart_items.count(), 1)

        other = User.objects.create_user("other", password="s3cure-pass-123")
        self.client.force_login(other)
        self.assertEqual(len(self.client.get(reverse("cart")).context["items"]), 0)

    def test_checkout_creates_order_and_clears_cart(self):
        self.client.force_login(self.user)
        self.client.post(reverse("cart_add", args=[self.movie.pk]))
        response = self.client.post(reverse("checkout"), {
            "full_name": "Viewer One", "email": "viewer@example.com",
            "phone": "+91 98765 43210", "address": "Kochi, Kerala",
        })
        self.assertRedirects(response, reverse("orders"))
        order = Order.objects.get(user=self.user)
        self.assertEqual(order.total, self.movie.price)
        self.assertEqual(order.items.get().title, self.movie.title)
        self.assertFalse(self.user.cart_items.exists())

        # A purchased title can't be bought again.
        self.client.post(reverse("cart_add", args=[self.movie.pk]))
        self.assertFalse(self.user.cart_items.exists())

    def test_checkout_with_invalid_phone_shows_error(self):
        self.client.force_login(self.user)
        self.client.post(reverse("cart_add", args=[self.movie.pk]))
        response = self.client.post(reverse("checkout"), {
            "full_name": "Viewer", "email": "viewer@example.com", "phone": "abc", "address": "Kochi",
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn("phone", response.context["form"].errors)
        self.assertFalse(Order.objects.exists())

    def test_users_cannot_remove_other_users_cart_items(self):
        item = CartItem.objects.create(user=self.user, movie=self.movie)
        intruder = User.objects.create_user("intruder", password="s3cure-pass-123")
        self.client.force_login(intruder)
        self.assertEqual(self.client.post(reverse("cart_remove", args=[item.pk])).status_code, 404)
        self.assertTrue(CartItem.objects.filter(pk=item.pk).exists())

    def test_login_ignores_external_next_url(self):
        response = self.client.post(reverse("login"), {
            "username": "viewer", "password": "s3cure-pass-123", "next": "https://evil.example.com/",
        })
        self.assertRedirects(response, reverse("home"))
