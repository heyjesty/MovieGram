from django.contrib.auth.hashers import make_password
from django.db import migrations


def forwards(apps, schema_editor):
    """Move legacy accounts (plaintext passwords) into Django's auth users with hashed passwords."""
    User = apps.get_model("auth", "User")
    Registerdb = apps.get_model("frontend", "Registerdb")
    for account in Registerdb.objects.exclude(Username__isnull=True).exclude(Username=""):
        if User.objects.filter(username__iexact=account.Username).exists():
            continue
        User.objects.create(
            username=account.Username,
            email=account.Email or "",
            password=make_password(account.Password) if account.Password else make_password(None),
        )


class Migration(migrations.Migration):
    dependencies = [
        ("frontend", "0006_store_models"),
        ("auth", "0001_initial"),
    ]

    operations = [migrations.RunPython(forwards, migrations.RunPython.noop)]
