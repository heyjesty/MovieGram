import shutil
import tempfile

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from backend.models import Category, Language, Movie

# Smallest valid GIF, used as an uploaded poster.
GIF = (b"GIF89a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xff\xff\xff!\xf9\x04\x01\x00\x00\x00\x00"
       b",\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;")


class DashboardTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.media = tempfile.mkdtemp()
        cls.override = override_settings(MEDIA_ROOT=cls.media)
        cls.override.enable()

    @classmethod
    def tearDownClass(cls):
        cls.override.disable()
        shutil.rmtree(cls.media, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.staff = User.objects.create_user("staff", password="s3cure-pass-123", is_staff=True)
        self.customer = User.objects.create_user("customer", password="s3cure-pass-123")

    def test_dashboard_requires_staff(self):
        for user in (None, self.customer):
            if user:
                self.client.force_login(user)
            response = self.client.get(reverse("dashboard"))
            self.assertEqual(response.status_code, 302)
            self.assertIn(reverse("dashboard_login"), response.url)

    def test_customer_cannot_sign_in_to_dashboard(self):
        response = self.client.post(reverse("dashboard_login"), {"username": "customer", "password": "s3cure-pass-123"})
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_staff_pages_render(self):
        self.client.force_login(self.staff)
        movie = Movie.objects.first()
        for url in [reverse("dashboard"), reverse("movie_create"), reverse("movie_edit", args=[movie.pk]),
                    reverse("taxonomy"), reverse("dashboard_orders")]:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 200)

    def test_create_edit_and_delete_movie(self):
        self.client.force_login(self.staff)
        data = {
            "title": "Test Movie", "category": Category.objects.first().pk,
            "language": Language.objects.first().pk, "price": 199, "description": "",
        }
        response = self.client.post(reverse("movie_create"), {
            **data, "thumbnail": SimpleUploadedFile("poster.gif", GIF, "image/gif"),
        })
        self.assertRedirects(response, reverse("dashboard"))
        movie = Movie.objects.get(title="Test Movie")
        self.assertTrue(movie.thumbnail.name.startswith("Thumb/"))

        # Editing without a new poster keeps the old one; a new poster goes into Thumb/ too.
        self.client.post(reverse("movie_edit", args=[movie.pk]), {**data, "price": 249})
        movie.refresh_from_db()
        self.assertEqual(movie.price, 249)
        self.assertTrue(movie.thumbnail.name.startswith("Thumb/"))

        self.client.post(reverse("movie_edit", args=[movie.pk]), {
            **data, "thumbnail": SimpleUploadedFile("new.gif", GIF, "image/gif"),
        })
        movie.refresh_from_db()
        self.assertTrue(movie.thumbnail.name.startswith("Thumb/new"))

        self.assertEqual(self.client.get(reverse("movie_delete", args=[movie.pk])).status_code, 405)
        self.client.post(reverse("movie_delete", args=[movie.pk]))
        self.assertFalse(Movie.objects.filter(pk=movie.pk).exists())

    def test_category_in_use_cannot_be_deleted(self):
        self.client.force_login(self.staff)
        category = Category.objects.get(name="Movies")
        self.client.post(reverse("taxonomy_delete", args=["category", category.pk]))
        self.assertTrue(Category.objects.filter(pk=category.pk).exists())

    def test_add_category_and_language(self):
        self.client.force_login(self.staff)
        self.client.post(reverse("taxonomy"), {"category-name": "Documentary"})
        self.client.post(reverse("taxonomy"), {"language-name": "Telugu"})
        self.assertTrue(Category.objects.filter(name="Documentary", slug="documentary").exists())
        self.assertTrue(Language.objects.filter(name="Telugu").exists())
